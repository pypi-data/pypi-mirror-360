"""Light DAQ, lightweight data acquisition doing the bare minimum.
"""
import logging
import time
from collections import deque
from queue import Queue
from threading import Lock

from naludaq.backend.exceptions import BackendError
from naludaq.daq.workers import get_usb_reader
from naludaq.daq.workers.packager import get_packager
from naludaq.models import Acquisition

LOGGER = logging.getLogger(__name__)


class HiperDaq:
    """Data Acquisition (DAQ) for the ASoC.

    Capture and packetize bulk data from the Board.


    Args:
        board_controller: the board controller
        location: storage location for the data.


    Runs the different part of the acquisition pipeline.
    Serial reader
    Packager

    Attributes:
        parsed_output (bool): will output be parsed or raw. Default: True
        storage_directory (path): Where to store data to disk.
        frequency_packager (int): Polling speed of packager.
    """

    def __init__(self, board, location, start_workers):
        if board.using_new_backend:
            raise BackendError("DAQs are incompatible with the new backend")
        self._board = board

        self.storage_directory = location
        self._storage_directory = None
        self._output_buffer = deque()
        self.parsed_output = False
        self.answers = {}
        self.questions = {}
        self.answers_lock = Lock()
        self.serial_reader = None
        self.parser_worker = None
        self.disk_worker = None
        self.worker_packager = None
        self.answer_parser = None
        self._worker_serial_reader = None
        self._parsed_events = None  # Output
        self._acquisition_name = None
        self._frequency_packager = 50
        self.pkg_num = 0
        self.store_to_disk = False
        self.workers = list()

        # self.preprocess = None

        self._init_buffers()

        # if start_workers:
        #     self.init_and_start_workers()

    @property
    def storage_directory(self):
        """Get/Set the storage location for data saved to disk."""
        return self._storage_directory

    @storage_directory.setter
    def storage_directory(self, value):
        self._storage_directory = value

    @property
    def output_buffer(self):
        """Get/Set the output buffer of the DAQ.

        This is where the daq store the output data.

        Args:
            output_buffer(deque, acquisition):
        """
        return self._output_buffer

    @output_buffer.setter
    def output_buffer(self, output):
        if not isinstance(output, (deque, Acquisition)):
            raise TypeError(
                "outputbuffer must be either a deque or an Acquisition obj."
            )
        self._output_buffer = output

    def init_and_start_workers(self):
        """Starts the worker threads and initilizes queues and processes."""
        self._init_buffers()
        # self.setup_pipeline()

    def _init_buffers(self):
        """Initialize all inter-worker buffers used.

        There is a buffer between every worker.
        Buffers are made up of deque or queues.
        """
        # serial reader appends to:
        self._serial_to_packager_buffer = deque()
        self._packager_to_parser_buffer = deque()

        self._packager_to_answer_buffer = Queue()

    def setup_pipeline(self):
        """Setup the components of the pipeline.

        Automagically starts the parts of the pipeline.
        """
        # self.init_packager()

        # self._init_parser()

        # Start Storagers (both)
        # self._init_store_raw_to_disk()
        # self._init_store_parsed_to_disk()

    def init_serial_reader(self):
        """Serial reader is started when data capture is started."""
        self._worker_serial_reader = self._create_serial_reader()
        self._worker_serial_reader.start()

    def _create_serial_reader(self):
        ser = get_usb_reader(
            self._board,
            self._serial_to_packager_buffer,
        )
        return ser

    def init_packager(self):
        """Initialize the basic workers.

        Serial reader and the packager are the first
        two steps in the data acquisition pipeline.
        """

        self.worker_packager = self._create_packager()
        self.worker_packager._pkg_num = self.pkg_num

        self.workers.append(self.worker_packager)
        self.worker_packager.start()

    def _create_packager(self):
        """Creates a packager object and connects it to the various I/O buffers.

        HDSoC gets a special packager.
        """
        kwargs = {
            "input_buffer": self._serial_to_packager_buffer,
            "output_buffer": self.output_buffer,
            "output_answers": self._packager_to_answer_buffer,
            "stop_word": self._board.params["stop_word"],
            "frequency": self._frequency_packager,
        }
        pack = get_packager(self._board, **kwargs)
        return pack

    def stop_workers(self):
        """Worker cleanup, shutdown the pipeline."""

        LOGGER.debug("Stopping threads")
        while self.workers:
            worker = self.workers.pop()
            LOGGER.debug("stopping: %s", worker)
            worker.stop()
            worker.join(5)

    def start_capture(self, acq_name="command"):
        """Start capturing serial data.

        Start polling the serial port also start storing to disk
        if the storeage options are set.
        """
        # Need to clear the worker buffers. Prevents bad problems!
        self._init_buffers()

        time.sleep(0.05)
        LOGGER.debug("STORE TO DISK: %s", self.store_to_disk)

        self.init_packager()
        self.init_serial_reader()

    def stop_capture(self):
        """Stops the capturing of data via the interface."""
        # self.stop_workers()
        if self._worker_serial_reader:
            self._worker_serial_reader.stop()
            self._worker_serial_reader.join()

        if self.worker_packager:
            self.pkg_num = self.worker_packager.stop()
            self.worker_packager.join()

        self.clear_workers()

        try:
            self._board.connection.reset_input_buffer()
        except Exception as error_msg:
            LOGGER.debug(
                "No connection to stop when stopping capture due to: %s", error_msg
            )

        # self._parsed_events = self.parse_all()

    def clear_workers(self):

        self._worker_serial_reader = None
        self.worker_packager = None
        self.answer_parser = None
        self.disk_worker = None

    def get_buffer_levels(self):
        """Return the amount in each of the buffers."""

        return {
            "serial buffer": len(self._serial_to_packager_buffer),
            "package buffer": len(self._packager_to_parser_buffer),
            "output": len(self.output_buffer),
        }

    def switch_output_buffer(self, new_buffer):
        """Switching the output buffer, the daq will finish the last batch
        before switching.

        Args:
            new_buffer: Acquisition or deque to append to.
            pedestals: Pedestals to use with next acquisition.
        """

        self.output_buffer = new_buffer

        if "name" in new_buffer.__dir__():
            self.acquisition_name = new_buffer.name

    def peek_latest_event(self) -> dict:
        """Returns the latest event parsed.

        Parses events on the fly, useful for oscilloscope plotting.

        Returns:
            Parsed event (dict) and pedestals corrected if requested.

        Raises:
            IndexError if the output_buffer is empty
        """
        event = None
        try:
            event = self.output_buffer[-1]
        except IndexError as emsg:
            raise IndexError(
                "Couldn't peek latest event %s, buffers: %s",
                emsg,
                self.get_buffer_levels(),
            )

        return event


#####################################################################
