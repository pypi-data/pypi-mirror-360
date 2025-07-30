"""
"""
import time
from logging import getLogger

from naludaq.backend.managers.connection import ConnectionManager
from naludaq.backend.managers.io import BoardIoManager
from naludaq.backend.models.device import DeviceType
from naludaq.communication import ControlRegisters
from naludaq.controllers.controller import Controller

LOGGER = getLogger("naludaq.board_controller_udc")
NON_UDP = [DeviceType.SERIAL, DeviceType.D2XX, DeviceType.D3XX]


class UDCBoardController(Controller):
    """Board cotnroller for the specific UDC functionality.

    The UDC board reads out all data, every time.
    It has so far very limited readout modes.

    """

    def __init__(self, board):
        super().__init__(board)
        self._write_pause = 0.01

    def start_readout(
        self,
        trigger_type="self",
    ):
        """Sends a readout signal to the board.

        Obstensibly reads out the chip?

        Args:
            trigger_type (str):
                "There are 4 trigger modes:

                '00'	: 	Software Trigger Mode, the power on default.
                '01'	: 	Auto Trigger Mode. 1-2Hz auto trigger data rate.
                '10'	:	External Trigger Mode.
                '11'	: 	Self Trigger Mode.

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
        self.is_reading_out = True
        self._enable_rx_tx(False)
        self.sysrst(regclr=False)
        self.digital_reset()

        # # wave fifo reset
        self._clear_fpga_buffer()
        self._enable_rx_tx(True)

    def toggle_trigger(self):
        """Toggles the software trigger bit, should result in a software trigger event."""
        LOGGER.debug("Toggle software trigger")
        self._enable_rx_tx(False)
        self.sysrst(regclr=False)
        self.digital_reset()

        # # wave fifo reset
        self._clear_fpga_buffer()
        self._enable_rx_tx(True)
        self.arm()
        cmd = "C0000064"  # Send software trigger
        self._send_command(cmd)
        self.toggle_reread()

    def arm(self):
        """Arms the system by toggling the "udc_arm" register"""
        self._write_control_register("udc_arm", True)
        self._write_control_register("udc_arm", False)

    def toggle_reread(self):
        """"""
        self._write_control_register("reread_data", True)
        self._write_control_register("reread_data", False)

    def reset_board(self):
        """Try and reset the board.

        In case the FPGA get stuck this can help reset the state.
        """
        time.sleep(0.02)
        self.digital_reset()
        time.sleep(0.02)
        self.sysrst()

    def digital_reset(self):
        """Toggles the "reset" port on the readout module.

        Forcibly returns the chip to default state.
        """
        self._write_control_register("digrst", True)
        self._write_control_register("digrst", False)

    def clear_buffer(self):
        """Clears the UART buffer on both CPU and FPGA side."""
        try:
            self._clear_fpga_buffer()
        except Exception:
            pass

        try:
            self._clear_input_buffer()
        except Exception:
            pass

    def _clear_fpga_buffer(self):
        self._write_control_register("wave_fifo_reset", True)
        self._write_control_register("wave_fifo_reset", False)

    def _clear_input_buffer(self):
        if self.board.using_new_backend:
            device = ConnectionManager(self.board).device
            if device.type in NON_UDP:
                device.clear_buffers()
        else:
            self.board.connection.reset_input_buffer()

    def sysrst(self, regclr: bool = True):
        """Toggles the sysrst pin, which resets the digital portion of the chip

        Args:
            regclr (bool): whether to toggle the 'regclr' register.
        """
        self._write_control_register("sysrst", True)
        regclr and self._write_control_register("regclr", True)
        self._write_control_register("sysrst", False)
        regclr and self._write_control_register("regclr", False)

    def _enable_rx_tx(self, en: bool):
        """Turns on or off serial interface Rx and Tx.

        Args:
            en (bool): whether to enable Rx and Tx.
        """
        self._write_control_register("rx_enable", en)
        self._write_control_register("tx_enable", en)

    #############################################################################
    # Random Stuff, may or maynot work... Below functions need to be validated.
    #############################################################################

    def read_scalers(self, channels: list[int] = None):
        """Not implemented."""
        # self.stop_readout()
        scalers = []

        return scalers

    def enable_testmode(self, enabled: bool):
        """Enables the test-pattern output.

        Set the fpga in a mode to output a known test-pattern.
        """
        # ControlRegisters(self.board).write("fake", enabled)

    def get_available_chips(self) -> list[int]:
        """Get a list of available chip numbers."""
        return list(range(self.board.params.get("num_chips", 1)))

    def _write_control_register(self, register, value):
        """wrapper for the Control register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        try:
            ControlRegisters(self.board).write(register, value)
            time.sleep(self._write_pause)
        except (ValueError, TypeError) as error_msg:
            LOGGER.error("Couldn't update control register due to: %s", error_msg)

    def _send_command(self, command):
        """Send the given hex command to the board.

        Args:
            command (str): hex command
        """
        if self.board.using_new_backend:
            BoardIoManager(self.board).write(command)
        else:
            self.board.connection.send(command)
