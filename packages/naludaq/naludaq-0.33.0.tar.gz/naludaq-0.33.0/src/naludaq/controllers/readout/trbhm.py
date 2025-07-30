"""Readout settings for the board.

Controls the readout channels and the readout windows.
"""
from logging import getLogger

from .default import ReadoutController

LOGGER = getLogger("naludaq.readout_controller_default")
MAX_READOUT = 65536


class TrbhmReadoutController(ReadoutController):
    """Special readout controller for the TRHBM.

    Overrides the channel-setting logic.
    """

    def __init__(self, board):
        super().__init__(board)

    def set_readout_channels(self, channels_to_read: list):
        """Select channels to readout.

        TRBHM currently doesn't support setting channels individually
        across both ASICs; their 'chansel' is shared.

        Args:
            channels_to_read(list): List of channel numbers to read
                Accepts channels 1..8 for consistent API, but does
                a logical OR between the upper and lower 4 channels.
        """
        self._validate_channels_or_raise(channels_to_read)

        chansel_lower = sum([1 << x for x in channels_to_read if x < 4])
        chansel_upper = sum([1 << (x - 4) for x in channels_to_read if x >= 4])
        self._write_control_register("chansel", chansel_lower | chansel_upper)

    def get_readout_channels(self) -> "list[int]":
        """Get the enabled readout channels as a list[int]."""
        chansel = self.board.registers["control_registers"]["chansel"]["value"]
        chansel = f"{chansel:02b}"
        return [c for c in range(self.board.channels) if chansel[c % 4] == "1"]
