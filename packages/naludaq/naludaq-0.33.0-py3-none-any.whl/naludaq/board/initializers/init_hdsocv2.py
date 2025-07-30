"""Initializer for the HDSoCv1 board

This initializer will run the init sequence for the HDSoCv1 board.
It contains the HDSoCv1 specific startup sequence.
"""
import logging
import time

from naludaq.board.initializers import Initializers
from naludaq.helpers.decorators import log_function
from naludaq.communication.spi import SPIConnection, SPIBUS_t
from naludaq.devices.ad5674r import AD5674R_SPI

logger = logging.getLogger("naludaq.init_hdsocv2")

VALID_BOARDS = [
    "hdsocv2_eval",
    "hdsocv2_evalr2",
]


# Temporary device mapping, needs to be changed.
# If you see this comment and there are device mappings below, move them to naluconfigs.

DAC_W1_map = {
    0: 12,
    1: 13,
    2: 14,
    3: 15,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 8,
    13: 9,
    14: 10,
    15: 11,
}

DAC_W2_map = {
    16: 11,
    17: 10,
    18: 9,
    19: 8,
    20: 3,
    21: 2,
    22: 1,
    23: 0,
    24: 7,
    25: 6,
    26: 5,
    27: 4,
    28: 15,
    29: 14,
    30: 13,
    31: 12,
}

DAC_E1_map = {
    32: 11,
    33: 10,
    34: 9,
    35: 8,
    36: 3,
    37: 2,
    38: 1,
    39: 0,
    40: 7,
    41: 6,
    42: 5,
    43: 4,
    44: 15,
    45: 14,
    46: 13,
    47: 12,
}

DAC_E2_map = {
    48: 12,
    49: 13,
    50: 14,
    51: 15,
    52: 4,
    53: 5,
    54: 6,
    55: 7,
    56: 0,
    57: 1,
    58: 2,
    59: 3,
    60: 8,
    61: 9,
    62: 10,
    63: 11,
}


class InitHDSoCv2(Initializers):
    def __init__(self, board):
        """Initializer for HDSoCv2.

        Args:
            board (Board): the board to initialize.
        """
        super().__init__(board, VALID_BOARDS)
        self.power_sequence = [
            "en_avdd",
            "en_dvdd",
            "en_pllvdd",
            "clk2v5_en",
            "clk1v8_en",
        ]

    def run(self) -> bool:
        """Runs the initialization sequence.

        Returns:
            True, always.
        """
        # Initialize FPGA registers
        self._fpga_init()

        # Power on FMC board
        self._power_toggle(False)
        time.sleep(0.05)
        self._power_toggle(True)
        time.sleep(0.25)

        self._program_clock()

        self._reset_sys()
        self._set_serial_mode(True)
        time.sleep(0.1)
        self.board.control.set_loopback_enabled(False)

        # Chip-side register startup
        self._analog_startup()
        self._digital_startup()

        # init SPI daisy chains
        self._init_spi_connection()

        # Set DACs
        self._init_dacs()

        # Enable ASIC serial output padding  on the FPGA, 12-bit -> 16-bit
        self.board.control.enable_serial_padding(True)

        return True

    def _init_spi_connection(self):
        """Initialize the SPI connection for the board."""
        self.board.spi_connection = SPIConnection(self.board)

        self.board.spi_connection.add_bus(
            bus_id=0b01,
            bus_type=SPIBUS_t.DAISY_CHAIN,
        )

        self.board.spi_connection.add_bus(
            bus_id=0b10,
            bus_type=SPIBUS_t.DAISY_CHAIN,
        )

        self.board.spi_connection.add_bus(
            bus_id=0b11,
            bus_type=SPIBUS_t.DAISY_CHAIN,
        )

        self._populate_spi_connection()

        self.board.spi_connection.init()

    def _populate_spi_connection(self):
        """Populate the SPI connection with the devices.

        The devices are connected according to the schematic:
        320-0065-110

        """

        device_map = {
            0: {
                "device_id": 1,
                "bus_id": 0b01,
                "channel_map": DAC_W1_map,
            },
            16: {
                "device_id": 0,
                "bus_id": 0b01,
                "channel_map": DAC_W2_map,
            },
            32: {
                "device_id": 1,
                "bus_id": 0b10,
                "channel_map": DAC_E1_map,
            },
            48: {
                "device_id": 0,
                "bus_id": 0b10,
                "channel_map": DAC_E2_map,
            },
        }

        for channel, values in device_map.items():
            bus_id = values["bus_id"]
            device_id = values["device_id"]
            self.board.spi_connection[bus_id][device_id] = AD5674R_SPI(
                spi_connection=self.board.spi_connection,
                bus_id=values["bus_id"],
                device_id=values["device_id"],
                channelmap=values["channel_map"],
                daisy_chained=True,
            )
            # bus_id=values["bus_id"],
            # device_id=values["device_id"],
            # )

    @log_function(logger)
    def _fpga_init(self):
        """Write all FPGA registers to their default values."""
        self.control_registers.write_all()
        self.i2c_registers.write("i2c_en", True)

    @log_function(logger)
    def _power_toggle(self, state):
        """Toggles the power rails defined in `power_sequence` attribute."""
        for register in self.power_sequence:
            self.control_write(register, state)

    @log_function(logger)
    def _program_clock(self):
        """Program the clock chip, uses the clockfile in the paramters if it exits."""
        self.board.clock.program(filename=self.board.params["clock_file"])
        self.control_write("clk_oeb", False)

    @log_function(logger)
    def _reset_sys(self):
        """Reset the ASIC and clear the analog and digital registers"""
        self.control_write("sysrst", True)
        self.control_write("regclr", True)

        self.control_write("sysrst", False)
        self.control_write("regclr", False)

    @log_function(logger)
    def _set_serial_mode(self, enabled: bool):
        """Turn on or off serial mode."""
        self.board.control.set_serial_mode(enabled)

    @log_function(logger)
    def _digital_startup(self):
        """Startup the digital side of the chip by programming all registers."""
        self.digital_registers.write_all()

    def _set_scvbias(self):
        """Set the SCVBIAS value for both sides to default values.

        The SCVBias values are set to the values in NaluConfigs.
        """
        self.analog_write("scvbias_left")
        self.analog_write("scvbias_right")

    @log_function(logger)
    def _analog_startup(self):
        """Start the analog side of the chip by programming all registers."""
        self._set_scvbias()
        self.analog_registers.write_all()
        self._dll_startup()

    @log_function(logger)
    def _dll_startup(self):
        """Starting the delay line on the analog side.

        Sets and unsets vanbuff to get the dll going and
        changes the vadjp values to ensure proper SST duty cycle once locked.
        """

        # DLL startup
        for _side in ["left", "right"]:
            self.analog_write(f"qbias_{_side}", 0)
            self.analog_write(f"vadjn_{_side}")  # Use vadjn from yaml
            self.analog_write(f"vanbuf_{_side}", 1000)
            time.sleep(0.5)
            self.analog_write(f"qbias_{_side}", 2950)
            self.analog_write(f"vanbuf_{_side}", 0)

    @log_function(logger)
    def _init_dacs(self):
        """Program the default values to left and right side DACs"""
        channels = list(range(self.board.channels))
        self.board.ext_bias.set_dacs(channels=channels)
