import logging

from .peripherals_controller import PeripheralsController

logger = logging.getLogger("naludaq.peripherals_aardvarcv3")


class Aardvarcv3PeripheralsController(PeripheralsController):
    def __init__(self, board):
        """Aardvarcv3 peripherals controller.

        Provides a way to read various I2C devices on the board.

        Args:
            board (Board): the board object.
        """
        super().__init__(board)
        self._reader_functions = {
            "temp": self.read_temp_of_chip,
            "current_1v2": self.read_1v2_current_of_chip,
            "current_2v5": self.read_2v5_current_of_chip,
            "vadjn": self.read_vadjn,
            "vadjp": self.read_vadjp,
        }

    def read_1v2_current_of_chip(self):
        """Reads out the MCP3426 monitoring the current and converts to Ampere.

        Reads out the MCP3426 monitoring the current sense resistor, and converts
        it to a current in A.

        Returns:
            Current in Ampere.

        Raises:
            NotImplementedError if this functionality is not available for the current model.
        """
        rail = "current_1v2"

        return self._read_rail_current_of_chip(rail)

    def read_2v5_current_of_chip(self):
        """Reads out the MCP3426 monitoring the current and converts to Ampere.

        Reads out the MCP3426 monitoring the current sense resistor, and converts
        it to a current in A.

        Returns:
            Current in Ampere.

        Raises:
            NotImplementedError if this functionality is not available for the current model.
        """
        rail = "current_2v5"

        return self._read_rail_current_of_chip(rail)

    def _read_rail_current_of_chip(self, rail):
        voltage_mv = self._request_readout(rail)
        resistance_mo = self._get_v2a_resistance(rail)
        current_ma = self._convert_voltage_to_current(voltage_mv, resistance_mo=resistance_mo)
        logger.debug("Current Sense: %smA / %smV", current_ma, voltage_mv)
        return current_ma

    def _get_v2a_resistance(self, rail):
        """Return voltage to current resistor in mOhm."""
        try:
            return self.board.params["peripherals"][rail]["r_sense"] * 1000  # mOhm
        except KeyError:
            raise NotImplementedError(
                f"{rail} readout functionality has not been implemented for {self.board.model}"
            )

    def _convert_voltage_to_current(self, voltage_mv, resistance_mo):
        """Convert voltage to current by checking voltage drop over resistor."""
        current_ma = voltage_mv / resistance_mo
        return current_ma
