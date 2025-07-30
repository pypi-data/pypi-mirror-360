"""

"""
import logging
import time

import numpy as np

from naludaq.communication.analog_registers import AnalogRegisters
from naludaq.controllers import get_readout_controller
from naludaq.helpers import type_name
from naludaq.tools.threshold_scan.threshold_scan import ThresholdScan

LOGGER = logging.getLogger("naludaq.threshold_scan")


class ThresholdScanHdsoc(ThresholdScan):
    """Tool for sweeping over trigger thresholds and counting number of triggers.
    Can be used to determine the ideal point to set the trigger.

    """

    def __init__(
        self,
        board,
        *args,
        low_ref_value: int = None,
        high_ref_value: int = None,
        **kwargs,
    ):
        """Threshold scan for hdsoc boards.

        Args:
            board (Board): board object
            start_value (int): the start value for the scan
            stop_value (int): the stop value for the scan
            step_size (int): the step size for the scan
            low_ref_value (int): low reference value
            high_ref_value (int): high reference value
        """
        super().__init__(board, *args, **kwargs)
        self.low_reference = low_ref_value
        self.high_reference = high_ref_value

    @property
    def _max_reference(self) -> int:
        """Get the maximum number of references allowed"""
        return self.board.trigger.params.get("max_ref", 15)

    @property
    def _min_reference(self) -> int:
        """Get the minimum reference value allowed"""
        return self.board.trigger.params.get("min_ref", 0)

    @property
    def low_reference(self) -> int:
        """Get/set the low trigger reference value used during the scan"""
        return self._low_ref_value

    @low_reference.setter
    def low_reference(self, value: int):
        if value is None:
            value = self.board.params.get("threshold_scan", {}).get("low_ref", 0)
        if not isinstance(value, int):
            raise TypeError(f"Value must be int, not {type_name(value)}")
        if not self._min_reference <= value <= self._max_reference:
            raise ValueError(
                f"Value {value} is out of bounds for range "
                f"{self._min_reference} - {self._max_reference}"
            )
        self._low_ref_value = value

    @property
    def references(self) -> tuple[int, int]:
        """Get/Set the references (low, high) used during the scan"""
        return (self.low_reference, self.high_reference)

    @references.setter
    def references(self, values: tuple[int, int]):
        self.low_reference, self.high_reference = values

    @property
    def high_reference(self) -> int:
        """Get/set the high trigger reference value used during the scan"""
        return self._high_ref_value

    @high_reference.setter
    def high_reference(self, value: int):
        if value is None:
            value = self.board.params.get("threshold_scan", {}).get("high_ref", 0)
        if not isinstance(value, int):
            raise TypeError(f"Value must be int, not {type_name(value)}")
        if not self._min_reference <= value <= self._max_reference:
            raise ValueError(
                f"Value {value} is out of bounds for range "
                f"{self._min_reference} - {self._max_reference}"
            )
        self._high_ref_value = value

    def run(self, pause: float = 0.1):
        """Reimplementation to perform extra validation"""
        self._validate_scan_settings_or_raise()
        return super().run(pause)

    def _get_scalar_values(self, pause: float = 0.1):
        """Reimplementation to perform some extra setup."""
        rc = get_readout_controller(self.board)
        rc.set_readout_channels(self.channels)
        tc = self.board.trigger
        tc.tsel = {
            "0_15": True,
            "16_31": True,
        }
        tc.references = {
            "0_15": self.references,
            "16_31": self.references,
        }
        return self._get_scalar_values_vertical(pause)

    def _backup_board_settings(self):
        """Back up the trigger values, readout channels, references, and tsel"""
        super()._backup_board_settings()
        rc = get_readout_controller(self.board)
        tc = self.board.trigger
        self._original_readout_channels = rc.get_readout_channels()
        self._original_references = tc.references
        self._original_tsel = tc.tsel

    def _restore_board_settings(self):
        """Restore the trigger values, readout channels, references, and tsel"""
        super()._restore_board_settings()
        rc = get_readout_controller(self.board)
        rc.set_readout_channels(self._original_readout_channels)
        tc = self.board.trigger
        tc.references = self._original_references
        tc.tsel = self._original_tsel

    def _set_tsel_enabled(self, left: bool, right: bool):
        """Set whether tsel is enabled on each side.

        During the threshold scan, tsel must be enabled for scalars
        to read correctly.
        """
        AnalogRegisters(self.board).write("tsel_left", left)
        AnalogRegisters(self.board).write("tsel_right", right)

    def _get_analog_register(self, register: str) -> int:
        """Get the value of an analog register"""
        return self.board.registers["analog_registers"][register]["value"][0]

    def _validate_scan_settings_or_raise(self):
        """Raise an error if scan settings don't make sense"""
        if self.low_reference >= self.high_reference:
            raise ValueError("Low reference cannot exceed the high reference")

    def _get_scalar_values_vertical(self, pause: float) -> np.ndarray:
        """Scan the range and return np.array with trigger amounts

        Args:
            pause (float): amount of seconds to pause in between samples.

        Returns:
            Triggers value per channel as `np.array`.
        """
        scan_values = self.scan_values
        output = np.zeros((self.board.channels, len(scan_values)))

        # NOTE: the default threshold scan iterates over scan values then channels,
        # but on HDSoC it is super important that this order is reversed!
        # Otherwise the threshold scan will be super messed up or not work at all.
        for ch_i, chan in enumerate(self.channels):
            for i, value in enumerate(scan_values):
                if self._cancel:
                    break
                progress = ch_i * len(scan_values) + i + 1
                progress_total = len(self.channels) * len(scan_values)
                LOGGER.debug("Scan progress: %s/%s", progress, progress_total)
                self._progress.append(
                    (
                        int(95 * progress / progress_total),
                        f"Scanning {progress}/{progress_total}",
                    )
                )
                default_tval = self.board.trigger.params.get("default_trigger_value", 0)
                tvalues = {ch: default_tval for ch in range(self.board.channels)}
                tvalues[chan] = int(value)
                self.board.trigger.values = tvalues  # int(value)
                time.sleep(pause)

                scalar = self._get_single_scalar_value(chan)
                output[chan][i] = scalar

        return output

    def _get_single_scalar_value(self, channel) -> list[int]:
        """Gets a reading from all scalers on the board.

        Returns:
            list[int]: scalar values ordered by channel.
        """
        return self._board_controller.read_scalar(channel)
