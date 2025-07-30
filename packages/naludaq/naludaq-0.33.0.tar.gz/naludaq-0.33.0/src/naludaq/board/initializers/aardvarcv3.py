"""Initializer for the aardvarcv3 eval board
"""
import logging
import time

from naludaq.board.initializers import Initializers
from naludaq.communication import sendI2cCommand
from naludaq.helpers.decorators import log_function

logger = logging.getLogger("naludaq.init_aardvarcv3")


class InitAardvarcv3(Initializers):
    def __init__(self, board):
        """Initializer for the aardvarcv3.

        Args:
            board (Board): the board to initialize.
        """
        super().__init__(
            board, ["aardvarcv3", "aardvarcv4", "trbhm", "dsa-c10-8", "hiper"]
        )
        self.power_sequence = [
            "2v5_en",
            "1v2_en",
            "3v3_i2c_en",
            "clk2v5_en",
            "clk1v8_en",
            "clk_i2c_sel",
        ]

    def run(self) -> bool:
        """Runs the initialization sequence.

        Returns:
            True, always.
        """
        # Initialize FPGA registers
        self._fpga_init()
        self._i2c_startup()

        # Power on FMC board
        self._power_toggle(False)
        self._power_toggle(True)
        time.sleep(0.25)

        # Program the clock
        self._init_clock()

        # Select parallel interface
        self._system_reset()
        self._set_serial_mode(False)

        # Chip-side register startup
        self._analog_startup()
        self._digital_startup()

        # External devices
        self._init_dacs()
        self._init_i2c_devices()

        return True

    @log_function(logger)
    def _fpga_init(self):
        """Write all FPGA registers to their default values."""
        self.control_registers.write_all()

    @log_function(logger)
    def _i2c_startup(self):
        """Initialize the I2C interface."""
        self.i2c_registers.write("i2c_en", True)

    @log_function(logger)
    def _power_toggle(self, state):
        """Toggles the power rails defined in `power_sequence` attribute."""
        for register in self.power_sequence:
            self.control_write(register, state)

    @log_function(logger)
    def _init_clock(self):
        """Program the clock with the clockfile from the params"""
        logger.info("Programming clock")
        clockfile = self.board.params["clock_file"]
        self.board.clock.program(clockfile)
        time.sleep(0.25)
        self.control_write("clk_oeb", False)

    @log_function(logger)
    def _system_reset(self):
        """Toggle the sysrst pin high, then low"""
        self.control_registers.write("sysrst", True)
        self.control_registers.write("sysrst", False)

    @log_function(logger)
    def _set_serial_mode(self, enabled: bool):
        """Turn on or off serial mode."""
        self.board.control.set_serial_mode(enabled)

    @log_function(logger)
    def _digital_startup(self):
        """Startup the digital side of the chip by programming all registers."""
        self.digital_registers.write_all()

    @log_function(logger)
    def _analog_startup(self):
        """Start the analog side of the chip by programming all registers."""
        self.analog_registers.write_all()
        self._dll_startup()

    @log_function(logger)
    def _dll_startup(self):
        """Starting the delay line on the analog side.

        Sets and unsets vanbuff to get the dll going and
        changes the vadjp values to ensure proper SST duty cycle once locked.
        """
        self.analog_registers.write("qbias", 0)
        self.analog_registers.write("vadjn_sw", True)
        time.sleep(1)
        self.analog_registers.write("qbias", 2048)
        self.analog_registers.write("vadjn_sw", False)

    @log_function(logger)
    def _init_dacs(self):
        """Write the DAC values using the defaults in the YAML."""
        for channel, value in self._get_dac_values().items():
            self.board.ext_bias.set_single_dac(channel, value)

    def _get_dac_values(self) -> dict:
        """Return a dict with all the {channels: dac_values}"""
        return self.board.params.get("ext_dac", {}).get("channels", {})

    @log_function(logger)
    def _init_i2c_devices(self):
        """Initialize I2C devices on the eval card"""
        self.i2c_registers.write_all()
        sendI2cCommand(self.board, "30", ["05"])  # tempSensor to temp reg
        sendI2cCommand(self.board, "D0", ["00111011"])  # set up current sense ADC
