"""Package creator is the second part in a multithread double buffer.
The packager slices teh raw data from the serial reader into packages.

OVERVIEW:
Checks the applications serial buffer for data.
Reads all data in the buffer and splits the data into packages.

Return package:
{'created_at': time.time(),
 'length': length of data,
 raw_data': bytesarray()
}

"""

import logging
import time
from queue import Queue
from threading import Thread
from typing import MutableSequence

logger = logging.getLogger("naludaq.packager")


##############################################################################
class OldPackagerLight(Thread):
    """Drop in replacement for the Packager but without the zmq stuff.

    Significantly slower, beware.
    """

    def __init__(self, input_buffer, output_buffer, stop_word, frequency):
        super().__init__()
        self.daemon = True
        self.input_buffer = input_buffer
        self.output_buffer = output_buffer
        self.stop_word = stop_word
        self.frequency = frequency
        self._reset_pkg_num = False
        self.running = True
        self._pkg_num = 0
        self.answer_size = 8

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

    @property
    def stop_word(self):
        """Get/Set the stop word, the end word of a package.

        Args:
            stop_word (bytes): Specific word ending an event in input_buffer.
        Returns:
            Returns the current stop word as bytes.
        """
        return self._stop_word

    @stop_word.setter
    def stop_word(self, stop_word):
        if isinstance(stop_word, bytes):
            self._stop_word = stop_word
        else:
            raise TypeError("stop_word must be bytes")

    def reset_pkg_num(self):
        """Resets the event numbering.

        Raises the reset flag and let the loop reset the evt_num
        """
        self._reset_pkg_num = True

    def run(self):
        logger.debug("Trying to start packager.")
        self._package_worker()

    def stop(self):
        self.running = False

    def _slice_buffer(self, internal_buffer):
        """Slice the internal buffer at the stopword.

        Takes an internal buffer as a bytearray and cuts it at the stopword.
        The output is a list of packages.
        Once sliced the last part will be the first part of the next batch.

        Args:
            internal_buffer (bytearray): raw data to slice.

        Returns:
            output: a list of packages
            rest: whatever is after the last stopword.
        """

        packages = internal_buffer.split(self._stop_word)

        output = [
            {
                "created_at": time.time(),
                "length": len(x + self._stop_word),
                "pkg_num": self._pkg_num + idx,
                "rawdata": x + self._stop_word,
            }
            for idx, x in enumerate(packages[:-1])
        ]

        self._pkg_num += len(packages) - 1
        rest = packages[-1]
        del packages

        return output, rest

    def _package_worker(self):
        """Worker takes raw serial string and package into packages.

        It looks for the end of the package b'face'.
        Ideally it would find the header of the package, then read until the end.
        It adds a timestamp on when the package is arrived for sorting purposes.

        Appends to package_buffer {'package_id': timestamp, 'length': length, rawdata':package}.
        """
        internal_buffer = bytearray()
        try:
            while self.running or self.input_buffer:
                frametime = time.perf_counter()

                if self.input_buffer:
                    try:
                        internal_buffer.extend(self.input_buffer.pop())
                    except:
                        logger.error("can't pop!")

                if internal_buffer:
                    output, rest = self._slice_buffer(internal_buffer)
                    internal_buffer = bytearray()
                    internal_buffer.extend(rest)
                    for package in output:
                        package["event_num"] = package["pkg_num"]
                        self.output_buffer.append(package)

                if self._reset_pkg_num:
                    self._pkg_num = 0
                    self._reset_pkg_num = False

                try:
                    time.sleep(frametime + self._interval - time.perf_counter())
                except ValueError:
                    # LOGGER.debug("Package worker is %ss behind",
                    #              (frametime + self._interval - time.perf_counter()))
                    pass
        except KeyboardInterrupt:
            pass


##############################################################################
class PackagerLight(Thread):
    """Drop in replacement for the Packager but without the zmq stuff.

    Significantly slower, beware.
    """

    def __init__(
        self,
        input_buffer: MutableSequence,
        output_buffer: MutableSequence,
        output_answers: Queue,
        stop_word: bytes,
        frequency: int,
    ):
        """Prepares a thread (not open) which polls the input buffer and pops all data in it
        into a internal buffer. Depending on frequency, it will slice the internal
        buffer once it reaches a stop word, and store the sliced data into an
        output_buffer for parsing. If there are answers within the data, it will separate it
        and store it in output_answers.

        Args:
            input_buffer (deque): Incoming stream from serial reader, raw bytes
            output_raw_buffer (deque): Stores raw sliced data if defined
            output_buffer (deque): Stores dict'd raw sliced data + info about pkg
            output_answers (deque): Data recieved intermittent to readout
            stop_word (bytes): Stop word to slice on
            frequency (int): How quick to poll the input buffer and slice
        """
        super().__init__()
        self.daemon = True
        self.input_buffer = input_buffer
        self.output_buffer = output_buffer
        self.answers = output_answers
        self.stop_word = stop_word
        self.frequency = frequency
        self._reset_pkg_num = False
        self.running = True
        self._pkg_num = 0
        self.answer_size = 8

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

    @property
    def stop_word(self):
        """Get/Set the stop word, the end word of a package.

        Args:
            stop_word (bytes): Specific word ending an event in input_buffer.
        Returns:
            Returns the current stop word as bytes.
        """
        return self._stop_word

    @stop_word.setter
    def stop_word(self, stop_word):
        if isinstance(stop_word, bytes):
            self._stop_word = stop_word
        else:
            raise TypeError("stop_word must be bytes")

    def reset_pkg_num(self):
        """Resets the event numbering.

        Raises the reset flag and let the loop reset the evt_num
        """
        self._reset_pkg_num = True

    def run(self):
        logger.debug("Trying to start packager.")
        self._package_worker()

    def stop(self):
        self.running = False

        return self._pkg_num

    def _is_answer_package(self, package: bytearray) -> bool:
        """Checks if a package is an answer package based on length.

        Args:
            package (bytearray): the raw package.

        Returns:
            True if the package is an answer, False otherwise.
        """
        return len(package) + len(self.stop_word) <= self.answer_size

    def _is_data_package(self, package: bytearray) -> bool:
        """Checks if a package is a data (event) package based on length.

        Args:
            package (bytearray): the raw package.

        Returns:
            True if the package is data, False otherwise.
        """
        return len(package) + len(self.stop_word) > self.answer_size

    def _create_answer_package(self, rawdata: bytearray) -> dict:
        """Creates an answer package from rawdata.

        Args:
            rawdata (bytearray): the raw data.

        Returns:
            The answer package as a dict.
        """
        return {
            "created_at": time.time(),
            "length": len(rawdata),
            "rawdata": rawdata,
        }

    def _create_data_package(self, rawdata: bytearray, pkg_num) -> dict:
        """Creates a data package from rawdata.

        Args:
            rawdata (bytearray): the raw data.

        Returns:
            The data package as a dict.
        """
        return {
            "created_at": time.time(),
            "length": len(rawdata),
            "pkg_num": pkg_num,
            "rawdata": rawdata,
        }

    def _slice_buffer(self, internal_buffer):
        """Slice the internal buffer at the stopword.

        Takes an internal buffer as a bytearray and cuts it at the stopword.
        The output is a list of packages.
        Once sliced the last part will be the first part of the next batch.

        Args:
            internal_buffer (bytearray): raw data to slice.

        Returns:
            A tuple of (output, answers, rest):
                - output: a list of event packages
                - answers: a list of answer packages
                - rest: whatever is after the last stopword.
        """
        packages = internal_buffer.split(self._stop_word)

        output = [
            self._create_data_package(x + self._stop_word, self._pkg_num + idx)
            for idx, x in enumerate(packages[:-1])
            if self._is_data_package(x)
        ]
        answers = [
            self._create_answer_package(x + self._stop_word)
            for x in packages[:-1]
            if self._is_answer_package(x)
        ]

        self._pkg_num += len(packages) - 1
        rest = packages[-1]
        del packages

        return output, answers, rest

    def _route_serial_data(self, buff: bytearray):
        """Splits and routes serial data into the appropriate
        output buffers.

        Args:
            buff (bytearray): the serial input buffer

        Returns:
            Any leftover serial data following the last stop word.
        """
        output, answers, rest = self._slice_buffer(buff)
        for package in output:
            package["event_num"] = package["pkg_num"]
            self.output_buffer.append(package)
        for package in answers:
            self.answers.put(package)

        return rest

    def _package_worker(self):
        """Worker takes raw serial string and package into packages.

        It looks for the end of the package b'face'.
        Ideally it would find the header of the package, then read until the end.
        It adds a timestamp on when the package is arrived for sorting purposes.

        Appends to package_buffer {'package_id': timestamp, 'length': length, rawdata':package}.
        """
        internal_buffer = bytearray()
        try:
            while self.running:
                frametime = time.perf_counter()

                for _ in range(len(self.input_buffer)):
                    try:
                        internal_buffer.extend(self.input_buffer.pop())
                    except:
                        logger.error("can't pop from input buffer.")

                if internal_buffer:
                    rest = self._route_serial_data(internal_buffer)
                    internal_buffer = bytearray(rest)

                if self._reset_pkg_num:
                    self._pkg_num = 0
                    self._reset_pkg_num = False

                try:
                    time.sleep(frametime + self._interval - time.perf_counter())
                finally:
                    continue
        except KeyboardInterrupt:
            self.running = False
