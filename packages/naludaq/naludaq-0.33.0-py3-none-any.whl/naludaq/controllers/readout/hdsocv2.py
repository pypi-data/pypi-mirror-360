"""

"""
from naludaq.controllers.readout.default import ReadoutController
from naludaq.communication import DigitalRegisters
from naludaq.controllers.board import get_board_controller


class HDSoCv2ReadoutController(ReadoutController):
    def set_readout_channels(self, channels_to_read: list[int]):
        """Select channels to readout.

        Will turn on the chips necessary to read out from the given channels
        (e.g. channels [15, 16, 17] -> chips [0, 1]) and will turn off
        chips that are not being used.

        Args:
            channels_to_read (List[int]): List of channel numbers to read
        """
        self._validate_channels_or_raise(channels_to_read, min_valid=0)
        get_board_controller(self.board).activate_channels = channels_to_read
        self.select_channels(channels_to_read)

    def get_readout_channels(self) -> list:
        """Returns the channels active for readout."""
        return get_board_controller(self.board).active_channels

    def select_channels(self, channels: list[int]):
        """Select channels by masking them.

        Allows individual channel control and also to select channels for readout.

        Args:
            channels: selection to send the following commands to.
        """

        ch_per_group = 8
        for mask_group in range(self.board.params["channels"] // ch_per_group):
            mask_str = f"chanmask{mask_group}"
            ch_range = list(
                range(mask_group * ch_per_group, (mask_group + 1) * ch_per_group)
            )[::-1]
            bin_list = [str(int(channel not in channels)) for channel in ch_range]
            val = int("".join(bin_list), 2)

            DigitalRegisters(self.board).write(mask_str, val)

    def _compute_write_after_trig(self, write_after_trig):
        """On HDSoC write after trigger is equal to windows"""
        return write_after_trig
