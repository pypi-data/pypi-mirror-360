"""Initializer for the UDC board

This initializer will run the init sequence for the UDC board.
It contains all UDC16 specific startup sequence
"""
import functools
import logging
import time

from naludaq.board import initializers
from naludaq.controllers.biasing_mode import get_biasing_mode_controller

logger = logging.getLogger(__name__)


def func_print(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f" Running: {func.__name__} ".ljust(80, "#"))
        v = func(*args, **kwargs)
        return v

    return wrapper


class InitUDC16(initializers.Initializers):
    def __init__(self, board):
        super().__init__(board, "udc16")
        self.power_sequence = [
            "2v5_en",
            "1v2_en",
            "clk2v5_en",
            "clk1v8_en",
        ]
        self.rxtx = [
            "rx_enable",
            "tx_enable",
        ]

    def run(self):
        # UDC_FPGA_register_init
        self._fpga_init()

        # POWER ON FMC BOARD
        self._power_toggle(False)
        self._power_toggle(True)

        self._program_clock()

        # reset sysrst and regclr
        self._reset_sys()
        self._reset_digital()

        # Enable Rx and Tx
        self._rxtx_toggle(True)

        # Analog and digital startup:
        # Digital startup
        self._digital_startup()

        # Analog_startup
        self._analog_startup()

        # UDC ASIC reset
        self._asic_reset()

        # Set DACS
        self._init_dacs()

        return True

    @func_print
    def _fpga_init(self):
        """Write all FPGA registers to their default values."""
        self.control_registers.write_all()
        self.i2c_registers.write("i2c_en", True)

    @func_print
    def _power_toggle(self, state):
        """Toggles the power rails defined in `power_sequence` attribute"""
        for register in self.power_sequence:
            self.control_write(register, state)

    @func_print
    def _program_clock(self):
        """Program the clock chip, uses the clockfile in the paramters if it exits."""
        time.sleep(0.05)
        self.board.clock.program(filename=self.board.params["clock_file"])
        time.sleep(0.05)

    @func_print
    def _reset_sys(self):
        """Reset the ASIC and clear the analog and digital registers"""
        self.control_write("sysrst", True)
        self.control_write("regclr", True)

        self.control_write("sysrst", False)
        self.control_write("regclr", False)
        self._reset_digital()

    def _reset_digital(self):
        """Reset digital side of the ASIC"""
        self.control_write("digrst", True)
        self.control_write("wave_fifo_reset", True)

        self.control_write("digrst", False)
        self.control_write("wave_fifo_reset", False)

    @func_print
    def _asic_reset(self):
        """Reset the asic, analog side, digital side, and fifo"""
        self.control_write("sysrst", True)
        self.control_write("sysrst", False)
        self._reset_digital()

    @func_print
    def _rxtx_toggle(self, state):
        """Toggles ASIC rx and tx enable. True when talking to ASIC."""
        for register in self.rxtx:
            self.control_write(register, state)

    @func_print
    def _digital_startup(self):
        """Startup the digital side by programming all registers"""
        self.digital_registers.write_all()

    @func_print
    def _analog_startup(self):
        """Start the analog side of the chip"""
        # PCLK decoding ANALOG REGISTERS decoding
        self.analog_registers.write_all()

        # DLL START UP SEQUENCE
        self._dll_startup()
        self._set_default_biasing_mode()

    @func_print
    def _dll_startup(self):
        """Starting the delay line on the analog side."""
        self.analog_write("qbias", 0)
        self.analog_write("vadjn_sw", 1)
        time.sleep(1)
        self.analog_write("qbias", 2048)
        self.analog_write("vadjn_sw", 0)

    @func_print
    def _init_dacs(self):
        """Program the left and right side DACs"""
        dacvalues = self._get_dacvalues()

        for channel, value in dacvalues.items():
            self.board.ext_bias.set_single_dac(channel, value)

    def _get_dacvalues(self) -> dict:
        """Return a dict with all the "channels: dac_values"""
        return self.board.params.get("ext_dac", {}).get("channels", {})

    def _set_default_biasing_mode(self):
        get_biasing_mode_controller(self.board).set_biasing_mode(
            self.board.params["intamp_bias_mode_chan0_7"],
            self.board.params["intamp_bias_mode_chan8_15"],
        )
