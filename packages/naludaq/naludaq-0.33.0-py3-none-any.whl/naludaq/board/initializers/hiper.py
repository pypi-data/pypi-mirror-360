"""Initializer for the hiper board
"""
import logging
import time

from naludaq.controllers.board.hiper import BoardControllerHiper
from naludaq.helpers.decorators import log_function

from .aardvarcv3 import InitAardvarcv3

logger = logging.getLogger("naludaq.init_hiper")


class InitHiper(InitAardvarcv3):
    def __init__(self, board):
        """Initializer for the hiper board.

        Args:
            board (Board): the board to initialize.
        """
        super().__init__(board)

    def run(self) -> bool:
        """Runs the initialization sequence.

        Returns:
            True, always.
        """

        self._reset_digital()

        # Initialize FPGA registers
        self._fpga_init()
        self._i2c_startup()

        # Power on FMC board
        # self._power_toggle(False)
        # self._power_toggle(True)
        time.sleep(0.25)

        # Program the clock
        self._init_clock()

        # Select parallel interface
        magic_coms = [
            "AF040240",
            "AF040040",
            "AF040041",
            "AF040001",
        ]
        self.write_commands(magic_coms)
        time.sleep(0.1)
        # self._set_serial_mode(True)
        time.sleep(0.1)
        # self._set_loopback_enabled(False)
        chips = self.board.params.get("installed_chips", [])
        if len(chips) > 0:
            self._set_chips(chips=chips)
            time.sleep(0.1)
            self._set_txin()
            time.sleep(0.1)

            # Chip-side register startup
            BoardControllerHiper(self.board).analog_startup(chips=chips)
            BoardControllerHiper(self.board).digital_startup(chips=chips)

        if not self._sync_tx_pol():
            logger.error("tx idle detection missmatch")
        if not self._sync_rx_pol():
            logger.error("busy not locked.")

        # External devices
        self._init_dacs()

        return True

    def write_commands(self, commands):
        for cmd in commands:
            self.board.connection.send(cmd)
            time.sleep(0.01)

    def _reset_digital(self):
        """Reset digital side of the ASIC"""
        self.control_write("digrst", True)
        self.control_write("digrst", False)

    @log_function(logger)
    def _reset_sys(self):
        """Reset the ASIC and clear the analog and digital registers"""
        self.control_write("sysrst", True)
        self.control_write("sysrst", False)
        self.control_write("regclr", True)
        self.control_write("regclr", False)

    @log_function(logger)
    def _set_chips(self, chips):
        # chips = [x for x in range(14)]  # self.board.params.get("installed_chips", [])
        chips = sum(1 << chip for chip in chips)
        self.control_write("rxout_en", chips)

    @log_function(logger)
    def _set_txin(self):
        self.control_write("txin_en", False)

    def _sync_tx_pol(self):
        """Set ASIC txin polarity and check if locked

        SET POLARITY TO ASIC TXIN
        IF POLAROITY AND BAUD IS NOT CORRECT IDLE_DETECT WILL BE 0
        IF POLARITY AND BAUD ARE CORRECT IDLE_DETETCT WILL BE 1
        """
        chips = self.board.params.get("installed_chips", [])
        expected_sync = sum(1 << chip for chip in chips)
        for _ in range(5):
            if self.control_registers.read("idle_det")["value"] == expected_sync:
                return True
            time.sleep(0.05)
        return False

    def _sync_rx_pol(self):
        """Set ASIC rxout pol and make sure it's locked

        SET POLARITY TO ASIC RXOUT
        IF POLAROITY AND BAUD IS NOT CORRECT BUSY_LOCKED WILL BE 0
        IF POLARITY AND BAUD ARE CORRECT BUSY_LOCKED WILL BE 1
        """
        chips = self.board.params.get("installed_chips", [])
        expected_sync = sum(1 << chip for chip in chips)
        for _ in range(5):
            if self.control_registers.read("busy_locked")["value"] == expected_sync:
                return True
            time.sleep(0.05)
        return False

    @log_function(logger)
    def _set_loopback_enabled(self, enabled: bool):
        """Enable or disable loopback mode."""
        from naludaq.controllers import get_board_controller

        get_board_controller(self.board).set_loopback_enabled(enabled)
