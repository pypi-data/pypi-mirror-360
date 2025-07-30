"""Readout settings for the asocv3 board.

When setting the readout channel, asoc uses exclude channel mask registers
to exclude certain channels from readout

Controls the readout channels and the readout windows.
"""
from logging import getLogger

from .default import ReadoutController

LOGGER = getLogger("naludaq.readout_controller_asocv3")


class Asocv3ReadoutController(ReadoutController):
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
