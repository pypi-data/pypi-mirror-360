import logging
import time
from functools import partial

from naludaq.devices import LTC2990
from naludaq.helpers import type_name
from naludaq.helpers.exceptions import BadDataError

from .peripherals_controller import PeripheralsController

logger = logging.getLogger("naludaq.peripherals_hdsoc")


class HdsocPeripheralsController(PeripheralsController):
    def __init__(self, board):
        """HDSoCv1 peripherals controller.

        Provides a way to read various I2C devices on the board.

        Args:
            board (Board): the board object.
        """
        super().__init__(board)
        self._reader_functions = {
            "temp": self.read_temp_of_chip,
            "current": self.read_current_of_chip,
            "fpga_voltage": self.read_fpga_voltage,
            "board_voltage": self.read_board_current,
            "vadjn_left": partial(self.read_vadjn, "left"),
            "vadjn_right": partial(self.read_vadjn, "right"),
            "vadjp_left": partial(self.read_vadjp, "left"),
            "vadjp_right": partial(self.read_vadjp, "right"),
        }

    def read_vadjn(self, side: str) -> float:
        """Reads a VadjN measurement from the board.

        Args:
            side (str): the side of the chip to measure,
                'left' or 'right'

        Returns:
            The measurement in Volts.
        """
        self._validate_side_or_raise(side)

        voltage = self._request_readout(f"vadjn_{side.lower()}")
        logger.debug("VadjN (%s): %s mV", side, voltage)
        return voltage

    def read_vadjp(self, side: str) -> float:
        """Reads a VadjP measurement from the board.

        Args:
            side (str): the side of the chip to measure,
                'left' or 'right'

        Returns:
            The measurement in Volts.
        """
        self._validate_side_or_raise(side)
        voltage = self._request_readout(f"vadjp_{side.lower()}")
        logger.debug("VadjP (%s): %s mV", side, voltage)
        return voltage

    def read_fpga_voltage(self) -> float:
        """Reads the FPGA supply voltage.

        Raises:
            BadDataError if the voltage cannot be read.
        """
        return self._read_ltc2990_voltage("fpga_voltage")

    def read_chip_voltage(self) -> float:
        """Reads the chip voltage in Volts.

        Raises:
            BadDataError if the voltage cannot be read.
        """
        return self._read_ltc2990_voltage("chip_voltage")

    def read_board_voltage(self) -> float:
        """Reads the board supply voltage in Volts.

        Raises:
            BadDataError if the voltage cannot be read.
        """
        return self._read_ltc2990_voltage("board_voltage")

    def read_board_current(self) -> float:
        """Calculates the board current draw in Amps.

        Raises:
            BadDataError if the voltage cannot be read.
        """
        fpga_voltage = self.read_fpga_voltage()
        board_voltage = self.read_board_voltage()
        resistor = self.board.params["peripherals"].get("current_resistor", 5e-3)
        return (fpga_voltage - board_voltage) / resistor

    def _read_ltc2990_voltage(self, param_name: str, num_samples=1):
        """Reads a voltage from the LTC2990.

        Args:
            param_name (str): the name of the param in the board YAML.
            num_samples (int): number of sample points to average.
                Measurements jitter a bunch, so averaging is helpful.

        Returns:
            The voltage in Volts.

        Raises:
            BadDataError if the voltage cannot be read.
            NotImplementedError if the given parameter name is invalid.
        """
        try:
            params = self._get_peripheral_params(param_name)
            addr, chan = params["addr"], params["chan"]
        except (KeyError, NotImplementedError):
            raise NotImplementedError(
                f'Peripheral measurement "{param_name}" is not defined'
            )

        monitor = LTC2990(self._board, addr)

        samples = []
        for _ in range(num_samples):
            monitor.trigger_conversion()  # Important! Conversion needed before reading
            time.sleep(0.01)
            if chan == "vcc":
                try:
                    voltage = monitor.read_vcc()
                except BadDataError:
                    raise
            else:
                try:
                    voltage = monitor.read_voltage(chan)
                except BadDataError:
                    raise

            samples.append(voltage)

        return sum(samples) / len(samples)

    @staticmethod
    def _validate_side_or_raise(side: str):
        """Checks whether a given side value is 'left' or 'right'.
        Not case sensitive.

        Raises:
            TypeError if not a string
            ValueError if not 'left' or 'right'
        """
        if not isinstance(side, str):
            raise TypeError(f'Side must be a str, not "{type_name(side)}"')
        if side.lower() not in ["left", "right"]:
            raise ValueError(f'Side must be "left" or "right", not {side}')
