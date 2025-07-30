import time
from contextlib import contextmanager
from typing import Dict

import numpy as np

from naludaq.communication import ControlRegisters
from naludaq.tools.threshold_scan.threshold_scan import ThresholdScan


@contextmanager
def backup_trigger_settings(board):
    """Backup the trigger settings and restore them after the context."""
    tc = board.trigger
    old_trigger_mask = tc.get_channel_trigger_mask()
    tc.set_channel_trigger_mask([c for c in range(board.channels)])
    old_coincidence_trigger = tc.get_coincidence_trigger_enabled()
    coincidence_chips = {c: False for c in range(board.available_chips)}
    tc.set_coincidence_trigger_enabled(coincidence_chips)
    try:
        yield
    finally:
        tc.set_channel_trigger_mask(old_trigger_mask)
        tc.set_coincidence_trigger_enabled(old_coincidence_trigger)


class Upac96ThresholdScan(ThresholdScan):
    """Scan each trigger value and read the scaler values for each channel."""

    def _restore_board_settings(self):
        """Restores the original trigger values from board."""
        # self.trigger_values = self._original_trigger_values
        self.channels = self.chan_bk
        bk_trig = {c: v for c, v in enumerate(self._original_trigger_values)}
        self.board.trigger.write_triggers(bk_trig)

    def _get_scalar_values(self, pause: float) -> np.ndarray:
        """Scan the range and return np.array with trigger amounts.

        Args:
            pause (float): amount of seconds to pause in between samples.

        Returns:
            Triggers value per channel as `np.array`.
        """
        trigger_select_backup = self._get_ctrl_reg("trigger_select")
        self._set_ctrl_reg("trigger_select", 1)
        scan_values = self.scan_values
        output = np.zeros((self.board.channels, len(scan_values)))

        if self.board.using_new_backend is True:
            try:
                bundle_bk = self.board.params["usb"]["bundle_mode"]
                bk_tx_pause = self.board.params["usb"]["tx_pause"]
                self.board.params["usb"]["bundle_mode"] = True
                self.board.params["usb"]["tx_pause"] = 0
            except AttributeError:
                bundle_bk = None
                bk_tx_pause = None
        else:
            try:
                bundle_bk = self.board.connection.bundle_mode
                bk_tx_pause = self.board.connection.tx_pause
                self.board.connection.bundle_mode = True
                self.board.connection.tx_pause = 0
            except AttributeError:
                bundle_bk = None
                bk_tx_pause = None
        with backup_trigger_settings(self.board):
            for i, value in enumerate(scan_values):
                if self._cancel:
                    break
                self._progress.append(
                    (
                        int(95 * i / len(scan_values)),
                        f"Scanning {(i+1)}/{len(scan_values)}",
                    )
                )
                time.sleep(pause)

                scals = self._get_scaler_value(value)

                for chan in self.channels:
                    output[chan][i] = scals[chan]

                self.check_early_stopping(scals)

        self._set_ctrl_reg("trigger_select", trigger_select_backup)

        if bundle_bk is not None and bk_tx_pause is not None:
            if self.board.using_new_backend is True:
                self.board.params["usb"]["bundle_mode"] = bundle_bk
                self.board.params["usb"]["tx_pause"] = bk_tx_pause
            else:
                self.board.connection.bundle_mode = bundle_bk
                self.board.connection.tx_pause = bk_tx_pause

        return output

    def _get_scaler_value(self, trigger_value) -> Dict[int, int]:
        """Read the scalers for selected channels for a specific trigger value.

        Args:
            channels (list): list of channels to scan the scalers

        Returns:
            dict of scaler values for the selected channels
        """
        scalers = {}
        for chan in self.channels:
            self._set_trigger_thresholds(chan, trigger_value)
            scal = self._read_scaler(chan, trigger_value)
            scalers[chan] = scal

        return scalers

    def _read_scaler(self, channel, trigger_value):
        """Read the scaler value for a specific channel and trigger value.

        Args:
            channel (int): channel to read the scaler from
            trigger_value (int): trigger value to scan

        Returns:
            Scaler value for the channel
        """
        self._reset_counter()
        scal = self._get_scalar()
        return scal

    def _get_scalar(self) -> int:
        """Read and combine the scalar values from the two 16-bit registers."""
        upper = self._get_ctrl_reg("count_msb")
        lower = self._get_ctrl_reg("count_lsb")
        scaler = (upper << 16) + lower
        return scaler

    def _get_ctrl_reg(self, name: str):
        return ControlRegisters(self.board).read(name)["value"]

    def _set_ctrl_reg(self, name: str, value: int):
        ControlRegisters(self.board).write(name, value)

    def _reset_counter(self):
        """Reset the counter to 0."""
        self._set_ctrl_reg("count_reset", 1)
        self._set_ctrl_reg("count_reset", 0)
