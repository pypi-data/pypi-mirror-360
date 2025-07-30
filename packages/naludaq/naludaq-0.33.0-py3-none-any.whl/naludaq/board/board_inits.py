"""BoardInits is a Factory for the init_board command lists.

This class returns a function that should initialize each board,
since they are all different.

"""
import logging
import time

from naludaq.backend.managers.connection import ConnectionManager
from naludaq.board.initializers import Initializers
from naludaq.board.initializers.aardvarcv3 import InitAardvarcv3
from naludaq.board.initializers.aodsoc import InitAodsoc
from naludaq.board.initializers.asocv3s import InitASoCv3S
from naludaq.board.initializers.hiper import InitHiper
from naludaq.board.initializers.init_aodsv2_eval import InitAodsv2Eval
from naludaq.board.initializers.init_hdsocv1 import InitHDSoCv1
from naludaq.board.initializers.init_hdsocv2 import InitHDSoCv2
from naludaq.board.initializers.init_udc import InitUDC16
from naludaq.board.initializers.init_upac96 import InitUPAC96
from naludaq.board.initializers.trbhm import InitTrbhm
from naludaq.communication import (
    AnalogRegisters,
    ControlRegisters,
    DigitalRegisters,
    I2CRegisters,
)
from naludaq.communication.i2c import readI2cReg, sendI2cCommand

LOGGER = logging.getLogger("naludaq.board_inits")


class BoardInits:
    """Factory for the init_board commands.
    Hardware paramters for the chip/board and
    changes when hardware changes.
    By having this class the actual storage of the paramters are
    removed from the logic of the rest o the program.

    Functions:
        init_board()

    """

    def __init__(self, board):
        self.board = board
        self._initializers = {
            "aardvarcv2": self.init_AARDVARCv2,
            "aardvarcv3": InitAardvarcv3,
            "aardvarcv4": InitAardvarcv3,
            "aodsv1": self.init_AODSv1,
            "aodsv2_eval": InitAodsv2Eval,
            "asoc": self.init_ASoC,
            "asocv2": self.init_ASoCv2,
            "asocv3": self.init_ASoCv3,
            "asocv3s": InitASoCv3S,
            "hdsocv1": InitHDSoCv1,
            "hdsocv1_evalr1": InitHDSoCv1,
            "hdsocv1_evalr2": InitHDSoCv1,
            "hdsocv2_eval": InitHDSoCv2,
            "hdsocv2_evalr2": InitHDSoCv2,
            "hiper": InitHiper,
            "aodsoc_asoc": InitAodsoc,
            "aodsoc_aods": InitAodsoc,
            "siread": self.init_SiREAD,
            "trbhm": InitTrbhm,
            "dsa-c10-8": InitTrbhm,
            "udc16": InitUDC16,
            "upac96": InitUPAC96,
            "upac32": self.init_upac32,
        }

    def run_init_function(self) -> bool:
        """Runs the initialization sequence for the board.

        Returns:
            True if the board was successfully initialized, False otherwise.
        """
        model = self.board.params["model"]
        LOGGER.info("Init board - %s", model)

        initializer = self._initializers.get(model, None)
        if initializer is None:
            LOGGER.error("Error in board_inits: model %s not found", model)
            return False
        elif isinstance(initializer, type) and issubclass(initializer, Initializers):
            return initializer(self.board).run()
        else:
            return initializer()

    def init_ASoC(self) -> bool:
        """Initialize the board functions.

        Run through the startup script to init the board.

        Returns:
            True if the board is successfully connected, False if connection failed.
        """
        ControlRegisters(self.board).write_all()

        ControlRegisters(self.board).write("3v3_en_main", True)
        time.sleep(0.25)
        LOGGER.info("Programming clock")
        self.board.clock.program(filename=self.board.params["default_si5341"])
        time.sleep(0.25)
        # Starting the clock output, or no clocks signal on the board.
        ControlRegisters(self.board).write("clk_oe", True)
        ControlRegisters(self.board).write("sysrst", False)
        self.analogStartup()
        self.board.ext_bias.set_dacs(self.board.params["ext_dac"])

        sendI2cCommand(self.board, "30", ["05"])  # tempSensor to temp reg
        sendI2cCommand(self.board, "D0", ["00111011"])  # set up current sense ADC
        self.board.trigger.values = self.board.trigger.params.get(
            "default_trigger_value", 1350
        )
        self.board.write_triggers()
        LOGGER.info("Programming FPGA settings")
        DigitalRegisters(self.board).write_all()
        ControlRegisters(self.board).write("ls_oe", True)
        self.board.connection.DEBUG = False

        return True

    def init_ASoCv2(self) -> bool:
        """Initialize the board functions.

        Run through the startup script to init the board.

        Returns:
            True if the board is successfully connected, False if connection failed.
        """
        ControlRegisters(self.board).write_all()
        self._i2c_startup()

        ControlRegisters(self.board).write("2v5_en", True)
        time.sleep(0.25)
        LOGGER.info("Programming clock")
        self.board.clock.program(filename=self.board.params["clock_file"])
        time.sleep(0.25)
        ControlRegisters(self.board).write("clk_noe", False)
        ControlRegisters(self.board).write("sysrst", True)
        ControlRegisters(self.board).write("sysrst", False)
        ControlRegisters(self.board).write("iomode0", True)
        ControlRegisters(self.board).write("iomode1", False)

        self.analogStartup()
        DigitalRegisters(self.board).write_all()
        self.board.ext_bias.set_dacs(self.board.params["ext_dac"])

        I2CRegisters(self.board).write_all()
        sendI2cCommand(self.board, "30", ["05"])  # tempSensor to temp reg
        sendI2cCommand(self.board, "D0", ["00111011"])  # set up current sense ADC

        LOGGER.info("Programming FPGA settings")

        return True

    def init_ASoCv3(self) -> bool:
        """Initialize the board functions.

        Run through the startup script to init the board.

        Returns:
            True if the board is successfully connected, False if connection failed.
        """
        ControlRegisters(self.board).write_all()
        self._i2c_startup()

        ControlRegisters(self.board).write("2v5_en", True)
        time.sleep(0.25)
        LOGGER.info("Programming clock")
        self.board.clock.program(filename=self.board.params["clock_file"])
        time.sleep(0.25)
        ControlRegisters(self.board).write("clk_noe", False)
        ControlRegisters(self.board).write("sysrst", True)
        ControlRegisters(self.board).write("sysrst", False)
        ControlRegisters(self.board).write("iomode0", True)
        ControlRegisters(self.board).write("iomode1", False)

        self.analogStartup()
        DigitalRegisters(self.board).write_all()
        ext_dac_val = self.board.params.get("ext_dac", {})
        for chan, dac_val in ext_dac_val["channels"].items():
            self.board.ext_bias.set_single_dac(
                chan, dac_val
            )  # self.board.params['ext_dac'])

        sendI2cCommand(self.board, "30", ["05"])  # tempSensor to temp reg
        sendI2cCommand(self.board, "D0", ["00111011"])  # set up current sense ADC

        LOGGER.info("Programming FPGA settings")

        return True

    def init_AODSv1(self) -> bool:
        """Initialize the board functions.

        Run through the startup script to init the board.

        Returns:
            True if the board is successfully connected, False if connection failed.
        """
        ControlRegisters(self.board).write_all()
        self._i2c_startup()

        ControlRegisters(self.board).write("2v5_en", True)
        time.sleep(0.25)
        LOGGER.info("Programming clock")
        self.board.clock.program(filename=self.board.params["clock_file"])
        time.sleep(0.25)
        ControlRegisters(self.board).write("clk_noe", False)
        ControlRegisters(self.board).write("sysrst", True)
        ControlRegisters(self.board).write("sysrst", False)
        ControlRegisters(self.board).write("iomode0", True)
        ControlRegisters(self.board).write("iomode1", False)

        self.analogStartup()
        DigitalRegisters(self.board).write_all()
        ext_dac_val = self.board.params.get("ext_dac", {})
        for chan, dac_val in ext_dac_val["channels"].items():
            self.board.ext_bias.set_single_dac(
                chan, dac_val
            )  # self.board.params['ext_dac'])

        I2CRegisters(self.board).write_all()
        sendI2cCommand(self.board, "30", ["05"])  # tempSensor to temp reg
        sendI2cCommand(self.board, "D0", ["00111011"])  # set up current sense ADC

        # AODS specific
        DigitalRegisters(self.board).write("waitread", 1)

        LOGGER.info("Programming FPGA settings")

        return True

    def init_SiREAD(self) -> bool:
        ControlRegisters(self.board).write_all()
        self._i2c_startup()

        time.sleep(0.1)
        ControlRegisters(self.board).write("v2v5_en", True)

        self.change_si570(100)

        AnalogRegisters(self.board).write_all()

        time.sleep(0.1)
        for _ in range(5):
            ControlRegisters(self.board).write("wraddrsync", True)
            time.sleep(0.1)
            ControlRegisters(self.board).write("wraddrsync", False)
            time.sleep(0.1)
        time.sleep(0.1)

        sendI2cCommand(self.board, "30", ["05"])  # tempSensor to temp reg
        sendI2cCommand(self.board, "D0", ["00111011"])  # set up current sense ADC

        return True

    def _power_toggle(self, state):
        for register in [
            "2v5_en",
            "1v2_en",
            "3v3_i2c_en",
            "clk2v5_en",
            "clk1v8_en",
            "clk_i2c_sel",
        ]:
            ControlRegisters(self.board).write(register, state)

    def init_AARDVARCv2(self) -> bool:
        ControlRegisters(self.board).write_all()
        self._i2c_startup()

        self._power_toggle(False)
        self._power_toggle(True)

        time.sleep(0.25)
        LOGGER.info("Programming clock")
        self.board.clock.program(filename=self.board.params["clock_file"])
        time.sleep(0.25)
        ControlRegisters(self.board).write("clk_oeb", False)
        ControlRegisters(self.board).write("sysrst", True)
        ControlRegisters(self.board).write("sysrst", False)
        ControlRegisters(self.board).write("iomode0", True)
        ControlRegisters(self.board).write("iomode1", False)

        self.analogStartup()
        DigitalRegisters(self.board).write_all()
        ext_dac_val = self.board.params.get("ext_dac", {})
        for chan, dac_val in ext_dac_val["channels"].items():
            self.board.ext_bias.set_single_dac(chan, dac_val)

        I2CRegisters(self.board).write_all()
        sendI2cCommand(self.board, "30", ["05"])  # tempSensor to temp reg
        sendI2cCommand(self.board, "D0", ["00111011"])  # set up current sense ADC

        return True

    def init_HIPeR(self) -> bool:
        ControlRegisters(self.board).write_all()
        self._i2c_startup()

        self._power_toggle(False)
        self._power_toggle(True)

        time.sleep(0.25)
        LOGGER.info("Programming clock")
        self.board.clock.program(filename=self.board.params["clock_file"])
        time.sleep(0.25)
        ControlRegisters(self.board).write("clk_oeb", False)
        ControlRegisters(self.board).write("sysrst", True)
        ControlRegisters(self.board).write("sysrst", False)
        ControlRegisters(self.board).write("iomode0", True)
        ControlRegisters(self.board).write("iomode1", False)

        self.analogStartup()
        DigitalRegisters(self.board).write_all()
        ext_dac_val = self.board.params.get("ext_dac", {})
        for chan, dac_val in ext_dac_val["channels"].items():
            self.board.ext_bias.set_single_dac(
                chan, dac_val
            )  # self.board.params['ext_dac'])

        I2CRegisters(self.board).write_all()
        sendI2cCommand(self.board, "30", ["05"])  # tempSensor to temp reg
        sendI2cCommand(self.board, "D0", ["00111011"])  # set up current sense ADC

    def init_upaci(self) -> bool:
        """Starting the UPAC-I board."""
        if self.board.using_new_backend:
            return self._init_upac32_new()
        # ControlRegisters(self.board).write_all_registers()
        LOGGER.info("Setting up UPAC-I")
        if (
            self.board.connection.baud >= 1_000_000
            or self.board.connection_info["speed"] >= 1_000_000
        ):
            self.board.connection.rtscts = True
            ControlRegisters(self.board).write("uart_handshake_en_out", True)
        else:
            self.board.connection.rtscts = False
            ControlRegisters(self.board).write("uart_handshake_en_out", False)
        try:
            ctrl_regs = ControlRegisters(self.board).read_all()
        except Exception:
            LOGGER.error("Can't read the control registers off the board.")
        else:
            self.board.registers["control_registers"] = ctrl_regs

        dac_val = 30_000
        ControlRegisters(self.board).write("dac_vbias00_07_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias08_15_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias16_23_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias24_31_out", dac_val)
        ControlRegisters(self.board).write("dac_write_strobe", True)
        ControlRegisters(self.board).write("dac_write_strobe", False)

        return True

    def init_upac32(self) -> bool:
        """Starting the upac32 board."""
        if self.board.using_new_backend:
            return self._init_upac32_new()

        # ControlRegisters(self.board).write_all_registers()
        LOGGER.info("Setting up UPAC32")
        # ControlRegisters(self.board).write("baud_rate_divisor", 108)
        if (
            self.board.connection.baud >= 1_000_000
            or self.board.connection_info["speed"] >= 1_000_000
        ):
            self.board.connection.rtscts = True
            ControlRegisters(self.board).write("uart_handshake_en_out", True)
        else:
            self.board.connection.rtscts = False
            ControlRegisters(self.board).write("uart_handshake_en_out", False)

        try:
            ctrl_regs = ControlRegisters(self.board).read_all()
        except Exception:
            LOGGER.error("Can't read the control registers off the board.")
        else:
            self.board.registers["control_registers"] = ctrl_regs

        dac_val = 30_000
        ControlRegisters(self.board).write("dac_vbias00_07_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias08_15_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias16_23_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias24_31_out", dac_val)
        ControlRegisters(self.board).write("dac_write_strobe", True)
        ControlRegisters(self.board).write("dac_write_strobe", False)

        return True

    def _init_upac32_new(self) -> bool:
        """Starting the upac32 board."""
        LOGGER.info("Setting up UPAC32")
        device = ConnectionManager(self.board)
        if (
            device.baud_rate >= 1_000_000
            or self.board.connection_info["baud_rate"] >= 1_000_000
        ):
            device.rts_cts = True
            ControlRegisters(self.board).write("uart_handshake_en_out", True)
        else:
            device.rtscts = False
            ControlRegisters(self.board).write("uart_handshake_en_out", False)

        try:
            ctrl_regs = ControlRegisters(self.board).read_all()
        except Exception:
            LOGGER.error("Can't read the control registers off the board.")
        else:
            self.board.registers["control_registers"] = ctrl_regs

        dac_val = 30_000
        ControlRegisters(self.board).write("dac_vbias00_07_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias08_15_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias16_23_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias24_31_out", dac_val)
        ControlRegisters(self.board).write("dac_write_strobe", True)
        ControlRegisters(self.board).write("dac_write_strobe", False)

        return True

    def init_zdigitizer(self) -> bool:
        """Starting the Z-Digitizer board."""
        if self.board.using_new_backend:
            return self._init_upac32_new()
        # ControlRegisters(self.board).write_all_registers()
        LOGGER.info("Setting up Z-Digitizer")
        if (
            self.board.connection.baud >= 1_000_000
            or self.board.connection_info["speed"] >= 1_000_000
        ):
            self.board.connection.rtscts = True
            ControlRegisters(self.board).write("uart_handshake_en_out", True)
        else:
            self.board.connection.rtscts = False
            ControlRegisters(self.board).write("uart_handshake_en_out", False)
        try:
            ctrl_regs = ControlRegisters(self.board).read_all()
        except Exception:
            LOGGER.error("Can't read the control registers off the board.")
        else:
            self.board.registers["control_registers"] = ctrl_regs

        dac_val = 30_000
        ControlRegisters(self.board).write("dac_vbias00_07_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias08_15_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias16_23_out", dac_val)
        ControlRegisters(self.board).write("dac_vbias24_31_out", dac_val)
        ControlRegisters(self.board).write("dac_write_strobe", True)
        ControlRegisters(self.board).write("dac_write_strobe", False)

        return True

    def change_si570(self, freq):
        """
        change the clock frequency of the si570 by writing to register 13
        Values taken from the XO calculator (start-up freq = 156.25)
        """
        board = self.board
        board.connection.reset_input_buffer()
        board.connection.reset_output_buffer()
        addr = "BA"

        hs_map = [
            (4, "000"),
            (5, "001"),
            (6, "010"),
            (7, "011"),
            (9, "101"),
            (11, "111"),
        ]

        # restart chip
        sendI2cCommand(board, addr, (["87", "01"]))
        time.sleep(2)

        # read start up freq configuration
        temp = readI2cReg(board, addr, "07")
        hs_div_bin = temp >> 5
        hs_div = -1
        for hs_div_i in hs_map:
            if int(hs_div_i[1], 2) == hs_div_bin:
                hs_div = hs_div_i[0]
                break
        if hs_div == -1:
            LOGGER.error("no valid hs_div found... %s", hs_div_bin)
            return

        n1 = (temp & 31) << 2
        temp = readI2cReg(board, addr, "08")
        n1 += temp >> 6
        n1 += 1

        rfreq = (temp & 63) << 32
        rfreq += readI2cReg(board, addr, "09") << 24
        rfreq += readI2cReg(board, addr, "0A") << 16
        rfreq += readI2cReg(board, addr, "0B") << 8
        rfreq += readI2cReg(board, addr, "0C")
        rfreq2 = rfreq / (2**28)

        LOGGER.debug("hs_div=%s , n1=%s", hs_div, n1)
        LOGGER.debug("rfreq=%s , rfreq/(2^28)=%s", hex(rfreq), rfreq2)

        fxtal = (156.25 * hs_div * n1) / rfreq2

        LOGGER.debug("fxtal=%s", fxtal)

        # calculate new values
        good = False

        for hs_div_i in hs_map:
            for n1 in range(0, 128, 2):
                fdco = hs_div_i[0] * n1 * freq
                if fdco > 4850 and fdco < 5670:
                    LOGGER.debug("fdco=%s @n1=%s, hs_div_i=%s", fdco, n1, hs_div_i)
                    good = True
                    hs_div = hs_div_i
                    break
            if good:
                break

        if not good:
            LOGGER.debug("no valid values?")
            return
        LOGGER.debug(hs_div)

        rfreq = fdco / fxtal
        rfreqHex = hex(int(rfreq * 2**28))[2:].zfill(10)
        LOGGER.debug("rfreqHex:%s hs_dev[0]:%s n1:%s", rfreqHex, hs_div[0], n1)

        new_freq1 = hex(int(int(hs_div[1], 2) * (2**5) + (n1 - 1) / (2**2)))[2:].zfill(
            2
        )
        new_freq2 = (
            hex(((n1 - 1) % 4) * (2**6) + int(rfreqHex[0], 16) * (2**5))[2:-1]
            + rfreqHex[1]
        )

        sendI2cCommand(board, addr, ["89", "10"])  # freeze DCO
        sendI2cCommand(board, addr, ["07", new_freq1])
        sendI2cCommand(board, addr, ["08", new_freq2])
        sendI2cCommand(board, addr, ["09", rfreqHex[2:4]])
        sendI2cCommand(board, addr, ["0A", rfreqHex[4:6]])
        sendI2cCommand(board, addr, ["0B", rfreqHex[6:8]])
        sendI2cCommand(board, addr, ["0C", rfreqHex[8:]])
        sendI2cCommand(board, addr, ["89", "00"])  # unfreeze DCO
        sendI2cCommand(board, addr, ["87", "40"])  # set NewFreq bit within 10ms

    def analogStartup(self):
        model = self.board.params["model"]
        if model in ["asoc", "asoc-ml605", "asocv2", "asocv3", "aodsv1"]:
            self.analogStartup_ASoC()

        elif model in ["aardvarcv2"]:
            self.analogStartup_AARDVARC()

        elif model == "siread":
            AnalogRegisters(self.board).write_all()

        else:
            LOGGER.error("Error: analogStartup() didn't recognize model %s", model)

    def analogStartup_ASoC(self):
        """Startup sequence for the analog.

        Same as analog update, except it sets and unsets vanbuff to get the dll going.
        """
        LOGGER.debug("Setting analog ASoC control registers")
        board = self.board
        AnalogRegisters(board).write_all()
        AnalogRegisters(board).write("qbuff", 0)
        AnalogRegisters(board).write("vanbuff", 0xB00)
        time.sleep(1)
        AnalogRegisters(board).write("qbuff", 2048)
        AnalogRegisters(board).write("vanbuff", 0)

    def analogStartup_AARDVARC(self):
        """Startup sequence for the analog.

        Same as analog update, except it sets and unsets vanbuff to get the dll going.
        """
        board = self.board
        LOGGER.debug("Setting analog ASoC control registers")
        AnalogRegisters(board).write_all()
        AnalogRegisters(board).write("qbias", 0)
        AnalogRegisters(board).write("vadjn_sw", True)
        time.sleep(1)
        AnalogRegisters(board).write("qbias", 2048)
        AnalogRegisters(board).write("vadjn_sw", False)

    def _i2c_startup(self):
        """Startup for I2C. Just powers it on."""
        I2CRegisters(self.board).write("i2c_en", True)
