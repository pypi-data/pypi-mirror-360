from logging import getLogger
from typing import MutableSequence

from naludaq.daq.workers.packager.worker_packager import PackagerLight

MAX_TIMEOUT = 50

logger = getLogger("naludaq.hiper_apckager")


class HiperPackager(PackagerLight):
    def __init__(
        self,
        input_buffer: MutableSequence,
        output_buffer: MutableSequence,
        output_answers: MutableSequence,
        stop_word: bytes,
        frequency: int,
    ):
        super().__init__(
            input_buffer=input_buffer,
            output_buffer=output_buffer,
            output_answers=output_answers,
            stop_word=stop_word,
            frequency=frequency,
        )

        self.answer_size = 8
        self._max_chip = -1
        self._prev_split = -1  # reset counter
        self._prev_buflen = -1
        self._prev_increase = 0
        self._timeout = 0

        self.chips = 14
        self.splitwords = [
            (x, bytes.fromhex(f"bbb{hex(x)[2:]}"), bytes.fromhex(f"fff{hex(x)[2:]}"))
            for x in range(self.chips)
        ]

    def run(self):
        logger.debug("Trying to start packager.")
        self._package_worker()

    def stop(self):
        self.running = False

    def _route_serial_data(self, internal_buffer) -> bytearray:
        """Splits and routes serial data into the appropriate
        output buffers.

        Args:
            buff (bytearray): the serial input buffer

        Returns:
            Any leftover serial data following the last stop word.
        """
        valid_splits = self._check_for_chips(internal_buffer)
        if not valid_splits:
            return internal_buffer
        max_chip, stop_word = valid_splits[
            -1
        ]  # Biggest chipnum is last in list by design, if this increased then flag stays low
        trigger = False
        if max_chip == self._prev_split:  # no increase in chip ending
            if (
                len(internal_buffer) >= self._prev_buflen + self._prev_increase
                and self._timeout > MAX_TIMEOUT
            ):  # we knew it took _prev_buflen to find an increase previously  # Can cause issue if polling too fast and no new endwords are polled, add a timeout or data amount recv critera?
                trigger = True
                self._timeout = 0
            if (
                len(internal_buffer) == self._prev_buflen
                and self._timeout > MAX_TIMEOUT
            ):  # No more data received.
                trigger = True
                self._timeout = 0
            else:
                self._timeout += 1
        else:
            # Will capture first time the last chipend is found
            self._prev_increase = (
                len(internal_buffer) - self._prev_buflen
            )  # will give us the requirec increase to find a chipend.
            self._prev_buflen = len(internal_buffer)
            self._timeout += 1

        if trigger:
            packages, answers, rest = self._slice_buffer(internal_buffer, stop_word)
            for package in packages:
                self.output_buffer.append(package)
            for package in answers:
                self.answers.put(package)

            self._prev_split = -1  # reset counter
            self._prev_buflen = len(rest)
            trigger = False
        else:
            # Not done collecting data yet
            self._prev_split = max_chip
            self._prev_buflen = len(internal_buffer)
            rest = internal_buffer

        return rest

    def _check_for_chips(self, idata) -> list:
        """Checks which chips are present in the data.
        Args:
        Returns:
            the (start,end) string tuple for the available chips.
        """
        p = -1
        valid_splits = []
        for idx, spl, sp2 in self.splitwords:
            p = idata.find(sp2)
            if p != -1:
                valid_splits.append((idx, sp2))
        return valid_splits

    def _slice_buffer(self, internal_buffer, stopword):
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

        packages = internal_buffer.split(stopword)

        output = [
            self._create_data_package(x + stopword, self._pkg_num + idx)
            for idx, x in enumerate(packages[:-1])
            if self._is_data_package(x)
        ]
        answers = [
            self._create_answer_package(x + stopword)
            for x in packages[:-1]
            if self._is_answer_package(x)
        ]
        self._pkg_num += len(packages) - 1
        rest = packages[-1]
        del packages

        return output, answers, rest
