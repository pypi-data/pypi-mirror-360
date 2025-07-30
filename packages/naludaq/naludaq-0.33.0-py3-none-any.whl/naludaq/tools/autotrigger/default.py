"""Tool for automatically sending software triggers over time.

See the class docstring for more details.

Author:
    Mitchell Matsumori-Kelly <mitchell@naluscientific.com>
"""
import logging
from typing import Callable

from naludaq.controllers import get_board_controller
from naludaq.helpers import type_name
from naludaq.helpers.exceptions import AutoTriggerError
from naludaq.models.acquisition import AcquisitionLike
from naludaq.tools.autoaction import AutoAction

logger = logging.getLogger("naludaq.tools.autotrigger_default")


class DefaultAutoTrigger(AutoAction):
    def __init__(self, board, interval: "float | Callable") -> None:
        """Default auto trigger module. Used to send software triggers at a consistent interval.

        There are three main ways this class can be used in:
        1. Through the `start()` method. This will start sending software triggers in a new thread, and must
        be stopped with the `stop()` method. This is best suited for situations when the exact
        number of triggers needed is unclear or unknown.
        2. Through the `send_triggers()` method. This will send an exact number of triggers. This is
        best suited for situations in which the exact amount of data required is known.
        3. Through the `send_triggers_until_amount_read()` method. This will send triggers until some number
        of additional events have been added to a buffer.

        This class is also a context manager. Use in this manner is equivalent to `start()` on entering
        the context and `stop()` upon leaving.
        """
        super().__init__(self._send_trigger, interval=interval)
        self._board = board

        # triggers can fire quickly, so keeping just one instance is faster
        self._board_controller = get_board_controller(board)
        self._trigger_count = 0

    @property
    def board(self):
        """Get the board object"""
        return self._board

    def send_triggers(self, num_triggers: int):
        """Send a given number of software triggers at the set interval.

        This function is blocking, and will only return once all triggers have been sent.

        Args:
            num_triggers (int): the number of triggers to send. Must be a positive integer.

        Raises:
            AutoTriggerError: if the autotrigger has been started in a different thread
                and is not yet stopped, or if the software triggers cannot be sent
        """
        if not isinstance(num_triggers, int):
            raise TypeError("Argument must be a positive int")
        if num_triggers <= 0:
            raise ValueError("Argument must be a positive int")
        if self._running:
            raise AutoTriggerError(
                "Autotrigger is already running from a different thread"
            )

        logger.info("Sending %s triggers...", num_triggers)
        self._trigger_count = 0
        self.stop_condition = (
            lambda: self._trigger_count >= num_triggers
        )  # >= for safety
        self.start(blocking=True)

    def send_triggers_until_amount_read(
        self,
        buffer: AcquisitionLike,
        amount: int,
        attempts: int = 5,
    ):
        """Send triggers until a buffer increases in size by a given amount. This function
        is blocking.

        This method is mainly useful for collecting a minimum number of events when used in
        combination with the output buffer from a daq.

        The initial contents of the buffer is ignored when determining how much data has been
        read back. This means you can call this method multiple times with the same output buffer
        and you will (ideally) get `amount` new events added each time.

        Args:
            buffer (AcquisitionLike): the buffer to monitor the size of. Should be the output buffer
                from a DAQ, otherwise using this method is pointless.
            amount (int): the minimum buffer size (number of events) desired.
            attempts (int): maximum number of times to continue sending software triggers when

        Raises:
            AutoTriggerError: if there was a problem sending software triggers, or if not enough data
                was collected in the given number of attempts.
        """
        self._validate_send_triggers_until_amount_read_args(buffer, amount, attempts)

        initial_amount = len(buffer)
        while len(buffer) - initial_amount < amount:
            buff_size_before_trigger = len(buffer)
            additional_amount_needed = amount - (len(buffer) - initial_amount)

            # Will raise an error if ZERO additional events have been read by the end of the loop
            for _ in range(attempts):
                try:
                    self.send_triggers(additional_amount_needed)
                except Exception as e:
                    raise AutoTriggerError("Failed to send software triggers") from e

                additional_amount_received = len(buffer) - buff_size_before_trigger
                if additional_amount_received != additional_amount_needed:
                    logger.warning(
                        "Sent %s triggers but received %s events",
                        additional_amount_needed,
                        additional_amount_received,
                    )
                if additional_amount_received > 0:
                    break
            else:
                raise AutoTriggerError(
                    f"Failed to collect the requested amount of data ({len(buffer)-initial_amount} / {amount})"
                )

    def _send_trigger(self):
        """Send a software trigger to the board."""
        self._trigger_count += 1
        try:
            self._board_controller.toggle_trigger()
        except Exception as e:
            raise AutoTriggerError("Failed to send software trigger") from e

    # ================================= VALIDATION =================================
    def _validate_send_triggers_until_amount_read_args(
        self,
        buffer: AcquisitionLike,
        amount: int,
        attempts: int,
    ):
        """Validate the arguments passed to `send_triggers_until_amount_read_args()`"""
        if not isinstance(buffer, AcquisitionLike):
            raise TypeError(f"Buffer must be Acquisition-like, not {type_name(buffer)}")
        if not isinstance(amount, int):
            raise TypeError(f"Amount must be an int, not {type_name(amount)}")
        if not isinstance(attempts, int):
            raise TypeError(f"Attempts must be positive, not {type_name(attempts)}")
        if amount <= 0:
            raise ValueError(f"Amount must be positive (got {amount})")
        if attempts <= 0:
            raise ValueError(f"Attempts must be positive (got {attempts})")
