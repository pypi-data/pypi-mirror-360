import logging
import time

import numpy as np

from naludaq.communication import control_registers, digital_registers
from naludaq.controllers import get_dac_controller
from naludaq.helpers.exceptions import (
    BoardParameterError,
    OperationCanceledError,
    PedestalsDataCaptureError,
)
from naludaq.tools.pedestals import get_pedestals_controller

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name
DigitalRegisters = digital_registers.DigitalRegisters
ControlRegisters = control_registers.ControlRegisters


class DACSweepController:
    """DAC Sweep Controller allows the user to easily collect data for
    a sweep of dac values.

    The DAC Sweep Controller uses portions of the pedestal controller
    to collect data for every sample per channel per dac sweep, allowing
    the user to find the linear region and linear regression values on
    a per sample basis.

    Args:
        board (naludaq.board): Board object

    Attributes:
        num_attempts: How many attempts to try a DAC value before skipping that dac value

    raises:
        BoardParameterError if ext_dac fields are not available amoung the board params.
    """

    def __init__(self, board):
        # The type of daq used depends on the connection type
        self._board = None
        self.board = board
        self._num_attempts = 2
        self._dac_min_counts: int = 0
        self._dac_max_counts: int = self._get_max_counts()
        self._progress: list = []
        self._cancel = False
        self.ped_ctrl = get_pedestals_controller(board)
        self._backup_dac: dict = {}

    def _get_max_counts(self) -> int:
        try:
            return self.board.params["ext_dac"]["max_counts"]
        except KeyError as e:
            raise BoardParameterError(
                f"The register file lacks necessary ext_dac fields: {e}"
            )

    @property
    def dac_max_counts(self):
        """Get/Set the max count value for the DAC.

        The true max value is determined by the board params.

        12-bit: <= 4095
        16-bit: <= 65535

        Raises:
            TypeError: if value is not an int
            ValueError: if value is outside of the boards accepted range.
        """
        return self._dac_max_counts

    @dac_max_counts.setter
    def dac_max_counts(self, value):
        if not isinstance(value, int):
            raise TypeError("dac max counts must be an int.")
        max_val = self._get_max_counts()
        if not self.dac_min_counts <= value <= max_val:
            ValueError(
                f"dac_max_counts must be a value between {self.dac_min_counts} and {max_val}"
            )
        self._dac_max_counts = value

    @property
    def dac_min_counts(self):
        """Get/Set the min count value for the DAC.

        The min count for a board should be 0, unless otherwise stated

        Raises:
            TypeError: if value is not an int
            ValueError: if value is outside of the boards accepted range.
        """
        return self._dac_min_counts

    @dac_min_counts.setter
    def dac_min_counts(self, value):
        if not isinstance(value, int):
            raise TypeError("dac min counts must be an int.")
        min_val = self.board.params["ext_dac"].get("min_counts", 0)
        if not min_val <= value <= self.dac_max_counts:
            ValueError(
                f"dac_min_counts must be a value between {min_val} and {self.dac_max_counts}"
            )
        self._dac_min_counts = value

    @property
    def num_attempts(self):
        return self._num_attempts

    @num_attempts.setter
    def num_attempts(self, value):
        if not isinstance(value, int):
            raise TypeError("num_attempts must be an int.")
        if value < 0:
            raise ValueError("num_attempts must be positive")
        self._num_attempts = value

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board):
        self._board = board

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError("Progress is stored in a list")
        self._progress = value

    def cancel(self):
        """Cancels the dac sweep as soon as possible.
        No data is generated, and the board is restored to
        its previous state.

        Can only be called from a separate thread.
        """
        self._cancel = True
        if self.ped_ctrl:
            self.ped_ctrl.cancel()

    def dac_sweep(
        self,
        step_size: int = 50,
        min_counts: int = 0,
        max_counts: int = None,
        num_captures: int = 3,
        num_warmup_events: int = 1,
        channels: list = None,
    ):
        """Perform a dac sweep with a given step size.
        IMPORTANT: TURN OFF CONNECTED FUNCTION GENERATORS BEFORE RUNNING
        Ext-dac + signal = :(

            Args:
                step_size (int): Step sizes for the ext-dac, from 0 to max_counts
                min_counts (int): minimum DAC value to start sweep from
                max_counts (int): maximum DAC value to stop sweep at
                num_captures (int): number of events per data point
                num_warmup_events (int): number of events to capture before starting the sweep
                channels (list): list of channel numbers to sweep over

            Returns:
                dac_sweep (dict): In form of:
                    dac_val (int): pedestals (dict) {
                        "data", "rawdata"
                    }
                or None if the dac sweep was canceled.
        """
        self._cancel = False

        if step_size <= 0 or step_size > self.dac_max_counts:
            raise ValueError(f"Step size is out of bounds: 0-{self.dac_max_counts}")
        if channels is None:
            channels = list(range(self.board.channels))
        if max_counts is None:
            max_counts = self.board.params["ext_dac"]["max_counts"]

        self._backup_settings()

        output = {}

        ext_dac_values = np.arange(min_counts, max_counts + 1, step_size)
        LOGGER.info(
            f"Starting DAC Sweep from {min_counts}-{max_counts} with step {step_size}"
        )

        for dac_idx, dac_val in enumerate(ext_dac_values):
            dac_val = int(dac_val)
            LOGGER.info(f"Currently running DAC_val: {dac_val}")
            # set dac value for all channels
            self.progress.append(
                (
                    int(98 * (dac_val - min_counts) / (max_counts - min_counts)),
                    f"Collecting DAC value {dac_idx+1}/{len(ext_dac_values)}",
                )
            )
            dac_data = self._run_dac_value(
                dac_val, channels, num_captures, num_warmup_events
            )
            if dac_data:
                output[dac_val] = dac_data
            if self._cancel:
                break

        # Restore backups
        self._restore_settings()

        # Data is probably bad if canceled, so return None
        if self._cancel:
            return None

        # save data
        try:
            self.progress.append((99, "Saving DAC Sweep"))
        except:
            LOGGER.debug("Status message couldn't append to self.progress")
        return output

    def _run_dac_value(self, dac_val, channels, num_captures, num_warmup_events):
        """Run a single dac value for all channels.

        Args:
            dac_val (int): DAC value to set
            channels (list): list of channel numbers to sweep over
            num_captures (int): number of events per data point
            num_warmup_events (int): number of events to capture before starting the sweep

        Returns:
            output (dict): In form of:
                channel (int): {
                    "data": (np.array) pedestal data,
                    "rawdata": (np.array) raw pedestal data
                }
        """
        self._set_dacs(dac_val, channels)
        output = None
        for _ in range(self.num_attempts):
            try:
                output = self._capture_pedestals(num_captures, num_warmup_events)
                LOGGER.info(f"{dac_val} total data: {len(output)}")
                break
            except PedestalsDataCaptureError:
                LOGGER.error("Couldn't capture %d DAC data", dac_val)
                continue
            except (KeyboardInterrupt, OperationCanceledError):
                self.cancel()
                break
        return output

    def _set_dacs(self, dac_val, channels):
        get_dac_controller(self.board).set_dacs(dac_val, channels)
        time.sleep(0.01)

    def _capture_pedestals(self, num_captures: int, num_warmup_events: int):
        """Capture pedestals data for each data point in the DAC sweep.

        This function will behave a bit different if it's a

        Args:
            num_captures (int): number of events per data point
            num_warmup_events (int): number of events to capture before starting the sweep

        Returns:
            pedestals (dict): In form of:
                "data": {
                    channel (int): {
                        "data": (np.array) pedestal data,
                        "rawdata": (np.array) raw pedestal data
                    }
                }
        """
        self.ped_ctrl.reset_pedestals()
        self.ped_ctrl.num_captures = num_captures
        self.ped_ctrl.num_warmup_events = num_warmup_events
        blocks = self.ped_ctrl._capture_data_for_pedestals()
        self.ped_ctrl._store_raw_data(blocks)
        self.ped_ctrl._store_averaged_data()
        return self.board.pedestals

    def _backup_settings(self):
        self._backup_pedestals = self.board.pedestals
        self._backup_dac = (
            self.board.params.get("ext_dac", {}).get("channels", {}).copy()
        )

    def _restore_settings(self):
        self.board.pedestals = self._backup_pedestals
        for chan, value in self._backup_dac.items():
            get_dac_controller(self.board).set_single_dac(chan, value)
