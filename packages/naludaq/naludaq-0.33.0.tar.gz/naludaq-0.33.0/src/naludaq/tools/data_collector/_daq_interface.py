import abc
import typing
from collections import deque

from naludaq.backend import AcquisitionManager
from naludaq.daq import get_daq
from naludaq.helpers.exceptions import BadDataError
from naludaq.tools.waiter import EventWaiter


class DaqInterface(abc.ABC):
    def __init__(self, board: str):
        """Interface combining the old and new DAQ."""
        self._board = board

    @abc.abstractmethod
    def start_capture(self):
        """Start the data capture.

        Must be called before using stream()
        """

    @abc.abstractmethod
    def stop_capture(self):
        """Stop the data capture"""

    @abc.abstractmethod
    def stream(self, timeout: float) -> typing.Iterable[dict]:
        """Generator for valid events.

        This generator will continually yield valid events until
        the timeout is reached or the first invalid event is captured.

        The start_capture() method must be called before using this method.

        Args:
            timeout (float): timeout in seconds for each event.
                The timeout is reset for each event.

        Raises:
            TimeoutError: if no events are captured within the timeout
            BadDataError: if an invalid event is captured
        """


def get_daq_interface(board: str) -> DaqInterface:
    """Internal method for getting the correct DAQ interface.

    The DAQ interface allows an abstraction around the two DAQs which allows
    the user to be DAQ-agnostic until the old DAQ is sunset.
    """
    if board.using_new_backend:
        return NewDaqInterface(board)
    return OldDaqInterface(board)


class OldDaqInterface(DaqInterface):
    def __init__(self, board: str):
        super().__init__(board)
        self._output_buffer = deque()

        self._daq = get_daq(board, parsed=True)
        self._daq.output_buffer = self._output_buffer

    def start_capture(self):
        self._daq.start_capture()

    def stop_capture(self):
        self._daq.stop_capture()

    def stream(self, timeout: float) -> typing.Iterable[dict]:
        while True:
            # It's possible more than one event is in the buffer,
            # in which case we don't need to wait.
            if self._output_buffer:
                event = self._output_buffer.popleft()
                if "data" not in event:
                    raise BadDataError("Invalid event captured")
                yield event
                continue
            waiter = EventWaiter(self._output_buffer, 1, 0.01, timeout)
            try:
                waiter.start(blocking=True)
            except TimeoutError:
                raise


class NewDaqInterface(DaqInterface):
    def __init__(self, board: str):
        super().__init__(board)
        self._acq = None

    def __del__(self):
        try:
            self.stop_capture()
        except:
            pass

    def start_capture(self):
        self._acq = AcquisitionManager(self._board).create_temporary()
        self._acq.set_output()

    def stop_capture(self):
        try:
            self._acq.delete()
        except:
            # most likely means it was already deleted
            pass
        self._acq = None
        AcquisitionManager(self._board).current_acquisition = None

    def stream(self, timeout: float) -> typing.Iterable[dict]:
        start = 0
        skip_bad = False
        return self._acq.stream_parsed(timeout, skip_bad=skip_bad, start=start)
