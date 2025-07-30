import time
from logging import getLogger
from threading import Thread

from naludaq.helpers.exceptions import BadDataError

logger = getLogger(__name__)


class ParserWorkerLight(Thread):
    """Lightweight replacement for the parser worker."""

    def __init__(
        self, parser, input_buffer, output_buffer, error_buffer, frequency=1000
    ):
        super().__init__()
        self.parser = parser
        self.input_buffer = input_buffer
        self.output_buffer = output_buffer
        self.error_buffer = error_buffer
        self.frequency = frequency
        self.running = True
        self.daemon = True

    @property
    def frequency(self):
        """Get/Set the frequency this thread polls the serial port.

        Frequency in Hz (times per second).
        """

        return self._frequency

    @frequency.setter
    def frequency(self, freq):
        if not isinstance(freq, (int, float)):
            raise TypeError("Frequency must be an integer or float")
        if freq <= 0:
            raise ValueError("Frequency must be positive")

        self._frequency = freq
        self._interval = 1 / freq

    def run(self):
        self._parserloop()

    def stop(self):
        self.running = False

    def _parserloop(self):
        """Main worker loop"""
        evt_num = 0
        try:
            while self.running or self.input_buffer:
                frametime = time.perf_counter()
                next_pkg = None

                if self.input_buffer:
                    next_pkg = self.input_buffer.popleft()

                if next_pkg:
                    try:
                        parsed_package = self.parser.parse(next_pkg)
                    except (Exception, TypeError, BadDataError) as error_msg:
                        logger.error("Parsing package failed due to: %s", error_msg)
                        self.error_buffer.append(next_pkg)
                    else:
                        parsed_package["event_num"] = evt_num
                        self.output_buffer.append(parsed_package)
                        evt_num += 1

                try:
                    time.sleep(frametime + self._interval - time.perf_counter())
                except ValueError:
                    pass
        except KeyboardInterrupt:
            pass
