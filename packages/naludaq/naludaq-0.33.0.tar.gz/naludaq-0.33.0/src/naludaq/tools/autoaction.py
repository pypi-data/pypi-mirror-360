"""Tool for automatically sending software triggers over time.

See the class docstring for more details.

Author:
    Mitchell Matsumori-Kelly <mitchell@naluscientific.com>
"""
import logging
import sched
import sys
import time
from contextlib import AbstractContextManager
from threading import Thread
from typing import Callable

from naludaq.helpers.exceptions import AutoActionError

logger = logging.getLogger("naludaq.tools.autotrigger_default")
_default_stop_condition = lambda: False


class AutoAction(AbstractContextManager):
    def __init__(
        self,
        action: Callable,
        stop_condition: Callable = _default_stop_condition,
        interval: float = 1,
    ):
        """Create a new AutoAction object.

        Args:
            action (Callable): a function (or function-like) object to call periodically
            stop_condition (Callable): a function (or function-like) object which this class
                will call to determine whether a stop condition has been met, at which point
                the class will stop calling the `action`. The signature must be: `() -> bool`,
                returning `True` to stop or `False` to continue. If not provided, the
                stop condition will never be met and the class must be stopped manually.
                NOTE: the stop condition is called *before* each action call
            interval (float): the interval at which to call the `action` in seconds.
        """
        self.action = action
        self.stop_condition = stop_condition
        self.interval = interval

        self._running = False
        self._thread = None
        self._scheduler = None
        self._exception = None

        self._time_fn = time.monotonic
        self._delay_fn = time.sleep

    @property
    def action(self):
        """Get the board object"""
        return self._action

    @action.setter
    def action(self, action: Callable):
        if not callable(action):
            raise TypeError("Action must be callable")
        self._action = action

    @property
    def stop_condition(self) -> Callable:
        """Get/set the stop condition function, used to progammatically
        determine when to stop action-ing.

        The function must take no arguments, and return a `bool`
        indicating whether to stop.
        """
        return self._stop_condition

    @stop_condition.setter
    def stop_condition(self, stop_condition: Callable):
        if not callable(stop_condition):
            raise TypeError("Stop condition must be callable")
        self._stop_condition = stop_condition

    @property
    def interval(self) -> float:
        return self._interval

    @interval.setter
    def interval(self, interval: float):
        if not isinstance(interval, (int, float)):
            raise TypeError("Interval must be numeric")
        if interval <= 0:
            raise ValueError("Interval must be positive")
        self._interval = interval

    @property
    def is_running(self) -> bool:
        """Check if currently running"""
        return self._running

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_args):
        self.stop()

    def start(self, blocking=True):
        """Starts calling the action periodically from a new thread.

        Args:
            blocking (bool): whether to block until the stop condition is met
                or the `stop()` method is called.
        """
        if self._running:
            raise AutoActionError("Already running")

        # scheduler used to periodically call action
        self._scheduler = self._make_scheduler()
        self._schedule_action(self._time_fn())  # initial action, occurs immediately

        self._running = True
        self._thread = Thread(target=self._scheduler.run, daemon=True)
        self._thread.start()
        if blocking:
            self._thread.join()
            self._running = False
            self._reraise_last_error()

    def stop(self):
        """Tells the autoaction module to cease scheduling new actions.

        This method blocks until the scheduler is complete.
        """
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._reraise_last_error()

    def _reraise_last_error(self):
        """Reraise any error caught in the scheduler thread.

        Resets the stored exception, so this method will not raise an error
        on subsequent calls.
        """
        if self._exception is not None:
            self._exception, e = None, self._exception  # reset exception
            raise e

    def _call_action(self) -> bool:
        try:
            self._action()
        except Exception as e:
            self._store_error_and_abort(e)

    def _should_continue(self) -> bool:
        """Check whether the autoaction should schedule the next action.

        Returns:
            bool: True if running and the stop condition is not met
        """
        try:
            return self._running and not self.stop_condition()
        except Exception as e:
            self._store_error_and_abort(e)

    def _store_error_and_abort(self, exc: Exception):
        """Store an exception and immediately stop the scheduler thread.
        This method should only be called from the scheduler thread.
        """
        self._exception = exc
        self._running = False
        sys.exit()  # immediately exit the thread

    # ================================= SCHEDULING =================================
    def _scheduler_callback(self, scheduled_time: float):
        """Calls the user action callback and schedules the next action, if any.

        This method is called periodically by the scheduler and should not be
        called directly.

        Args:
            scheduled_time (float): the time that *this* event was scheduled for.
                The next action is scheduled to occur some amount of time after
                this value.
        """
        if self._should_continue():
            self._call_action()

            next_time = self._get_next_action_time(scheduled_time)
            self._schedule_action(next_time)

    def _make_scheduler(self) -> sched.scheduler:
        """Make a scheduler and schedule the first trigger event.

        Args:
            check_continue (callable): a function that takes no arguments and returns a bool indicating
                whether or not to continue sending triggers.

        Returns:
            sched.scheduler: the new scheduler object
        """
        return sched.scheduler(timefunc=self._time_fn, delayfunc=self._delay_fn)

    def _schedule_action(self, scheduled_time: float):
        """Schedule a new trigger event to occur at the given time.

        Args:
            scheduled_time (float): the time at which the next action should occur.
                Units are in seconds, and the point of reference depends on
                the time function used in the constructor.
        """
        self._scheduler.enterabs(
            time=scheduled_time,
            priority=0,  # priority doesn't matter here
            action=self._scheduler_callback,
            argument=(scheduled_time,),
        )

    def _get_next_action_time(self, current_time: float = None) -> float:
        """Get the time that the next action should be scheduled for.

        Args:
            current_time (float): the time of the current action. If not provided,
                the value is assumed from the time function.
        """
        return (current_time or self._time_fn()) + self._interval
