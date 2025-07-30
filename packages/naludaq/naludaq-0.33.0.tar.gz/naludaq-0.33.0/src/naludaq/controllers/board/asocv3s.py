""" Board controller for the ASoCv3s

This board has a few differences, the stop acq needs to send a proper stop acq command.

"""
import time
from logging import getLogger

from naludaq.communication.control_registers import ControlRegisters

from .default import BoardController

LOGGER = getLogger("naludaq.board_controller_asocv3s")


class ASoCv3SBoardController(BoardController):
    def start_readout(
        self,
        trig: str = "self",
        lb: str = "trigrel",
        acq: str = "raw",
        dig_head: bool = False,
        ped: str = "zero",
        readoutEn: bool = True,
        singleEv: bool = False,
    ):
        """Sends a readout signal to the board.

        Obstensibly reads out the chip?

        Args:
            trigger_type (str):
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
        self.serial_to_parallel_conv(True)

        super().start_readout(
            trig,
            lb,
            acq,
            dig_head,
            ped,
            readoutEn,
            singleEv,
        )

    def serial_to_parallel_conv(self, enabled: bool):
        """Enabled/Disable serial to parallel conversion

        This conversion is used to enabled a 16-bit padded output
        instead of the 12-bit raw output.

        The parser requires this to be enabled.
        Register reads require this to be disabled.
        """

        ControlRegisters(self.board).write("ser2par_en", enabled)

    def stop_readout(self):
        """Toggles the "stopacq" signal on the readout module.

        It's equivalent of asking it nicely to stop reading.
        """
        self.is_reading_out = False
        cmd = "B0B00000"
        self._send_command(cmd)
        time.sleep(0.1)
        self.serial_to_parallel_conv(False)

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
