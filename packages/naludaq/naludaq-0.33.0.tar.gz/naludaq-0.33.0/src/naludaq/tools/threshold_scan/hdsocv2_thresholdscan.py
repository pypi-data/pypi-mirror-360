import logging

from naludaq.communication import DigitalRegisters
from naludaq.controllers import get_readout_controller
from naludaq.tools.threshold_scan.hdsoc_thresholdscan import ThresholdScanHdsoc

import numpy as np
import time

LOGGER = logging.getLogger("naludaq.threshold_scan.hdsocv2_eval")


BROADCAST = 64


class ThresholdScanHdsocv2(ThresholdScanHdsoc):
    """Tool for sweeping over trigger thresholds and counting number of triggers.
    Can be used to determine the ideal point to set the trigger.

    """

    def __init__(
        self,
        board,
        *args,
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
        self._references = {
            "0_15": self.references,
            "16_31": self.references,
            "32_47": self.references,
            "48_63": self.references,
        }

    def _get_scalar_values(self, pause: float = 0.1):
        """Reimplementation to perform some extra setup."""
        get_readout_controller(self.board).set_readout_channels(self.channels)
        tc = self.board.trigger
        tc.references = self._references
        tc.tsel = True
        return self._get_scalar_values_vertical(pause)

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
                self.board.trigger.values = tvalues
                time.sleep(pause)

                scalar = self._get_single_scalar_value(chan)
                output[chan][i] = scalar

        return output

    def _backup_board_settings(self):
        """Back up the trigger values, readout channels, references, and tsel"""
        self._original_trigger_values = self.board.trigger.values.copy()
        rc = get_readout_controller(self.board)
        self._original_readout_channels = rc.get_readout_channels()
        self._original_references = self.board.trigger.references

    def _restore_board_settings(self):
        """Restore the trigger values, readout channels, references, and tsel"""
        self.board.trigger.values = self._original_trigger_values
        self.board.trigger.references = self._original_references

        rc = get_readout_controller(self.board)
        rc.set_readout_channels(self._original_readout_channels)

        dr = DigitalRegisters(self.board)
        dr.write("selectchannel", BROADCAST)

    def _set_tsel_enabled(self, left: bool, right: bool):
        """Set whether tsel is enabled on each side.

        During the threshold scan, tsel must be enabled for scalars
        to read correctly.
        """
        pass
        # self._trigger_controller._set_tsel_enabled()
