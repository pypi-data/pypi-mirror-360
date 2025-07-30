import logging
import time
from typing import Iterable, Callable

from naludaq.controllers import get_board_controller, get_readout_controller
from naludaq.helpers import FancyIterator, validations
from naludaq.helpers.exceptions import BadDataError, DataCaptureError
from naludaq.helpers.helper_functions import event_transfer_time
from naludaq.tools.data_collector._daq_interface import get_daq_interface

logger = logging.getLogger("naludaq.data_collector")


class DataCollector:
    def __init__(
        self,
        board,
        channels: "list[int] | None" = None,
        trig: "str|None" = None,
        lb: "str|None" = None,
        acq: "str|None" = None,
        ped: "str|None" = None,
        readoutEn: "bool|None" = None,
        singleEv: "bool|None" = None,
        windows: "int|None" = None,
        lookback: "int|None" = None,
        write_after_trig: "int|None" = None,
    ):
        """Tool for easily collecting data from a board.

        This tool implements a simple interface for collecting data from a board
        without having to worry about the details of the readout configuration and DAQ.
        This tool also provides stability and robustness over a hand-wrangled readout
        solution.

        If the data collection succeeds, the following guarantees are made:
        - The events are all parsed and valid
        - The number of events is exactly the number of events requested
        - The events are in chronological order
        - The events are not duplicated

        Note that this tool does not preserve the state of the board before and after
        data collection. It is the responsibility of the user to ensure that the board
        state is restored if necessary.

        A DataCollector object may be reused as many times as desired, as long as only
        one collection is running at a time. The benefit of reusing a DataCollector
        is that the readout does not need to be reconfigured each time, and the
        timeout starts off better-tuned on subsequent collections.

        The data collector is modeled after Rust's iterators. Operations may be chained
        sequentially to build up a pipeline of operations to perform on the data. The
        pipeline is executed when the final `collect()` function is called.

        Example usage:

        .. code-block:: python

            collector = DataCollector(board)
            collector
                .iter(attempts=3)                 # 1. create a new iterator
                .enumerate()                      # 2. add an index to each event
                .filter(lambda x: x[0] % 2 == 0)  # 3. filter out odd-numbered events
                .unenumerate()                    # 4. remove the index so we're left with events only
                .take(10)                         # 5. only take the first 10 odd-numbered events (1, 3, .., 21)
                .collect()                        # 6. execute the pipeline

        Properties:
            board: Board object
            readout_settings: dictionary of readout settings to use
            window_settings: the window of the sampling array to read
            forced: whether the readout is in forced mode or not
            channels: list of channels to read
            error_count: number of errors encountered during data collection, read-only
            max_errors: maximum number of errors allowed before stopping data collection, can be None

        Args:
            board: Board object
            channels (Iterable[int]): list of channels to read, defaults to all channels
            trig (str): trigger mode, defaults to "ext"
            lb (str): lookback mode, defaults to "trigrel"
            acq (str): acquisition mode, defaults to "raw"
            ped (str): pedestal mode, defaults to "zero"
            readoutEn (bool): whether to enable readout, defaults to True
            singleEv (bool): whether to enable single event readout, defaults to False
            windows (int): number of windows to read, defaults to 8
            lookback (int): number of lookback windows, defaults to 8
            write_after_trig (int): number of windows to write after trigger, defaults to 8
        """
        self._board = board
        self.channels = channels or range(board.channels)
        self.readout_settings = {
            "trig": trig or "ext",
            "lb": lb or "trigrel",
            "acq": acq or "raw",
            "ped": ped or "zero",
            "readoutEn": readoutEn or True,
            "singleEv": singleEv or False,
        }
        self._window_settings = {
            "windows": 8,
            "lookback": 8,
            "write_after_trig": 8,
        }
        self.set_window(windows, lookback, write_after_trig)
        self.trigger_fn = None
        self._single_event_timeout = 0
        self._margin = 2
        self._trigger_limit = 0.01
        self._last_trigger_time = None
        self.timeout_overhead = self.board.params.get("timeout_overhead", 10.0)
        self._error_count = 0
        self._max_errors = None

    @property
    def max_errors(self) -> int:
        """Get/set the maximum number of attempts to capture an event"""
        return self._max_errors

    @max_errors.setter
    def max_errors(self, value: int | None):
        if value is not None:
            validations.validate_positive_int_or_raise(value)
        self._max_errors = value

    @property
    def error_count(self) -> int:
        """Get the number of errors encountered during data collection"""
        return self._error_count

    @property
    def board(self):
        """Get the board object used by the data collector"""
        return self._board

    @property
    def readout_settings(self) -> dict:
        """Get/set the readout settings dictionary.

        This dictionary contains the following keys, which correspond to the
        start_readout() function in the board controller:
            "trig"
            "lb"
            "acq"
            "ped"
            "readoutEn"
            "singleEv"
        """
        return self._readout_settings

    @readout_settings.setter
    def readout_settings(self, settings: dict):
        validations.validate_readout_settings(settings)
        self._readout_settings = settings.copy()

    @property
    def window_settings(self) -> dict:
        """Get the window settings dictionary.

        This dictionary contains the following keys:
            "windows"
            "lookback"
            "write_after_trig"
        """
        return self._window_settings

    @property
    def channels(self) -> list[int]:
        """Get/set the channels to read"""
        return self._channels

    @channels.setter
    def channels(self, channels: Iterable[int]):
        validations.validate_channel_sequence_or_raise(self.board.params, channels)
        self._channels = list(channels)

    @property
    def forced(self) -> bool:
        """Get/set whether the readout is in forced mode or not"""
        return self._readout_settings["lb"].lower().startswith("f")

    @forced.setter
    def forced(self, forced: bool):
        if not isinstance(forced, bool):
            raise TypeError("Value must be a boolean")
        if forced:
            self._readout_settings["lb"] = "forced"
        else:
            self._readout_settings["lb"] = "trigrel"

    @property
    def trigger_interval_limit(self) -> float:
        """Get/set the trigger interval limit in seconds.

        This is the minimum time between consecutive triggers.
        Note that this increases the calculated event timeout
        by the same amount to account for dead time.

        Some boards don't like it when you send triggers really
        fast, so this is a way to prevent that.
        """
        return self._trigger_limit

    @trigger_interval_limit.setter
    def trigger_interval_limit(self, limit: float):
        if not isinstance(limit, float):
            raise TypeError("Value must be a float")
        if limit < 0:
            raise ValueError("Value must be non-negative")
        self._trigger_limit = limit

    @property
    def trigger_frequency_limit(self) -> float:
        """Same thing as self.trigger_interval_limit, but in Hz."""
        return 1 / self._trigger_limit

    @trigger_frequency_limit.setter
    def trigger_frequency_limit(self, limit: float):
        if limit == 0:
            raise ValueError("Zero frequency not allowed")
        self.trigger_interval_limit = 1 / limit

    @property
    def trigger_fn(self) -> Callable:
        """Get/set the trigger callback function.

        Settings this function allows the user to inject custom logic
        into the data capture code.
        """
        return self._trigger_fn

    @trigger_fn.setter
    def trigger_fn(self, fn: Callable):
        if fn is None:
            fn = self._board.control.toggle_trigger
        validations.validate_callable_or_raise(fn)
        self._trigger_fn = fn

    @property
    def timeout_overhead(self) -> float:
        """Get/set the timeout offset in seconds.

        This is the amount of time added to the event timeout.
        """
        return self._overhead

    @timeout_overhead.setter
    def timeout_overhead(self, value: float):
        if value < 0:
            raise ValueError("Value must be non-negative")
        self._overhead = value
        self._recompute_timeout()

    def set_window(
        self, windows: int = None, lookback: int = None, write_after_trig: int = None
    ):
        """Set the read window.

        Args:
            windows (int): number of windows to read for each event
            lookback (int): number of windows to look back after writing "write_after_trig" windows
            write_after_trig (int): number of windows to write after the trigger
        """
        if windows is not None:
            self._window_settings["windows"] = windows
        if lookback is not None:
            self._window_settings["lookback"] = lookback
        if write_after_trig is not None:
            self._window_settings["write_after_trig"] = write_after_trig

    def set_self_trigger(self):
        """Sets trigger to self mode"""
        self._readout_settings["trig"] = "self"

    def set_external_trigger(self):
        """Sets trigger to external mode"""
        self._readout_settings["trig"] = "ext"

    def set_immediate_trigger(self):
        """Sets trigger to immediate mode"""
        self._readout_settings["trig"] = "immediate"

    def iter(self, count: int, attempts: int = 3) -> FancyIterator:
        """Create a bounded iterator of valid events.

        The iterator lazily generates events, and is a FancyIterator
        so it can be used as a data pipeline.

        It is encouraged to use this method instead of `iter_inf()` where
        possible to avoid collecting data forever.

        When any one event takes more than `attempts` attempts to capture,
        a TimeoutError is raised. The attempt counter is reset on success.

        Example:

        .. code-block:: python

            collector = DataCollector(board)
            collector
                .iter(10)
                .collect()

        Args:
            count (int): maximum number of events to read
            attempts (int): number of attempts to get an event

        Returns:
            FancyIterator: an iterator over events
        """
        return self.iter_inf(attempts).take(count)

    def iter_inf(self, attempts: int = 3) -> FancyIterator:
        """Create an infinite iterator of valid events.

        The iterator lazily generates events, and is a FancyIterator
        so it can be used as a data pipeline.

        When any one event takes more than `attempts` attempts to capture,
        a TimeoutError is raised. The attempt counter is reset on success.

        Example:

        .. code-block:: python

            collector = DataCollector(board)
            collector
                .iter_inf()
                .take(10)
                .collect()

        Args:
            attempts (int): number of attempts to get an event

        Returns:
            FancyIterator: an iterator over valid events
        """
        return FancyIterator(self._iter_inner(attempts))

    def _iter_inner(self, attempts=3):
        """A generator of single events.

        This method lazily generates events. If any one event takes more
        than `attempts` attempts to capture, a TimeoutError is raised.
        The attempt counter is reset on success.

        The timeout per event is increased on each failure to capture an event.
        This is to account for real-world factors which may make the initial
        timeout computation unrealistically short.

        Args:
            attempts (int): number of attempts to get an event
        """
        validations.validate_positive_int_or_raise(attempts)
        validations.validate_readout_settings(self._readout_settings)

        # the number of channels may have changed, need to recompute
        # (the timeout margin isn't affected by this)
        self._recompute_timeout()
        self._setup_readout()
        self._start_readout()
        self._last_trigger_time = 0
        try:
            for event in self._capture_with_attempts(attempts):
                yield event
        finally:
            self._stop_readout()

    def _capture_with_attempts(self, attempts: int) -> Iterable[dict]:
        """Attempts to capture events until the attempt counter is reached.

        This method lazily generates events. If any one event takes more
        than `attempts` attempts to capture, a TimeoutError is raised.
        The attempt counter is reset on success.

        The timeout per event is increased on each failure to capture an event.
        This is to account for real-world factors which may make the initial
        timeout computation unrealistically short.

        Raises:
            TimeoutError: if the attempt counter is reached for an event
        """
        attempt_count = 0
        interface = get_daq_interface(self._board)
        interface.start_capture()
        try:
            while True:
                self._toggle_trigger()
                try:
                    for event in interface.stream(self._single_event_timeout):
                        yield event
                        self._error_count += attempt_count
                        attempt_count = 0
                        self._toggle_trigger()
                except TimeoutError:
                    logger.warning("Capture failed, increasing sleep time")
                    self._event_failed()
                    attempt_count += 1
                except BadDataError:
                    logger.warning("Bad event received, ignoring")
                    attempt_count += 1
                if attempt_count >= attempts:
                    self._error_count += attempt_count
                    raise TimeoutError(
                        f"Failed to capture event after {attempts} attempts, total attempts: {self._error_count}"
                    )
                if (
                    self._max_errors is not None
                    and self._error_count >= self._max_errors
                ):
                    raise DataCaptureError(
                        f"Maximum number of bad events reached: {self._error_count}"
                    )
        finally:
            interface.stop_capture()

    # ================================================================================
    # Readout
    # ================================================================================
    def _start_readout(self):
        """Start a readout"""
        logger.info("Starting readout using: %s", self._readout_settings)
        get_board_controller(self._board).start_readout(**self._readout_settings)

    def _stop_readout(self):
        """Stop the readout"""
        logger.info("Stopping readout")
        get_board_controller(self._board).stop_readout()

    def _setup_readout(self):
        """Set up the readout"""
        rc = get_readout_controller(self.board)
        rc.set_readout_channels(self.channels)
        rc.set_read_window(**self._window_settings)

    def _toggle_trigger(self):
        """Toggle the trigger.

        Includes a `time.sleep` to enforce the trigger interval limit.
        """
        if self.readout_settings["trig"].lower().startswith(("i", "s")):
            return

        now = time.perf_counter()
        delta = now - self._last_trigger_time
        if delta < self._trigger_limit:
            time.sleep(self._trigger_limit - delta)
        self._last_trigger_time = now
        self._trigger_fn()

    # ================================================================================
    # Timeout
    # ================================================================================
    def _event_failed(self):
        """Callback for when an event capture times out.

        Subclasses may override this method to implement custom behavior.
        It is highly recommended to call the super method, as it handles
        increasing the timeout.
        """
        self._increase_timeout()

    def _recompute_timeout(self):
        """Recompute the event timeout attribute based on the current settings."""
        self._single_event_timeout = event_transfer_time(
            self._board,
            windows=self.window_settings["windows"],
            channels=len(self._channels),
            margin=self._margin,
            overhead=self._overhead,
        )
        logger.debug("Timeout changed to %s", self._single_event_timeout)

    def _increase_timeout(self, current_amount=0, needed_amount=1):
        """Increase the timeout based on received vs expected.

        Formula is intended to change the margin incrementally without
        causing to much oscillation.
        """
        # Settles at 0.38
        factor = ((needed_amount - current_amount) / needed_amount) / 3 + 1
        self._margin = min(self._margin * factor, 10)
        self._recompute_timeout()
