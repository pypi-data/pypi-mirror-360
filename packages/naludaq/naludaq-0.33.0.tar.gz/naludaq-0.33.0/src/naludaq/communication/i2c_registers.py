import logging

from naludaq.communication import _fpga
from naludaq.helpers.exceptions import I2CError, InvalidBoardModelError
from naludaq.helpers.semiton import SemitonABC

logger = logging.getLogger("naludaq.i2c_registers")


class I2CRegisters(_fpga.FpgaRegisters, SemitonABC):
    def __init__(self, board):
        """Communication with I2C devices through FPGA registers.

        Args:
            board (Board): the board object.
        """
        if "i2c_registers" not in board.registers:
            raise InvalidBoardModelError(
                f'Board "{board.model}" is missing I2C registers or does not support I2C'
            )
        super().__init__(board, "i2c_registers")

        # These are the same on all valid boards
        self._i2c_transmit_command = board.params.get("i2c", {}).get(
            "transmit_command", "CA000000"
        )

    def transmit_command(self):
        """Send the command which tells the board to transmit data over the I2C bus.

        Raises:
            I2CError: if the command fails to send.
        """
        try:
            self._send_command(self._i2c_transmit_command)
        except Exception as e:
            raise I2CError("Failed to initiate I2C send") from e
