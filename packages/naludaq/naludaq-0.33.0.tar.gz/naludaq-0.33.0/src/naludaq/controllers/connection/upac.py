"""

"""
import time
from logging import getLogger

from naludaq.backend.managers.connection import ConnectionManager
from naludaq.communication.control_registers import ControlRegisters

from . import ConnectionController

LOGGER = getLogger(__name__)


class UPACConnectionController(ConnectionController):
    """Connection controller for UPAC boards

    Uses a different command to change speed in UART connections
    """

    def change_speed(self, sync_int, rate, divider, sync_addr=0x00):
        """
        Attempts to change the baudrate!

        Divider sets it so: (25MHz clock / 16clks/bit)/(divider+1) = baudrate

        NOTE: It is a 100MHz clock now, so the math changes accordingly
          Also it looks like the baud gets quantized on the CPU side at higher rates, so keep that in mind

        Command is DDDDVVVV where V is the divider value (max 256)

        Args:
            sync_int (int): expected integer return when syncing with the board.
            rate (int): valid baudrate
            divider (int): baud divider
        """
        if self.board.using_new_backend:
            return self._change_speed_new(rate, divider)
        if not self.board.connection.is_uart():
            raise ConnectionError

        ControlRegisters(self.board).write("baud_rate_divisor", divider)
        time.sleep(
            0.1
        )  # Important, without wait the baord gets stuck on the next command
        self.board.connection.baud = rate

        # Resyncing the connection.
        for _ in range(3):
            if self.board.connection.resync(sync_int, sync_addr):
                LOGGER.debug(
                    "Baudrate synced successfully, divider: %s, baud: %s", divider, rate
                )
                break
        else:
            LOGGER.debug("Sync failed.")

    def _change_speed_new(self, rate, divider):
        """
        Attempts to change the baudrate!

        Divider sets it so: (25MHz clock / 16clks/bit)/(divider+1) = baudrate

        NOTE: It is a 100MHz clock now, so the math changes accordingly
          Also it looks like the baud gets quantized on the CPU side at higher rates, so keep that in mind

        Command is DDDDVVVV where V is the divider value (max 256)

        Args:
            sync_int (int): expected integer return when syncing with the board.
            rate (int): valid baudrate
            divider (int): baud divider
        """
        self._validate_connection_or_raise()
        ControlRegisters(self.board).write("baud_rate_divisor", divider)
        # Important, without wait the baord gets stuck on the next command
        time.sleep(0.1)
        ConnectionManager(self.board).device.baud_rate = rate

        # Resyncing the connection.
        for _ in range(3):
            if self._resync_new():
                LOGGER.debug(
                    "Baudrate synced successfully, divider: %s, baud: %s", divider, rate
                )
                break
        else:
            LOGGER.debug("Sync failed.")
