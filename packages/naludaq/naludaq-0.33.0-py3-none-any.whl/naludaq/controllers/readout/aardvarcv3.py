"""Readout settings for the aardvarcv3 board.

When setting the readout channel, aardvarc uses exclude channel mask registers
to exclude certain channels from readout

Controls the readout channels and the readout windows.
"""
from logging import getLogger

from .default import ReadoutController

LOGGER = getLogger("naludaq.readout_controller_aardvarcv3")


class Aardvarcv3ReadoutController(ReadoutController):
    def __init__(self, board):
        """Readout Controller for aardvarcv3.
        Args:
            board (Board): the board object.
        """
        super().__init__(board)

    def set_readout_channels(self, channels_to_read: list):
        """Select channels to readout.

        Update the registers and write them to the board.

        Args:
            channels_to_read(list): List of channel numbers to read

        Raises:
            TypeError if the list or an element in the list are the wrong type
            ValueError if the list is too large, too small, or contains a channel
                number that is out of bounds.

        """
        self._validate_channels_or_raise(channels_to_read)
        chansel = self._generate_channels_bits(channels_to_read)
        max_chan = self.board.params["channels"]
        # Exclude channel mask is opposite of chansel
        excludechanmask = (2**max_chan - 1) ^ int(chansel, 2)
        self._write_digital_register("excludechannelmask", excludechanmask)

    def get_readout_channels(self):
        """Get the current channels to read out.

        Returns:
            Sorted list of channel numbers to read out.
        """
        mask_reg = self.board.registers["digital_registers"]["excludechannelmask"]
        mask = mask_reg["value"][0]
        return [c for c in range(self.board.channels) if (mask >> c) & 1 == 0]

    def disable_calibration_channel(self, channels: "int | list[int]" = None):
        """Disable use of the calibration channel for all channels."""
        self._set_cal_mode_or_raise(channels, False, False)

    def enable_external_calibration_channel(self, channels: "int | list[int]"):
        """Enable external calibration for the given channels."""
        self._set_cal_mode_or_raise(channels, True, True)

    def enable_internal_calibration_channel(self, channels: "int | list[int]"):
        """Enable internal calibration for the given channels."""
        self._set_cal_mode_or_raise(channels, True, False)

    def _set_cal_mode_or_raise(
        self,
        channels: "int | list[int] | None",
        enabled: bool,
        external: bool,
    ):
        """Set the calibration mode for each of the given channels.
        Channels not included in the given list will not be modified.

        Args:
            channels (int | list[int] | None): the channel(s) to set the calibration for,
                or `None` for all channels.
            enabled (bool): whether to enable calibration for the given channel(s)
            external (bool): whether to use the external calibration channel for the
                given channels
        """
        if channels is None:
            channels = list(range(self.board.channels))
        if not isinstance(enabled, bool) or not isinstance(external, bool):
            raise TypeError("Enabled and external must be booleans")
        if isinstance(channels, int):
            channels = [channels]
        self._validate_channels_or_raise(channels, min_valid=0)

        channels_per_chip = self.board.channels // self.board.available_chips
        for channel in channels:
            chip = channel // channels_per_chip
            rel_channel = channel % channels_per_chip
            self._write_analog_register(f"cal_en_{rel_channel}", enabled, chips=chip)
            self._write_analog_register(f"cal_ext_{rel_channel}", external, chips=chip)
        for chip in range(self.board.available_chips):
            analog = self.board.registers["analog_registers"]
            global_en = any(
                analog[f"cal_en_{c}"]["value"][chip] for c in range(channels_per_chip)
            )
            self._write_analog_register("cal_en", global_en, chips=chip)
