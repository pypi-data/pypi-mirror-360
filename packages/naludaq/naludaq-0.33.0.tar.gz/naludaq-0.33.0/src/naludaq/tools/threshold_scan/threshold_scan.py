import logging
import time
from collections import defaultdict
from typing import Dict, Iterable

import numpy as np

from naludaq.controllers.board import get_board_controller
from naludaq.helpers import type_name

LOGGER = logging.getLogger("naludaq.threshold_scan")
NUM_NO_TRIGGERS = 5


class ThresholdScan:
    """Tool for sweeping over trigger thresholds and counting number of triggers.
    Can be used to determine the ideal point to set the trigger.
    """

    def __init__(
        self,
        board,
        channels: Iterable[int] = None,
        scan_values: Iterable[int] = None,
    ):
        """Class to run ThresholdScan. Used to find the number of
        triggers for each trigger threshold.

        Args:
            board (Board): Board to run a threshold scan on
            threshold_values (Iterable[int]): threshold values to run the scan for.
        """
        self.board = board
        self.channels = channels
        self._cancel = False
        self._progress: list = []
        self._num_trig_chans = board.channels
        self.scan_values = scan_values
        self._counters = defaultdict(int)

        self._board_controller = get_board_controller(self.board)

    @property
    def channels(self) -> list[int]:
        """Get/set the channels to run the scan on."""
        return self._channels.copy()

    @channels.setter
    def channels(self, channels: Iterable[int]):
        if channels is None:
            channels = range(self.board.channels)
        if not isinstance(channels, Iterable):
            raise TypeError(
                f"Channels must be a Iterable[int], not {type_name(channels)}"
            )
        if any(not isinstance(c, int) for c in channels):
            raise TypeError("Channels must be a Iterable[int]")
        if any(not 0 <= c < self.board.channels for c in channels):
            raise ValueError("One or more channels is out of bounds")
        self._channels = list(channels)

    @property
    def scan_values(self) -> np.ndarray:
        """Gets/sets the threshold values to read the scalars for."""
        return self._threshold_values.copy()

    @scan_values.setter
    def scan_values(self, values: Iterable[int]):
        if values is None:
            values = self._default_scan_values()
        if not isinstance(values, Iterable):
            raise TypeError(f"Values must be a Iterable[int], not {type_name(values)}")
        values = np.array(values)
        if (
            np.min(values) < self.board.trigger._min_thresholds
            or np.max(values) > self.board.trigger._max_thresholds
        ):
            raise ValueError("One or more values is out of bounds")
        self._threshold_values = values

    def run(self, pause: float = 0.1):
        """Scan the scalars at the trigger values defined by the scan_values property.

        Returns the amount of hits for each scanned trigger value in the range.

        Args:
            pause (float): amount of seconds to pause in between samples.

        Returns:
            Tuple of (trigger value per channel as `np.array`, `irange` as list).
        """
        self._cancel = False
        self._progress.append((0, "Backing up board settings"))
        self._backup_board_settings()
        output = self._get_scalar_values(pause)
        self._progress.append((95, "Restoring board settings"))
        self._restore_board_settings()
        self._progress.append((100, "Done"))

        return (np.array(output), self.scan_values.copy())

    def _backup_board_settings(self):
        """Saves a copy of board trigger values to be restored later."""
        self._original_trigger_values = self.board.trigger.values.copy()
        self.chan_bk = self.channels.copy()

    def _restore_board_settings(self):
        """Restores the original trigger values from board."""
        self.board.trigger.values = self._original_trigger_values
        self.board.trigger.write_triggers()
        self.channels = self.chan_bk

    def _get_scalar_values(self, pause: float) -> np.ndarray:
        """Scan the range and return np.array with trigger amounts

        Args:
            pause (float): amount of seconds to pause in between samples.

        Returns:
            Triggers value per channel as `np.array`.
        """
        scan_values = self.scan_values
        self._counters = defaultdict(int)

        output = np.zeros((self.board.channels, len(scan_values)))
        for i, value in enumerate(scan_values):
            if self._cancel:
                break
            LOGGER.debug("Scan progress: %s/%s", i + 1, len(scan_values))
            self._progress.append(
                (int(95 * i / len(scan_values)), f"Scanning {(i+1)}/{len(scan_values)}")
            )
            time.sleep(pause)

            scals = self._get_scaler_value(value)

            for chan in self.channels:
                output[chan][i] = scals[chan]

            self.check_early_stopping(scals)
        return output

    def cancel(self):
        """Cancels the threshold scan if one is currently running.

        This function must be called from a different thread, as the
        threshold scan is blocking. The threshold scan will stop as
        soon as possible.
        """
        self._cancel = True

    def _set_trigger_thresholds(self, channel: int, trigger_value: int):
        trigger_vals = {ch: 0 for ch in range(self.board.channels)}
        trigger_vals[channel] = int(trigger_value)
        self.board.trigger.values = trigger_vals

    def _get_scaler_value(self, trigger_value: list[int]) -> Dict[int, int]:
        """Read the scalers for selected channels for a specific trigger value.

        Args:
            channels (list): list of channels to scan the scalers

        Returns:
            dict of scaler values for the selected channels
        """
        scalers = {}
        for chan in self.channels:
            self._set_trigger_thresholds(chan, trigger_value)
            scal = self._board_controller.read_scalar(chan)
            scalers[chan] = scal

        return scalers

    @property
    def progress(self):
        """Get/Set the progress message queue.

        This is a hook to read the progress if running threads.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    def _default_scan_values(self) -> np.ndarray:
        """Get the default scan values from the params"""
        scan_params = self.board.params.get("threshold_scan", {})
        return np.arange(
            scan_params.get("start", 500),
            scan_params.get("stop", 3500),
            scan_params.get("stepsize", 5),
        )

    def check_early_stopping(self, scals: dict[int, int]):
        """Check if the scan should be stopped early.

        Stops the scan to a channel if there has been a a trigger.
        If there are no channels left to scan a cancel is set.

        Args:
            scals (Dict[int, int]): Scaler values for each channel.
        """
        for i, val in scals.items():
            if val > 0:
                self._counters[i] = NUM_NO_TRIGGERS
            if self._counters[i] > 0:
                self._counters[i] -= 1
                if self._counters[i] == 0:
                    channels = self.channels
                    channels.remove(i)
                    self.channels = channels
                    if len(self.channels) == 0:
                        self._cancel = True
