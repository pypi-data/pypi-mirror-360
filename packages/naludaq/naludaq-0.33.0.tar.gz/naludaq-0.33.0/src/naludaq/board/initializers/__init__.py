"""

"""
from abc import ABC, abstractmethod
from typing import List

from naludaq.communication import (
    AnalogRegisters,
    ControlRegisters,
    DigitalRegisters,
    I2CRegisters,
)
from naludaq.helpers.exceptions import InvalidBoardModelError


class Initializers(ABC):
    def __init__(self, board, expected_models: List[str]) -> None:
        """Base class for board initializers.

        Args:
            board (Board): the board to initialize.
            expected_models (List[str]): a list of valid models this
                initializer will work for. This should be determined
                by the subclass.

        Raises:
            InvalidBoardModelError if the board is of an incorrect type.
        """
        if isinstance(expected_models, str):
            expected_models = [expected_models]
        if board.model not in expected_models:
            raise InvalidBoardModelError(
                f'Incorrect initializer used for board "{board.model}"'
            )
        self.board = board
        self.analog_registers = AnalogRegisters(self.board)
        self.control_registers = ControlRegisters(self.board)
        self.digital_registers = DigitalRegisters(self.board)
        self.i2c_registers = I2CRegisters(self.board)

        self.control_write = self.control_registers.write
        self.digital_write = self.digital_registers.write
        self.analog_write = self.analog_registers.write
        self.i2c_write = self.i2c_registers.write

    @abstractmethod
    def run(self) -> bool:
        """Runs the initialization sequence for the board.

        Returns:
            True if successful, False otherwise.
        """
        pass
