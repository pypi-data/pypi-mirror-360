import logging
from functools import partial

from naludaq.helpers import type_name

from .peripherals_controller import PeripheralsController

logger = logging.getLogger("naludaq.peripherals_hdsoc")


class AodsocPeripheralsController(PeripheralsController):
    def __init__(self, board):
        """AODSOC peripherals controller.

        Provides a way to read various I2C devices on the board.

        Args:
            board (Board): the board object.
        """
        super().__init__(board)
        self._reader_functions = {
            "current": self.read_current_of_chip,
            "vadjn0": partial(self.read_vadjn, 0),
            "vadjn1": partial(self.read_vadjn, 1),
            "chip_voltage": self.read_chip_voltage,
            "ldo_voltage": self.read_ldo_voltage,
        }

    def read_vadjn(self, chip: int) -> float:
        """Reads a VadjN measurement from the board.

        Args:
            chip (int): chip number, must be 0 or 1

        Returns:
            The measurement in Volts.
        """
        self._validate_chip_or_raise(chip)
        voltage = self._read_ltc2990_voltage(f"vadjn_{chip}")
        logger.debug("VadjN (%s): %s V", chip, voltage)
        return voltage

    def read_vadjp(self, chip: int = 0) -> float:
        """Get the vadjp value. It's not hooked up to the voltage monitor."""
        return 0

    def read_chip_voltage(self) -> float:
        voltage = self._read_ltc2990_voltage("chip_voltage")
        logger.debug("Chip voltage: %s V", voltage)
        return voltage

    def read_ldo_voltage(self) -> float:
        voltage = self._read_ltc2990_voltage("ldo_voltage")
        logger.debug("Chip voltage: %s V", voltage)
        return voltage

    def read_current_of_chip(self) -> float:
        v_ldo = self.read_ldo_voltage()
        v_chip = self.read_chip_voltage()
        return self._convert_voltage_to_current(v_ldo - v_chip)

    @staticmethod
    def _validate_chip_or_raise(chip: int):
        """Checks whether a given chip number is 0 or 1.

        Raises:
            TypeError: if chip is not an int
            ValueError: if chip is not valid
        """
        if not isinstance(chip, int):
            raise TypeError(f'Chip must be an int, not "{type_name(chip)}"')
        if chip not in [0, 1]:
            raise ValueError(f"Chip must be 0 or 1, not {chip}")
