"""
"""
from logging import getLogger

from naludaq.communication import ControlRegisters, DigitalRegisters

from .default import BoardController

LOGGER = getLogger("naludaq.board_controller_trbhm")


class TrbhmBoardController(BoardController):
    """Special board controller for TRBHM."""

    def start_readout(
        self,
        trig="self",
        lb="trigrel",
        acq="raw",
        dig_head=False,
        ped="zero",
        readoutEn=True,
        singleEv=False,
    ):
        """Sends a readout signal to the board.

        Obstensibly reads out the chip?

        Args:
            trig (str):
                'immediate', '00' - digitize whatever instantly as fast as possible.
                'ext': '01' - use the external trigger.
                'self': '10' - trigger on input RF signal.
            lbType (str):
                'forced': '00' - always reads out same set of windows, start window set by lookback
                'trig': '01' - relative to the trigger.
                'roi': '10' - complicated...
            acq_type (str):
                'raw': '00' - Can't ped-subtract. <Default output>
                'ped': '01' - sub, spits out headers, channels, and windows. <Requires firmware modification>
            dig_head (bool):
                True: reads out a "digitization" header after each sram read (only works with acq_type="ped")
                False: doesn't read out that header
            pedMode (str):
                'z': '00' - all peds = 0
                'c': '01' - peds = chan*1024, set offset per channel
                'r': '11' - peds = RAM addr
            readoutEn (bool): Enables readout to ethernet (otherwise data thrown away)
                self.readReadoutRate() is the companion to this to see the true rate
                readout rate scalar stored in FPGA reg N_GPR(32) + 5
            singleEV (bool): True - only reads one event.

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
        readout_params = self._validate_readout_params(
            trig, lb, acq, dig_head, ped, readoutEn, singleEv
        )

        ControlRegisters(self.board).write("exttrig", True)
        readout_params["trig"] = "ext"
        if trig[0] == "e":  # ext
            trig_sel = 0b00
        elif trig[0] == "s":  # self
            trig_sel = 0b01
        else:  # imm
            trig_sel = 0b10
        ControlRegisters(self.board).write("trig_sel", trig_sel)

        ControlRegisters(self.board).write("fifo_unload_or_event_en", True)

        cmd = self._generate_start_readout_cmd(readout_params)
        LOGGER.debug("READOUT command: %s", cmd)

        self._send_command(cmd)
        self.is_reading_out = True

    def stop_readout(self):
        super().stop_readout()
        ControlRegisters(self.board).write("fifo_unload_or_event_en", False)

    def read_scalar(self, channel: int) -> int:
        """Read the scalar for the given channel"""
        channels_per_chip = self.board.channels // self.board.available_chips
        relative_channel = channel % channels_per_chip
        chip = channel // channels_per_chip
        return self._read_scalar_inner(chip, relative_channel)

    def _read_scalar_inner(self, chip: int, relative_channel: int) -> int:
        """Read the scalar for the given channel.

        This is the inner function that actually reads the scalar.
        It is called by `read_scalar` and should not be called directly.
        """
        name = self.get_scal_name(relative_channel)
        scal = self._read_digital_register(name, chips=chip)
        try:
            scalhigh = self._read_digital_register("scalhigh", chips=chip)
        except (KeyError, AttributeError):
            scalhigh = 0
        shift_amt = DigitalRegisters(self.board).registers[name]["bitwidth"]
        scal += scalhigh << shift_amt

        return scal

    # def _toggle_trigger(self):
    #     """Toggles the ext trigger using software.

    #     For TRBHM the wait between separate register writes is too long, and
    #     toggling the trigger too slowly results in too many events coming back
    #     and filling the FIFO, causing malformed events. This method instead
    #     sends the register writes all as one string.
    #     """
    #     cr = ControlRegisters(self.board)

    #     wait_cmd = "AE000001"
    #     exttrig_high_cmd = cr.generate_write("exttrig", True)
    #     exttrig_low_cmd = cr.generate_write("exttrig", False)
    #     toggle_cmd = wait_cmd + exttrig_high_cmd + exttrig_low_cmd
    #     self._send_command(toggle_cmd)

    def set_loopback_enabled(self, enabled: bool):
        """Set whether serial loopback is enabled.

        Loopback can safely be disabled during most of the operations with the board.
        Loopback **must** be disabled when communicating over the serial interface.
        If serial communication with the ASIC is intended then this should run during startup and only be enabled as needed.

        Args:
            enabled (bool): True to enable loopback.

        Raises:
            TypeError if enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise TypeError("Argument must be bool")
        OFF = "B0900002"
        ON = "B0900003"
        cmd = ON if enabled else OFF
        self._send_command(cmd)
