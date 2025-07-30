import logging
import time

from naludaq.backend import ConnectionManager
from naludaq.tools.data_collector.default import DataCollector

logger = logging.getLogger("naludaq.data_collector_udc16")

DEFAULT_TRIGGER_INTERVAL_LIMIT = 0.001


class Udc16DataCollector(DataCollector):
    """Data collector for the UDC16.

    This subclass is necessary for a few reasons:
    - Starting a readout is different for the UDC16
    - The UDC16 has no concept of a read window
    - The UDC16 needs to be reset when an event times out
    """

    def __init__(self, board, *args, **kwargs):
        super().__init__(board, *args, **kwargs)

        # UDC16/UPAC96 have an issue where the firmware locks up if the triggers
        # are sent too close together
        self.trigger_interval_limit = board.trigger.params.get(
            "trigger_interval_limit", DEFAULT_TRIGGER_INTERVAL_LIMIT
        )

    def _start_readout(self):
        logger.info("Starting readout")
        bc = self.board.control
        bc.clear_buffer()
        time.sleep(0.2)
        self._clear_connection_buffer()
        if self.board.model in ["upac96"]:
            bc.set_continuous_mode(True)
        bc.start_readout("software")

    def _restart_readout(self):
        self._stop_readout()
        time.sleep(0.1)
        self.board.control.digital_reset()
        self.board.control.digital_reset()
        time.sleep(0.1)
        self._start_readout()

    def _setup_readout(self):
        """Does nothing since UDC16 has nothing to configure"""

    def _event_failed(self):
        self._restart_readout()
        super()._event_failed()

    def _clear_connection_buffer(self):
        if self._board.using_new_backend:
            ConnectionManager(self.board).device.clear_buffers()
        else:
            self._board.connection.reset_input_buffer()
