import numpy as np

from naludaq.communication import AnalogRegisters
from naludaq.controllers import get_dac_controller
from naludaq.helpers import validations
from naludaq.helpers.exceptions import OperationCanceledError
from naludaq.helpers.operations import CancelableOperation, ProgressReporter
from naludaq.tools import get_data_collector

from .bayesian_optimizer import BayesianOptimizer


class GainStageTuner(ProgressReporter, CancelableOperation):
    def __init__(
        self,
        board,
        isel_bounds: tuple[int, int],
        dac_bounds: tuple[int, int],
        cost_function=None,
    ):
        """Tunes the DAC and ISEL values of the board to center the ADC values around midrange for each channel.

        This tool is intended to be used for finding the ideal DAC and ISEL values in order to center the ADC values
        around midrange (2048 ADC counts on 12-bit ADCs). It uses Bayesian optimization to find the DAC and ISEL values
        that give the best cost values independently for each chip. The cost value is calculated by the cost function,
        which by default calculates the difference from the average to midrange for each channel.
        The DAC and ISEL values are set to the values that gave the best cost values upon completion.

        Care should be taken when selecting the ISEL bounds to search within, as ISEL values outside of a certain range
        can damage certain chips.

        Args:
            board (Board): Board to tune. Needs an open connection
            isel_bounds (tuple[int, int]): Minimum and maximum ISEL values.
            dac_bounds (tuple[int, int]): Minimum and maximum DAC values.
            cost_function (function): Function to calculate the cost for a given set of DAC and ISEL values.
                Defaults to None, which scores the costs values based on the difference from the average to midrange (2048).
                Any function with the signature `fn(acq: list[dict], chip: int) -> float` can be used.
        """
        super().__init__()
        self._board = board
        self._channels_per_chip = self._board.channels // self._board.available_chips
        self._midrange = 2 ** (self._board.params.get("resolution", 12) - 1)

        self._bounds = {}
        self.isel_bounds = isel_bounds
        self.dac_bounds = dac_bounds
        self.cost_function = cost_function or self._calculate_mean_diff

        self.events_per_probe = 10
        self.attempts_per_event = 10
        self.readout_params = {"trig": "ext", "lb": "forced"}
        self.read_window = {
            "windows": 10,
            "lookback": 20,
            "write_after_trig": 254,
        }

    @property
    def board(self):
        """Get the board being tuned."""
        return self._board

    @property
    def cost_function(self):
        """Get/set the function to calculate the cost value for a given set of DAC and ISEL values.

        The function must have the signature `fn(acq: list[dict], chip: int) -> float`.
        """
        return self._cost_function

    @cost_function.setter
    def cost_function(self, fn):
        validations.validate_callable_or_raise(fn)
        self._cost_function = fn

    @property
    def isel_bounds(self) -> tuple[int, int]:
        """Get/set the minimum and maximum ISEL values.

        Care should be taken when selecting the ISEL bounds to search within, as ISEL values outside of a certain range
        can damage certain chips.
        """
        return self._bounds["y"]

    @isel_bounds.setter
    def isel_bounds(self, value: tuple[int, int]):
        validations.validate_positive_int_range_or_raise(value)
        self._bounds["y"] = tuple(value)

    @property
    def dac_bounds(self) -> tuple[int, int]:
        """Get/set the minimum and maximum DAC values."""
        return self._bounds["x"]

    @dac_bounds.setter
    def dac_bounds(self, value: tuple[int, int]):
        validations.validate_positive_int_range_or_raise(value)
        value = tuple(value)
        low, high = value
        max_counts = self.board.params["ext_dac"]["max_counts"]
        min_counts = self.board.params["ext_dac"].get("min_counts", 0)
        if low < min_counts:
            raise ValueError(f"Lower bound must be greater than {min_counts}")
        if high > max_counts:
            raise ValueError(f"Upper bound must be less than {max_counts}")
        self._bounds["x"] = value

    @property
    def events_per_probe(self) -> int:
        """Get/set the number of events to collect per probe.

        In this context "probe" means a single set of DAC and ISEL values.
        """
        return self._events_per_probe

    @events_per_probe.setter
    def events_per_probe(self, value):
        validations.validate_positive_int_or_raise(value)
        self._events_per_probe = value

    @property
    def attempts_per_event(self) -> int:
        """Get/set the number of attempts to collect an event."""
        return self._attempts_per_event

    @attempts_per_event.setter
    def attempts_per_event(self, value):
        validations.validate_positive_int_or_raise(value)
        self._attempts_per_event = value

    @property
    def readout_params(self) -> dict:
        """Get/set the readout parameters."""
        return self._readout_params

    @readout_params.setter
    def readout_params(self, value: dict):
        validations.validate_readout_settings(value)
        self._readout_params = value

    @property
    def read_window(self) -> dict:
        """Get/set the read window parameters."""
        return self._read_window

    @read_window.setter
    def read_window(self, value: dict):
        validations.validate_read_window_dict_or_raise(value)
        self._read_window = value

    def run(self, n_iter=50) -> list[tuple]:
        """Runs the optimization.

        Upon completion, the DAC and ISEL values of the board will be set to the values
        that gave the best cost values.

        Args:
            n_iter (int): Number of iterations to run. Defaults to 50.

        Returns:
            list[tuple]: List of tuples with the DAC and ISEL values for each chip.
                The first element of the tuple is the DAC value, the second is the ISEL value.

        Raises:
            OperationCanceledError: If the operation has been canceled.
            TimeoutError: If data capture timed out.
        """
        optimizers = self._create_optimizers()
        for i in range(n_iter):
            self._raise_if_cancelled()
            self.update_progress(
                (i / n_iter) * 100, f"Running optimization ({i+1}/{n_iter})"
            )
            self._run_iteration_or_raise(optimizers)

        results = [opt.maximum["params"] for opt in optimizers]
        results = self._round_params(results)
        self._apply_suggestions(results)
        return [(res["x"], res["y"]) for res in results]

    def _run_iteration_or_raise(self, optimizers: list[BayesianOptimizer]):
        """Runs a single iteration of the optimization.

        Args:
            optimizers (list[BayesianOptimizer]): List of optimizers to use.
        """
        suggestions = [optimizer.suggest() for optimizer in optimizers]
        suggestions = self._round_params(suggestions)
        self._apply_suggestions(suggestions)
        try:
            data = self._get_data()
        except (OperationCanceledError, TimeoutError):
            raise
        for chip, optimizer in enumerate(optimizers):
            cost = self._cost_function(data, chip)
            optimizer.register(suggestions[chip], cost)

    def _apply_suggestions(self, points: list[dict]):
        """Writes the suggested DAC and ISEL values to the board.

        Args:
            points (list[dict]): List of dictionaries with "x" and "y" keys, where x is the DAC value
                and y is the ISEL value.
        """
        for chip, point in enumerate(points):
            self._set_dac(chip, point["x"])
            self._set_isel(chip, point["y"])

    def _create_optimizers(self):
        """Creates the BayesianOptimizer instances for each chip."""
        return [
            BayesianOptimizer(cost_function=None, bounds=self._bounds)
            for _ in range(self.board.available_chips)
        ]

    def _get_data(self) -> list[dict]:
        """Collects data from the board.

        Uses the readout parameters set in the constructor.

        Returns:
            list[dict]: list of events

        Raises:
            OperationCanceledError: If the operation has been canceled.
            TimeoutError: If the operation timed out.
        """
        collector = get_data_collector(self._board)
        collector.set_window(**self._read_window)
        collector.readout_settings = self._readout_params
        data = (
            collector.iter(
                count=self._events_per_probe,
                attempts=self._attempts_per_event,
            )
            .for_each(lambda _: self._raise_if_cancelled)
            .collect()
        )
        return data

    def _calculate_mean_diff(self, acq: list[dict], chip: int) -> float:
        """Calculates the difference from the acq's average to midrange (2048).
        Calculates the cost value for the channels of the given chip

        Args:
            acq (list[dict]): List of events.
            chip (int): Chip number to calculate the cost value for.

        Returns:
            float: The cost value for the given chip.
        """
        evt_averages = []
        for evt in acq:
            evt_averages.append(
                [np.mean(chandata) for chandata in evt["data"] if len(chandata) != 0]
            )

        chan_averages = np.mean(evt_averages, axis=0)

        # compute cost value
        cpc = self._channels_per_chip
        chan_averages = chan_averages[cpc * chip : cpc * chip + cpc]
        cost_value = 0 - np.sum([np.abs(avg - self._midrange) for avg in chan_averages])

        return cost_value

    def _round_params(self, params: list[dict]) -> dict:
        """Rounds the DAC and ISEL values in the given parameters dictionaries.

        Float values are rounded to the nearest integer.

        Args:
            params (list[dict]): List of dictionaries with "x" and "y" keys, where x is the DAC value
                and y is the ISEL value.

        Returns:
            dict: Dictionary with the rounded DAC and ISEL values.
        """
        return [{k: round(v) for k, v in d.items()} for d in params]

    def _set_isel(self, chip: int, isel: int):
        """Sets the ISEL value for a chip.

        Args:
            chip (int): Chip number to set the ISEL value for.
            isel (int): ISEL value to set.
        """
        AnalogRegisters(self._board, chip).write("isel", isel)

    def _set_dac(self, chip: int, counts: int):
        """Sets the DAC values for a chip.

        Args:
            chip (int): Chip number to set the DAC values for.
            counts (int): DAC value to set.
        """
        start_chan = chip * self._channels_per_chip
        end_chan = start_chan + self._channels_per_chip
        get_dac_controller(self._board).set_dacs(
            counts, list(range(start_chan, end_chan))
        )
