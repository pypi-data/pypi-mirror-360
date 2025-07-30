from collections import deque

from naludaq.daq.workers.packager import PackagerLight


class DebugPackager(PackagerLight):
    """Similar to PackagerLight, the only difference is that
    it also stores sliced packets of raw data coming from the serial buffer
    into a raw_output_buffer. This allows the user to also collect
    data of the incoming byte stream.
    """

    def __init__(
        self,
        input_buffer: deque,
        output_raw_buffer: deque,
        output_buffer: deque,
        output_answers: deque,
        stop_word: bytes,
        frequency: int,
    ):
        """Prepares a thread (not open) which polls the input buffer and pops all data in it
        into a internal buffer. Depending on frequency, it will slice the internal
        buffer once it reaches a stop word, and store the sliced data into an
        output_buffer for parsing, and output_raw_buffer if defined. If there are answers within
        the data, it will separate it and store it in output_answers.

        Args:
            input_buffer (deque): Incoming stream from serial reader, raw bytes
            output_raw_buffer (deque): Stores raw sliced data if defined
            output_buffer (deque): Stores dict'd raw sliced data + info about pkg
            output_answers (deque): Data recieved intermittent to readout
            stop_word (bytes): Stop word to slice on
            frequency (int): How quick to poll the input buffer and slice
        """
        super().__init__(
            input_buffer, output_buffer, output_answers, stop_word, frequency
        )
        self.output_raw_buffer = output_raw_buffer

    def _slice_buffer(self, internal_buffer):
        """
        Slice the internal buffer at the stopword.

        Takes an internal buffer as a bytearray and cuts it at the stopword.
        The output is a list of packages. Once sliced the last part will be the first part of the next batch.

        Args:
            internal_buffer (bytearray): raw data to slice.

        Returns:
            output: a list of packages
            rest: whatever is after the last stopword.
        """
        output, answers, rest = super()._slice_buffer(internal_buffer)
        if self.output_raw_buffer is not None:
            for package in output:
                self.output_raw_buffer.append({"rawdata": package["rawdata"]})
        return output, answers, rest
