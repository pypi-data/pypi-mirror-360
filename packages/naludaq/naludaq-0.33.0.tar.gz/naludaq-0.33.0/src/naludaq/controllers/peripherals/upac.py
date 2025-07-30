"""Peripherhals controller for UPAC board series

"""
import math
from logging import getLogger

from naludaq.communication import ControlRegisters

from .peripherals_controller import PeripheralsController

logger = getLogger("naludaq.peripherals_upac")


class UpacPeripheralsController(PeripheralsController):
    """Upac specific peripherals controller

    The upac board uses a different system for the peripherals.
    The fpga reads the values off the onboard chips and stores the valus in the register space.
    This changes the readout to use the registers rather than i2c to gather values.

    Registers:
    Power (P1), Current (I1) and Voltage (S1) for PDBIAS rail:
    ltc2992_p1_in
    ltc2992_i1_in
    ltc2992_s1_in

    Temperature Measurement:
    ltc2992_g1_in

    Power (P2), Current (I2), and Voltage (S2) for 1.2v rail:
    ltc2992_p2_in
    ltc2992_i2_in
    ltc2992_s2_in
    """

    def __init__(self, board):
        super().__init__(board)
        self._reader_functions = {
            "temp": self.read_temperature,
            "pdbias_power": self.read_pdbias_power,
            "pdbias_current": self.read_pdbias_current,
            "pdbias_voltage": self.read_pdbias_voltage,
            "1v2_rail_power": self.read_1v2_rail_power,
            "1v2_rail_current": self.read_1v2_rail_current,
            "1v2_rail_voltage": self.read_1v2_rail_voltage,
            "frequencies": self.read_frequencies,
        }

    def read_temperature(self):
        """Read the ambient temperature of the board.

        The voltage for the temperate is bitshifted up 4 bits.
        On this board 1 count is 1 mV making the readout 1:1.
        """
        voltage = self._read_control_register("ltc2992_g1_in") >> 4
        temperature = self._convert_lmt88_voltage_to_temp(voltage / 1000)
        return temperature

    def read_pdbias_power(self):
        """Read the PDBIAS Power from the LTC2992"""

        top = self._read_control_register("ltc2992_p1_in_23_to_16")
        bottom = self._read_control_register("ltc2992_p1_in_15_to_0")

        res = (top << 16) + bottom
        return res

    def read_pdbias_current(self):
        """Read the PDBIAS Current from the LTC2992"""
        return self._read_control_register("ltc2992_i1_in")

    def read_pdbias_voltage(self):
        """Read the PDBIAS Voltage from the LTC2992"""
        # return self._read_control_register('ltc2992_s1_in')
        v_steps = self._read_control_register("ltc2992_s1_in")
        mv = self._voltage_counts_to_mv(v_steps)
        return mv

    def read_1v2_rail_power(self):
        """Read the 1.2V Rail Power from the LTC2992"""

        top = self._read_control_register("ltc2992_p2_in_23_to_16")
        bottom = self._read_control_register("ltc2992_p2_in_15_to_0")
        res = (top << 16) + bottom
        # res = ((top >> 4) << 16) + (bottom >> 4)
        return res

    def read_1v2_rail_current(self):
        """Read the 1.2V Rail Power from the LTC2990"""
        return self._read_control_register("ltc2992_i2_in")

    def read_1v2_rail_voltage(self) -> int:
        """Read the 1.2V Rail Power from the LTC2992

        When operating in 12-bit mode the return is bitshifted up 4-bits and each step is 25mV.
        > LTC2992 Manual p18 section 'ADC Resolution and Conversion Rate'

        Returns:
            readout value in mV.
        """

        v_steps = self._read_control_register("ltc2992_s2_in")
        mv = self._voltage_counts_to_mv(v_steps)
        return mv

    def read_frequencies(self) -> list:
        """Read frquencies for debug purposes.

        Returns: ro_freq, vcdl_freq, mclk_freq
        """

        # RO Monitor clock
        ro_freq = dict.fromkeys(["a", "b", "c", "d"])
        for item in ro_freq.keys():
            msw = self._read_control_register(
                "psec4a_" + item + "_ro_monitor_clock_count_msw"
            )
            lsw = self._read_control_register(
                "psec4a_" + item + "_ro_monitor_clock_count_lsw"
            )
            ro_freq[item] = (msw << 16) + lsw

        # VCDL Monitor clock
        vcdl_freq = dict.fromkeys(["a", "b", "c", "d"])
        for item in vcdl_freq.keys():
            msw = self._read_control_register(
                "psec4a_" + item + "_vcdl_monitor_clock_count_msw"
            )
            lsw = self._read_control_register(
                "psec4a_" + item + "_vcdl_monitor_clock_count_lsw"
            )
            vcdl_freq[item] = (msw << 16) + lsw

        # MCLK Source clock
        mclk_msw = self._read_control_register("psec4a_mclk_source_clock_count_msw")
        mclk_lsw = self._read_control_register("psec4a_mclk_source_clock_count_lsw")
        mclk_freq = (mclk_msw << 16) + mclk_lsw

        return ro_freq, vcdl_freq, mclk_freq

    @staticmethod
    def _voltage_counts_to_mv(v_cnt):
        """Correctly converts the voltage registers to mV from counts.

        When operating in 12-bit mode the return is bitshifted up 4-bits and each step is 25mV.
        > LTC2992 Manual p18 section 'ADC Resolution and Conversion Rate'

        Args:
            v_cnt: coltage in counts

        Returns:
            voltage in mV."""
        step_mv = 25
        bitshift = 4
        mv = (v_cnt >> bitshift) * step_mv
        return mv

    @staticmethod
    def _convert_lmt88_voltage_to_temp(voltage: float) -> int:
        """Converts the return voltage from the LT2990 and LMT88 to temperature in C"""

        temp = -1481.96 + math.sqrt(2.1962e6 + (1.8639 - voltage) / 3.88e-6)
        return temp

    def _read_control_register(self, name: str) -> int:
        """Shorthand to read register value

        Args:
            name: name of the register
        Returns:
            register value
        """
        return ControlRegisters(self.board).read(name)["value"]
