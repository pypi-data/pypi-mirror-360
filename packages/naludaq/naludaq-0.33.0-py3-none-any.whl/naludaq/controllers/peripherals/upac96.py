import logging

from naludaq.controllers.peripherals.peripherals_controller import PeripheralsController

logger = logging.getLogger("naludaq.peripherals.upac96")


class PeripheralsControllerUpac96(PeripheralsController):
    def __init__(self, board):
        """Peripherals controller for the UPAC96

        Contains a few functions to read from the two LTC2990 chips on the power regulator board.
        - read_udc1_1v2
        - read_udc1_2v5
        - read_udc2_1v2
        - read_udc2_2v5
        - read_fpga_1v0
        - read_fpga_1v8
        - read_fpga_io_2v5
        - read_fpga_io_3v3

        For reading temperatures:
        - read_readout_pcb_temperature
        - read_power_pcb_temperature
        """
        super().__init__(board)
        self._reader_functions = {
            "readout_pcb_temp": self.read_readout_pcb_temperature,
            "power_pcb_temp": self.read_power_pcb_temperature,
            "udc1_1v2": self.read_udc1_1v2,
            "udc1_2v5": self.read_udc1_2v5,
            "udc2_1v2": self.read_udc2_1v2,
            "udc2_2v5": self.read_udc2_2v5,
            "fpga_1v0": self.read_fpga_1v0,
            "fpga_1v8": self.read_fpga_1v8,
            "fpga_io_2v5": self.read_fpga_io_2v5,
            "fpga_io_3v3": self.read_fpga_io_3v3,
        }

    def read_readout_pcb_temperature(self):
        """Read the readout PCB temperature"""
        addr = (
            self.board.params["peripherals"]
            .get("readout_pcb_temp", {})
            .get("addr", 0b0011_000)
        )
        temp = self._read_temperature(addr)
        logger.debug("Temperature: %sC", temp)
        return temp

    def read_power_pcb_temperature(self):
        """Read the power PCB temperature"""
        addr = (
            self.board.params["peripherals"]
            .get("power_pcb_temp", {})
            .get("addr", 0b0011_001)
        )
        temp = self._read_temperature(addr)
        logger.debug("Temperature: %sC", temp)
        return temp

    def read_udc1_1v2(self):
        """Read V1P2_UDC1 (see schematic) from the board."""
        return self._read_ltc2990_voltage("udc1_1v2")

    def read_udc1_2v5(self):
        """Read V2P5_UDC1 (see schematic) from the board"""
        return self._read_ltc2990_voltage("udc1_2v5")

    def read_udc2_1v2(self):
        """Read V1P2_UDC2 (see schematic) from the board"""
        return self._read_ltc2990_voltage("udc2_1v2")

    def read_udc2_2v5(self):
        """Read V2P5_UDC2 (see schematic) from the board"""
        return self._read_ltc2990_voltage("udc2_2v5")

    def read_fpga_1v0(self):
        """Read V1P8_FPGA (see schematic) from the board"""
        return self._read_ltc2990_voltage("fpga_1v0")

    def read_fpga_1v8(self):
        """Read V1P8_FPGA (see schematic) from the board"""
        return self._read_ltc2990_voltage("fpga_1v8")

    def read_fpga_io_2v5(self):
        """Read V2P5_FPGA_IO (see schematic) from the board"""
        return self._read_ltc2990_voltage("fpga_io_2v5")

    def read_fpga_io_3v3(self):
        """Read V3P3_FPGA_IO (see schematic) from the board"""
        return self._read_ltc2990_voltage("fpga_io_3v3")
