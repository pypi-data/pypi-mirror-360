"""DebugDaq
=======

A DAQ used to collect more information about the incoming data.

"""
from collections import deque
from logging import getLogger
from queue import Queue

from naludaq.backend.exceptions import BackendError
from naludaq.daq.workers import get_usb_reader
from naludaq.daq.workers.packager import DebugPackager, get_packager
from naludaq.daq.workers.worker_parser import ParserWorkerLight
from naludaq.parsers import get_parser

LOGGER = getLogger(__name__)

HDSOC_PACKAGER = ["hdsocv1", "hdsocv1_evalr1", "hdsocv1_evalr2"]
HIPER_PACKAGER = ["hiper"]


class DebugDaq:
    def __init__(self, board, store_raw_data=False, custom_parser=None):
        """Creates a DAQ used to collect data readouts from the given board.

        Args:
            board (naludaq.board): Board object to collect data from
            store_raw_data (bool, optional): If True, the raw bytearray
                collected from the board will be saved to a buffer.
                Defaults to False.
            custom_parser (parser object, optional): A user provided parser which
                will be used to parse raw data. Requires a "parse" attribute.
                Defaults to None.
        """
        if board.using_new_backend:
            raise BackendError("DAQs are incompatible with the new backend")
        self.board = board
        self.serial_to_packager_buffer = deque()
        self.packager_to_parser_buffer = deque()
        self.parser_error_buffer = deque()
        self.intermittent_answers_buffer = Queue()
        self._output_buffer = deque()
        self._raw_output_buffer = deque()
        self._acquisition_name = None
        self._custom_parser = None
        self._store_raw_data = store_raw_data
        self.pedestals = None
        self.workers = list()
        self._custom_parser = custom_parser

    @property
    def output_buffer(self) -> deque:
        """The buffer that stores events from the readout."""
        return self._output_buffer

    @output_buffer.setter
    def output_buffer(self, buffer):
        self._output_buffer = buffer

    @property
    def raw_output_buffer(self) -> deque:
        """The buffer that stores raw data from events. Each element added is a dict containing an unparsed 'rawdata' bytearray."""
        return self._raw_output_buffer

    @raw_output_buffer.setter
    def raw_output_buffer(self, buffer):
        self._raw_output_buffer = buffer

    @property
    def raw_output_stream(self) -> bytearray:
        """
        Takes the raw_output_buffer property and joins all bytearrays into a
        single bytearray, giving one continuous stream.
        """
        return b"".join([package["rawdata"] for package in self.raw_output_buffer])

    @property
    def custom_parser(self):
        """A custom parser to use for parsing raw events. Must be set _before_ starting capture.

        Raises:
            AttributeError if set to an object that does not have a `parse` attribute.
        """
        return self._custom_parser

    @custom_parser.setter
    def custom_parser(self, parser):
        if parser is None or self.validate_parser(parser):
            self._custom_parser = parser
        else:
            raise AttributeError(
                "The given custom parser does not have attribute 'parse'."
            )

    @property
    def acquisition_name(self):
        """Get/Set the Acquisition name."""
        return self._acquisition_name

    @acquisition_name.setter
    def acquisition_name(self, name):
        self._acquisition_name = name

    @property
    def board(self):
        """Change the board controller used.

        Useful if the board model is changed, then update the board controller.
        This can also be used to restart the daq since all Threads and Processes are stopped
        before changing the board controller.

        Args:
            board_controller: New board controller to use.
        """
        return self._board

    @board.setter
    def board(self, board):
        LOGGER.debug("DAQ: changing board to: %s", board.params["model"])

        self._board = board

    def start_capture(self):
        """Starts workers that listen for readout data. Parsed events are stored in the
        `output_buffer` attribute, and raw events are stored in the `raw_output_buffer`
        attribute.

        If called while still capturing, the workers are restarted.
        """
        if self.workers:
            self.stop_capture()

        serial_reader = self._get_serial_reader()
        packager_worker = self._get_packager_worker()
        parser_worker = self._get_parser_worker()

        self.workers.append(serial_reader)
        self.workers.append(packager_worker)
        self.workers.append(parser_worker)

        for worker in self.workers:
            worker.start()

    def _get_serial_reader(self):
        return get_usb_reader(self.board, self.serial_to_packager_buffer)

    def _get_parser_worker(self):
        if self._custom_parser is None:
            parser = get_parser(self.board.params)
        else:
            parser = self.custom_parser

        pw = ParserWorkerLight(
            parser,
            self.packager_to_parser_buffer,
            self.output_buffer,
            self.parser_error_buffer,
        )
        return pw

    def _get_packager_worker(self):

        if self._store_raw_data:
            raw_buffer = self._raw_output_buffer
        else:
            raw_buffer = None

        if self.board.params["model"] in HDSOC_PACKAGER:
            dp = get_packager(
                self.board,
                self.serial_to_packager_buffer,
                # raw_buffer,
                self.packager_to_parser_buffer,
                self.intermittent_answers_buffer,
                self.board.params["stop_word"],
                1000,
            )
        elif self.board.params["model"] in HIPER_PACKAGER:
            dp = get_packager(
                self.board,
                self.serial_to_packager_buffer,
                # raw_buffer,
                self.packager_to_parser_buffer,
                self.intermittent_answers_buffer,
                self.board.params["stop_word"],
                1000,
            )
        else:
            dp = DebugPackager(
                # self.board,
                self.serial_to_packager_buffer,
                raw_buffer,
                self.packager_to_parser_buffer,
                self.intermittent_answers_buffer,
                self.board.params["stop_word"],
                1000,
            )

        return dp

    def stop_capture(self):
        """Stops all workers currently running."""
        while self.workers:
            worker = self.workers.pop()
            worker.stop()
            worker.join()

    def stop_workers(self):
        """Does nothing, but makes the class look like a LightDaq."""
        pass

    def switch_output_buffer(self, new_buffer, pedestals=None):
        """Switching the output buffer, the daq will finish the last batch
        before switching.

        Args:
            new_buffer: Acquisition or deque to append to.
            pedestals: Pedestals to use with next acquisition.
        """
        self.output_buffer = new_buffer
        self.pedestals = pedestals

        if "name" in new_buffer.__dir__():
            self.acquisition_name = new_buffer.name

    def validate_parser(self, parser):
        """Checks whether the given custom parser can be used for parsing events.

        Returns:
            True if the object has a "parse" attribute, or False otherwise.
        """
        return hasattr(parser, "parse")
