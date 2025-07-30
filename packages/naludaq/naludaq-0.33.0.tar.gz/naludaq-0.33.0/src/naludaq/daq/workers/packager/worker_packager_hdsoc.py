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
from collections import defaultdict, deque
from typing import List

from naludaq.daq.workers.packager.worker_packager import PackagerLight

logger = logging.getLogger(__name__)


UNUSED_TIMING = -1_000_000  # This must be sufficently far from timing margin.
TIMING_MARGIN = 1500


class HDSoCPackager(PackagerLight):
    """A specialized version of the `PackagerLight` for HDSoCv1.

    The packager will split the data in the ``input_buffer`` into
    ``output_buffer`` and ``output_answers`` depending on the pkg length.

    The HDSoC has a different timing system than the other boards.
    The timing system is used to sort the packets into events.
    The timing is a 24-bit number, it's stored in the header of the packet.

    To sort the packages correctly into events the timing of each packet is parsed
    Then it's compared to the timing of the previous packet.
    If the timing is within the margin, the packet is added to the event.
    If the timing is outside the margin, the previous event is completed and a new event is started.

    The packager also has a timeout to separate data originating from two
    different readouts. This prevents the problem of mixing old and new data
    and offsetting later data by some number of windows.

    Args:
        board (Board): the board object
        input_buffer (deque): incoming stream from serial reader, raw bytes
        output_buffer (deque): output for raw event `dict`s.
        output_answers (deque): answers received from serial reader during readout
        stop_word (bytes): Stop word to slice on
        frequency (int): How quick to poll the input buffer and slice

    """

    def __init__(
        self,
        board,
        input_buffer: deque,
        output_buffer: deque,
        output_answers: deque,
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
        self._board = board
        self._chan_mask = board.params.get("chanmask", 0x3F)
        self._package_size = board.params.get("package_size", 72)

        self._timing_mask = board.params.get("timing_mask", 0xFFF)
        self._timing_shift = board.params.get("timing_shift", 12)

        self._create_incomplete_event(UNUSED_TIMING)

        self.timing_margin = TIMING_MARGIN
        self._do_timeout = True
        self._timeout = 0.8  # determined experimentally
        self._last_packet_time = 0

    def _slice_buffer(self, internal_buffer: bytearray):
        """Slice the internal buffer at the stopword, and
        separates the data into events, answers, and remaining (incomplete)
        data.

        This specialized HDSoC version of the function builds events from
        received packets over multiple calls, and returns the built
        events once they are complete.

        Args:
            internal_buffer (bytearray): raw data to slice.

        Returns:
            A tuple of (output, answers, rest):
                - output: a list of rawevent packages(dict)
                - answers: a list of answer packages
                - rest: whatever is after the last stopword.
        """
        complete_events = []
        raw_events = []
        packets = internal_buffer.split(self._stop_word)

        complete_event = self._timeout_event(packets)
        if complete_event:
            complete_events.append(complete_event)

        # Separate the packets into events and answers
        c_events, answers = self._sort_packets(packets[:-1])
        complete_events.extend(c_events)

        # Create raw events from the complete_events
        for complete in complete_events:
            raw_event = self._create_raw_event(complete)
            raw_events.append(raw_event)

        return raw_events, answers, packets[-1]

    def _timeout_event(self, packets) -> dict:
        """Check if an incomplete event has timed out.

        If the event has timed out, it is added to the list of completed events.
        This means if the data stops, the incomplete event is not lost.

        Args:
            packets (list): list of packets to check for timeout.

        Returns:
            The completed event.
        """
        complete_event = None
        if (
            self._do_timeout and len(packets) > 1
        ):  # Not sure if there need to be a packet received for the timeout to activate.
            if time.perf_counter() - self._last_packet_time > self._timeout:
                if (
                    self._incomplete_event["timing"] != UNUSED_TIMING
                ):  # If the incomplete event is not new.
                    complete_event = self._incomplete_event
                self._create_incomplete_event(unused_timing=UNUSED_TIMING)
                logger.debug(f"Packager timed out, flushed an incomplete events")
            self._last_packet_time = time.perf_counter()

        return complete_event

    def _create_incomplete_event(self, unused_timing: int):
        """Create an incomplete event."""
        self._incomplete_event = defaultdict(list)
        self._incomplete_event["timing"] = unused_timing

    def _sort_packets(self, packets: List[bytes]) -> list:
        """Sorts packets received into answers and incomplete events.

        Sorts the packets into answers and incomplete events based on the length.
        An answer from the board is 8 bytes long, and an incomplete event is 72 bytes long.

        Args:
            packets (list): the packets to sort

        Returns:
            A list of events and a list of answers from the input packets.
        """
        events = []
        answers = []
        for packet in packets:
            if self._is_answer_package(packet):
                answer_package = self._create_answer_package(packet + self.stop_word)
                answers.append(answer_package)
            elif self._is_data_package(packet):
                event = self._insert_packet(
                    packet
                )  # Event is None if no complete event
                if event:
                    events.append(event)

        return events, answers

    def _create_raw_event(self, event: dict) -> dict:
        """Generates a raw event dict for each complete event
        given.

        Args:
            complete_events (list): list of complete events.
                Each element should be a `dict[chan: list[bytes]]`

        Returns:
            A list of parse-able raw events.
        """
        stop_word = self._stop_word
        all_packets = [
            x for chan in event if isinstance(chan, int) for x in event[chan]
        ]
        output_event = self._create_data_package(
            rawdata=stop_word.join(all_packets) + stop_word, pkg_num=self._pkg_num
        )
        self._pkg_num += 1
        return output_event

    def _is_data_package(self, package: bytearray) -> bool:
        """Checks if a package is a data (event) package based on length.

        Args:
            package (bytearray): the raw package.

        Returns:
            True if the package is data, False otherwise.
        """
        return len(package) == self._package_size

    def _insert_packet(self, packet: bytearray):
        """Sorts a package into the earliest occuring incomplete event for which there is a
        slot available. If the event is complete, it's returned

        If all previous events have the correct number of windows for that channel, a new
        incomplete event is created and the package is stored into it.

        Args:
            packet (bytearray): the package to store
        """
        complete_event = None
        word_builder = (
            lambda i: (packet[i] << 8) + packet[i + 1]
        )  # Builds a word from a pair of bytes
        packet_channel = word_builder(0) & 0b111111

        # packet timing are the lower 12 bit of the second and third word, making a 24-bit timing.
        packet_timing = (
            int(word_builder(2) & self._timing_mask) << self._timing_shift
        ) | int(word_builder(4) & self._timing_mask)

        # Case 1: timing withing margins, it's part of THIS event
        if (
            self._incomplete_event["timing"] - self.timing_margin
            <= packet_timing
            <= self._incomplete_event["timing"] + self.timing_margin
        ):
            self._incomplete_event[packet_channel].append(packet)  # NEED to append

        # Case 2: timing outside margins, it's part of a NEW event
        elif (
            self._incomplete_event["timing"] + self.timing_margin <= packet_timing
            or packet_timing < self._incomplete_event["timing"] - self.timing_margin
        ):
            if (
                self._incomplete_event["timing"] != UNUSED_TIMING
            ):  # The first packet is never complete
                complete_event = self._incomplete_event

            self._create_incomplete_event(packet_timing)
            self._incomplete_event[packet_channel].append(packet)

        else:
            pass

        return complete_event

    def stop(self):
        super().stop()
        # Any incomplete data will be saved in case stop is in middle of event.
        if self._incomplete_event["timing"] != UNUSED_TIMING:
            complete = self._incomplete_event
            raw_event = self._create_raw_event(complete)
            self.output_buffer.append(raw_event)
