import logging

from naludaq.communication import DigitalRegisters

from .default import BoardController

LOGGER = logging.getLogger("naludaq.board_controller_aodsoc")


class BoardControllerAodsoc(BoardController):
    """Board controller for AODSOC boards.

    Has a special version of the `read_scalers` function to handle reading from chips
    individually.
    """

    def read_scalar(self, channel: int) -> int:
        """Read the scalar for the given channel"""
        channels_per_chip = self.board.channels // self.board.available_chips
        relative_channel = channel % channels_per_chip
        chip = channel // channels_per_chip
        return self._read_scalar_inner(chip, relative_channel)

    def _read_scalar_inner(self, chip: int, relative_channel: int) -> int:
        """Read the scalar for the given channel.

        This is the inner function that actually reads the scalar.
        It is called by `read_scalar` and should not be called directly.
        """
        name = self.get_scal_name(relative_channel)
        scal = self._read_digital_register(name, chips=chip)
        try:
            scalhigh = self._read_digital_register("scalhigh", chips=chip)
        except (KeyError, AttributeError):
            scalhigh = 0
        shift_amt = DigitalRegisters(self.board).registers[name]["bitwidth"]
        scal += scalhigh << shift_amt

        return scal
