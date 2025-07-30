from collections import defaultdict

from naludaq.board import Board
from naludaq.communication import AnalogRegisters, DigitalRegisters


class UDC16ChannelWriter:
    """Writes values for the analog and digital registers to the given channels
    Makes use of write mask, so not all registers have per channel functionality
    """

    def __init__(self, board: Board):
        self.board = board
        self._num_channels = board.channels
        self._num_chips = board.available_chips
        self._channels_per_chip = self._num_channels // self._num_chips
        self.reset_mask_after_write = True

    def write_analog_register(self, name: str, value: int, channels: list[int] = None):
        """Writes the values to the analog registers for the given channels.

        Args:
            name (str): Name of analog register to write to
            value (int): Value to set the register to
            channels (list[int]): Channels to write to, if not specified,
                defaults to all channels
        """
        if not channels:
            channels = range(self._num_channels)
        self._validate_channel_list_or_raise(channels)
        channel_groups = self._group_channels_by_chips(channels)
        for chip, channels in channel_groups.items():
            self._write_register_chip(AnalogRegisters, name, value, chip, channels)
        if self.reset_mask_after_write:
            self.reset_writemask()

    def reset_writemask(self):
        """Reset the write mask register for all chips.

        The writemask register is restored to 0x1FF (broadcast + all channels),
        regardless of what it was set to before. This is important because
        it ensures the other analog registers don't get written improperly
        elsewhere due to the writemask being wrong.
        """
        DigitalRegisters(self.board).write("writemask_l", 0x1FF)
        DigitalRegisters(self.board).write("writemask_r", 0x1FF)

    def _write_register_chip(
        self,
        registers: AnalogRegisters,
        name: str,
        value: int,
        chip: int,
        channels: list[int],
    ):
        """Writes values to the given register per channels for a chip"""
        self._set_write_mask_for_chip(chip, channels)
        registers(self.board, chip).write(name, value)

    def _set_write_mask_for_chip(self, chip: int, channels: list[int]):
        """Sets the writemask to write to the specified channels of a chip

        Args:
            chip (int): Chip to set write mask
            channels (list[int]): List of channels for the given chip
        """
        wrmsk_l = 0
        wrmsk_r = 0
        for channel in channels:
            wrmsk_l_chan, wrmsk_r_chan = self._get_writemask_from_channel(
                channel % self._channels_per_chip
            )
            wrmsk_l = wrmsk_l | wrmsk_l_chan
            wrmsk_r = wrmsk_r | wrmsk_r_chan

        DigitalRegisters(self.board, chips=chip).write("writemask_l", wrmsk_l)
        DigitalRegisters(self.board, chips=chip).write("writemask_r", wrmsk_r)

    def _get_writemask_from_channel(self, channel: int):
        """
        Returns to the bitmask to be written to writemask digital registers that will enable writing
        to ONLY the channel specified.

        Used to write to 'writemask_l' and 'writemask_r' digital registers.

        Args:
            channel (int): The channel to generate a bitmask for, that will select ONLY that channel.

        Returns:
            hex: Bitmasks (left and right) that is 9 bits long, to set the digital registers to.
        """
        if channel >= 8:
            wrmsk_r = 0x100 | 1 << channel - 8
            wrmsk_l = 0x100
        else:
            wrmsk_r = 0x100
            wrmsk_l = 0x100 | 1 << channel

        return wrmsk_l, wrmsk_r

    def _group_channels_by_chips(self, channels: list) -> dict[int, list[int]]:
        """Groups a list of channels into a dict where the key is the chip,
        the value is a list of channels that correspond to the chip
        ```
        Example::

            {
                0: [0, 4, 12, 15],
                2: [32, 35, 47],
            }
        ```
        """
        groups = defaultdict(lambda: list())
        for channel in channels:
            chip = channel // self._channels_per_chip
            groups[chip].append(channel)
        return groups

    def _validate_channel_list_or_raise(self, channels):
        """Validates a list of channels, and raises an error
        if there's a problem with them.

        Args:
            channels: the object that is supposedly a channels list

        Raises:
            TypeError if the channel list is not a list or
                values are not an int
            ValueError if the values are out of range
        """
        if not isinstance(channels, (list, range)):
            raise TypeError(f"Channels needs to be a list, not a {type(channels)}")
        if len(channels) > self._num_channels:
            raise ValueError(f"Too many channels, max is {self._num_channels}")
        for channel in channels:
            if not isinstance(channel, int):
                raise TypeError(f"Channels can only contain integers")
            if channel >= self._num_channels or channel < 0:
                raise ValueError(f"Channel {channel} is out of bounds")
