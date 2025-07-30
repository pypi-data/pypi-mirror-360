"""Tool for waiting for events to fill a buffer to a specified amount

Author:
    Alvin Yang
    Mitchell Matsumori-Kelly <mitchell@naluscientific.com>
"""
import logging
import time
from typing import Callable

from naludaq.tools.autoaction import AutoAction

logger = logging.getLogger("naludaq.tools.eventwaiter")


class EventWaiter(AutoAction):
    def __init__(
        self,
        buffer,
        amount,
        interval: "float | Callable" = 0.1,
        timeout: float = 1.0,
        reset_timeout=False,
    ) -> None:
        """Module for waiting for when a buffer (events) is filled to a specified amount

        Args:
            buffer: A list like object that stores events
            amount (int): Desired amount of events for the buffer to be filled, before waiter stops
            interval (float): Time (s) between each buffer check
            timeout (float): Time (s) before the waiter stops
            reset_timeout (bool): Whether to reset timeout counter when len of buffer is changed
        """
        self.buffer = buffer
        self.amount = amount
        self.timeout = timeout
        self.reset_timeout = reset_timeout
        super().__init__(self._actioner, self._stopper, interval=interval)

    def _actioner(self):
        if len(self.buffer) > self._curr_len and self.reset_timeout:
            self._curr_len = len(self.buffer)
            self._start_time = time.time()

    def _stopper(self):
        if len(self.buffer) >= self.amount:
            return True
        time_passed = time.time() - self._start_time
        if time_passed > self.timeout:
            raise TimeoutError("Waited too long for an event")
        return False

    def start(self, blocking=True):
        """Starts calling the action periodically from a new thread.

        Args:
            blocking (bool): whether to block until the stop condition is met
                or the `stop()` method is called.
        """
        self._start_time = time.time()
        self._curr_len = len(self.buffer)
        super().start(blocking=blocking)
