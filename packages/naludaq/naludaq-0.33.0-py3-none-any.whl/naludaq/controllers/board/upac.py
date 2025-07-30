"""
"""
from logging import getLogger

from naludaq.backend.managers.connection import ConnectionManager
from naludaq.backend.models.device import DeviceType
from naludaq.communication import ControlRegisters
from naludaq.controllers.controller import Controller

LOGGER = getLogger("naludaq.board_controller_upac")
NON_UDP = [DeviceType.SERIAL, DeviceType.D2XX, DeviceType.D3XX]

TRIGGERS = {
    "software": "00",
    "auto": "01",
    "external": "10",
    "self": "11",
}


class UpacBoardController(Controller):
    """The board control communicates with to the board.

    This class is stateless, you need to supply the board to the class to perform actions on it.
    There is no need to store the controller, it will only be used to control the board.

    It is the interface between the application and the board.
    The Analytics package or the GUI uses this class to communicate with the
    hardware. Keeps track of all registers etc.
    It doesn't receive continous data, the data acquisition module should be used for that.
    """

    def __init__(self, board):
        super().__init__(board)

    def start_readout(
        self,
        trigger_type: str = "software",
    ):
        """Sends a readout signal to the board.

        Obstensibly reads out the chip?

        Args:
            trigger_type (str):
                "There are 4 trigger modes:

                ‘00’	: 	Software Trigger Mode, the power on default.
                ‘01’	: 	Auto Trigger Mode. 1-2Hz auto trigger data rate.
                ‘10’	:	External Trigger Mode.
                ‘11’	: 	Self Trigger Mode.

        Command
        -------

        command is: BMMXXVVV
        MM = singleEvent(7) + readoutEn(6) + pedSel(5 dt 4) + modeSel(3 dt 0)
        - modeSel=x"0" analog write
        - modeSel=x"1" digital write
        - modeSel=x"2" digital read
        - modeSel=x"3" waveform read

        VVVVV = addr_sel(19 dt 12) + data_sel(11 dt 0)
        - data_sel(5 downto 4) = trig type
        - data_sel(3 downto 2) = lb type
        - data_sel(1 downto 0) = acq type


        """
        if not isinstance(trigger_type, str):
            raise TypeError(f"trigger_type must be a str, got {type(trigger_type)}")
        if trigger_type.lower() in TRIGGERS.values():
            trigger_mode = trigger_type
        elif trigger_type.lower() in TRIGGERS.keys():
            trigger_mode = TRIGGERS[trigger_type]
        else:
            raise ValueError(
                f"trig not valid, got {trigger_type}, "
                "options are 'software', auto', 'external', 'self'"
            )
        self._write_control_register("trigger_mode", int(trigger_mode, 2))

        # Needed to enable self trigger
        self._write_control_register("self_trigger_or_enable", trigger_mode == "11")
        self.is_reading_out = True

    def stop_readout(self):
        """Toggles the "stopacq" signal on the readout module.

        It's equivalent of asking it nicely to stop reading.
        """
        # if self.trigger_mode == "00":
        #     self._write_control_register("software_trigger", False)
        self._write_control_register("trigger_mode", int("00", 2))
        self.is_reading_out = False

    def toggle_trigger(self):
        """Toggles the software trigger bit, should result in a software trigger event."""
        LOGGER.debug("Toggle software trigger")
        self._write_control_register("software_trigger", True)
        self._write_control_register("software_trigger", False)

    def toggle_reread(self):
        """"""
        self._write_control_register("reread_data", True)
        self._write_control_register("reread_data", False)

    def reset_board(self):
        """Try and reset the board.

        In case the FPGA get stuck this can help reset the state.
        """
        # time.sleep(0.02)
        # self.digital_reset()
        # time.sleep(0.02)
        # self.sysrst()

    def digital_reset(self):
        """Toggles the "reset" port on the readout module.

        Forcibly returns the chip to default state.
        """
        # self._write_control_register("digrst", True)
        # self._write_control_register("digrst", False)

    def clear_buffer(self):
        """Clears the UART buffer on both CPU and FPGA side."""
        try:
            self._clear_fpga_buffer()
        except Exception:
            pass

        try:
            self._clear_uart_buffer()
        except Exception:
            pass

    def _clear_fpga_buffer(self):
        self._write_control_register("wave_fifo_reset", True)
        self._write_control_register("wave_fifo_reset", False)

    def _clear_uart_buffer(self):
        if self.board.using_new_backend:
            device = ConnectionManager(self.board).device
            if device.type in NON_UDP:
                device.clear_buffers()
        else:
            self.board.connection.reset_input_buffer()

    def sysrst(self):
        """Toggles the sysrst pin, which resets the digital portion of the chip"""
        # self._write_control_register("sysrst", True)
        # self._write_control_register("sysrst", False)

    #############################################################################
    # Random Stuff, may or maynot work... Below functions need to be validated.
    #############################################################################

    def read_scalers(self, channels: list[int] = None):
        """Not implemented."""
        # self.stop_readout()
        scalers = []
        # for i in range(0, 4):
        #     name = "scal" + str(i)
        #     scalers.append(DigitalRegisters(self.board).read(name))
        #     # if Print: logger.debug("%s %s", name, scalers[-1])

        # scalers.append(DigitalRegisters(self.board).read("scalmon"))
        # if Print: logger.debug("scalmon %s", scalers[-1])
        return scalers

    def read_firmware_version(self):
        """Read the firmware version.

        This is a control register.
        """
        result = 0
        try:
            result = ControlRegisters(self.board).read("version_number")
        except Exception:
            LOGGER.error("Can't read firmware version")
        return result

    def read_identifier(self) -> str:
        """Read the board identifier."""
        result = ControlRegisters(self.board).read("identifier")
        return result

    def enable_testmode(self, enabled: bool):
        """Enables the test-pattern output.

        Set the fpga in a mode to output a known test-pattern.
        """
        # ControlRegisters(self.board).write("fake", enabled)

    def get_available_chips(self) -> list[int]:
        """Get a list of available chip numbers."""
        return list(range(self.board.params.get("num_chips", 1)))

    def set_lookahead(self):
        """Set look ahead mode"""
        # Old values
        name = "xref_address_mode"
        value = False
        self._write_control_register(name, value)

    def set_lookback(self):
        """Set look back mode"""
        name = "xref_address_mode"
        value = True
        self._write_control_register(name, value)

    def set_fast_rate(self):
        """Set sampling rate to 9.9Gsps.

        •"AF0C8050" Write Reg 12 x8050
        •"AF0D5777" Write Reg 13 x5777
        •"AF0EEO21" Write Reg 14 xE021
        •"AFOF8383" Write Reg 15 x8383
        •"AC130800" Set Reg 19 bit 11
        •"AB130800" Clear Reg 19 bit 11

        9.2Gsps (70Mhz)
        REG 0Chex cdce62002_register_1_msw_out 1104
        REG 0Dhex cdce62002_register_0_msw_out 21840
        REG OEhex cdce62002_register_1_lsw_out 41105
        REG OFhex cdce62002_register_1_msw_out 33677
        """
        # Old values
        reg_writes = {
            "cdce62002_register_0_lsw_out": 0x0450,
            "cdce62002_register_0_msw_out": 0x5550,
            "cdce62002_register_1_lsw_out": 0xA091,
            "cdce62002_register_1_msw_out": 0x838D,
        }

        for key, value in reg_writes.items():
            self._write_control_register(key, value)

        self._write_strobe()

    def set_slow_rate(self):
        """Set sampling rate to 3.0GSps (23.0MHz).

        • "AF0C1050" Write Reg 12 x1050
        • "AF0D5758" Write Reg 13 x5758
        • "AF0E8011" Write Reg 14 x8011
        • "AFOF8387" Write Reg 15 x8387
        • "AC130800" Set Reg 19 bit 11
        • "AB130800" Clear Reg 19 bit 11

        CHANGE TO
        3.0Gsps (23Mhz)
        REG 0Chex cdce62002_register_0_lsw_out 1104
        REG 0Dhex cdce62002_register_0_msw_out 22248
        REG OEhex cdce62002_register_1_lsw_out 40993
        REG OFhex cdce62002_register_1_msw_out 33666
        """
        reg_writes = {
            "cdce62002_register_0_lsw_out": 0x0450,
            "cdce62002_register_0_msw_out": 0x56E8,
            "cdce62002_register_1_lsw_out": 0xA021,
            "cdce62002_register_1_msw_out": 0x8382,
        }

        for key, value in reg_writes.items():
            self._write_control_register(key, value)

        self._write_strobe()

    def _write_strobe(self):
        """Write the changes and powercycles."""
        self._write_control_register("cdce62002_write_strobe", True)
        self._write_control_register("cdce62002_write_strobe", False)
        # This is normally true since it's _n and power should be up.
        self._write_control_register("cdce62002_power_down_n", False)
        self._write_control_register("cdce62002_power_down_n", True)

    def set_pd_bias_enabled(self, enabled: bool):
        """Set whether photodiode bias is enabled"""
        if enabled not in [0, 1]:
            raise TypeError("Enable flag must be a bool")
        self._write_control_register("pd_bias_en", enabled)

    def get_pd_bias_enabled(self) -> bool:
        """Get whether photodiode bias is enabled"""
        return bool(self.board.registers["control_registers"]["pd_bias_en"]["value"])

    def _write_control_register(self, register, value):
        """wrapper for the Control register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        Raises:
            ValueError, TypeError
        """
        ControlRegisters(self.board).write(register, value)  # pragma: no cover
