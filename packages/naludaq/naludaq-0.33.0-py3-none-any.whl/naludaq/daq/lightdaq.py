"""Light DAQ, lightweight data acquisition doing the bare minimum.
"""
import logging
import time
from collections import deque
from functools import partial
from queue import Queue
from threading import Lock, Thread

import numpy as np

from naludaq.backend.exceptions import BackendError
from naludaq.daq.workers import get_usb_reader
from naludaq.daq.workers.answer_parser_worker import AnswerParserWorker
from naludaq.daq.workers.csv_storage_worker import CSVStorageWorker
from naludaq.daq.workers.packager.worker_packager import OldPackagerLight, PackagerLight
from naludaq.daq.workers.packager.worker_packager_hdsoc import HDSoCPackager
from naludaq.models import Acquisition

LOGGER = logging.getLogger(__name__)


class LightDaq:
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

    MAX_DISK_WRITERS = 1

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
        self._init_storage_settings()

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
    def storage_settings(self):
        """Get/Set the storage location for data saved to disk."""
        return self._storage_settings

    @storage_settings.setter
    def storage_settings(self, value: dict):
        """Updates the storage settings used in preprocessing.
        Will only update values that are given.

        Args:
            value (dict):  {
            "correct_pedestals": bool
            "convert_mv": bool
            "correct_time": bool
            "convert_time": bool
            "process_in_place": bool

            }
        """
        self._storage_settings.update(value)
        if self.disk_worker:
            self.disk_worker.storage_settings = self.storage_settings

    @property
    def storage_namepattern(self):
        """Get/Set the storage namepattern.

        event_{} will fill the event number
        """
        return self._storage_namepattern

    @storage_namepattern.setter
    def storage_namepattern(self, value):
        self._storage_namepattern = value

    @property
    def storage_amount(self):
        """Get/Set the storage max amount."""
        return self._storage_amount

    @storage_amount.setter
    def storage_amount(self, value):
        self._storage_amount = value

    @property
    def acquisition_name(self):
        """Get/Set the Acquisition name."""
        return self._acquisition_name

    @acquisition_name.setter
    def acquisition_name(self, name):
        self._acquisition_name = name

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
        if self.disk_worker:
            self.disk_worker.input_buffer = self._output_buffer

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
        self.stop_workers()
        self._board = board

        self.init_and_start_workers()

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

    def _init_storage_settings(self):
        """Initializes the storage settings, used in Preprocessing."""
        self._storage_settings = {
            "correct_pedestals": False,
            "convert_adc2mv": False,
            "correct_timing": False,
            "convert_samples2time": False,
            "correct_ecc": False,
            "process_in_place": False,
        }

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
            self.board,
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
        return {
            "hdsocv1": partial(HDSoCPackager, self._board),
            "hdsocv1_evalr1": partial(HDSoCPackager, self._board),
            "hdsocv1_evalr2": partial(HDSoCPackager, self._board),
        }.get(self.board.model, PackagerLight)(**kwargs)

    def init_diskstorage(self):
        """Create the disk storage.
        Only create it if it didn't already exist.
        """
        if not self.disk_worker:
            self.disk_worker = self._create_diskstorage()
        self.disk_worker.start()

    def _create_diskstorage(self):
        """ """
        return CSVStorageWorker(
            self.output_buffer,
            self.board,
            self.storage_settings,
            self.storage_directory,
        )

    def init_answer_parser(self):
        """Create the answer parser.

        Parsers the answers to regreads into a buffer.
        """
        self.answer_parser = self._create_answer_parser()

        self.workers.append(self.answer_parser)
        self.answer_parser.start()

    def _create_answer_parser(self):
        return AnswerParserWorker(
            self._packager_to_answer_buffer,
            self.answers,
            self.answers_lock,
        )

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
        if self.store_to_disk:
            self.init_diskstorage()
        self.init_packager()
        self.init_answer_parser()
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

        if self.answer_parser:
            self.answer_parser.stop()
            self.answer_parser.join()

        if self.disk_worker:
            self.disk_worker.stop()

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

    def read_register(self, reg_num: int, timeout: int = 10000):
        """Read a register by number.

        Ask the board for a register and wait until there is a response.

        Args:
            reg_num(int): The register to read. See board specific register map.

        Returns:
            The register
        """
        # Make sure the id is unique.
        while True:
            cmd_id = np.random.randint(0, 2**16)
            if self.questions.get(cmd_id, False) is False:
                self.questions[cmd_id] = ""
                LOGGER.debug("Asked question: %s", cmd_id)
                break

        command = "AD{0:02x}{1:04x}".format(reg_num, cmd_id)

        self.board.connection.send(command)

        def find_answer(cmd_id, answer_lock, answers, answer):
            timeout = 5
            t_count = 0
            while True:
                print("waiting for answer")
                with answer_lock:
                    print("inside the lock")
                    answer = answers.get(cmd_id, None)
                    print(f"Available answers: {answers}")
                if answer:
                    break
                time.sleep(0.5)
                t_count += 1
                if t_count >= timeout:
                    break
            print(f"--------got an answer: {answer}")

        answer = ""
        finder = Thread(
            target=find_answer, args=(cmd_id, self.answers_lock, self.answers, answer)
        )
        LOGGER.debug("waiting to find answer")
        finder.daemon = True
        finder.start()
        finder.join()
        LOGGER.debug("Answer found: %s", answer)
        return answer


#####################################################################


class OldLightDaq:
    """Data Acquisition (DAQ) for the ASoC.

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

    MAX_DISK_WRITERS = 1

    def __init__(self, board):
        self._board = board
        self.serial_reader = None
        self.worker_packager = None
        self._worker_serial_reader = None
        self._parsed_events = None  # Output
        self._acquisition_name = None
        self._frequency_packager = 1000
        self._pkg_num = 0

        self.workers = []

        self._init_buffers()

    @property
    def storage_directory(self):
        """Get/Set the storage location for data saved to disk."""
        return self._storage_directory

    @storage_directory.setter
    def storage_directory(self, value):
        self._storage_directory = value

    @property
    def acquisition_name(self):
        """Get/Set the Acquisition name."""
        return self._acquisition_name

    @acquisition_name.setter
    def acquisition_name(self, name):
        self._acquisition_name = name

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
        self.stop_workers()
        self._board = board

        self.init_and_start_workers()

    def init_and_start_workers(self):
        """Starts the worker threads and initilizes queues and processes."""
        self._init_buffers()
        # self.setup_pipeline()

    def _init_buffers(self):
        """Initialize all buffers used.

        There is a buffer between every worker.
        Buffers are made up of deque or queues.
        """
        # serial reader appends to:
        self._serial_to_packager_buffer = deque()
        self._packager_to_parser_buffer = deque()

        # Output buffer
        self.output_buffer = deque()

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
        return get_usb_reader(self.board, self._serial_to_packager_buffer)

    def init_packager(self):
        """Initialize the basic workers.

        Serial reader and the packager are the first
        two steps in the data acquisition pipeline.
        """

        self.worker_packager = self._create_packager()

        self.workers.append(self.worker_packager)
        self.worker_packager.start()

    def _create_packager(self):
        return OldPackagerLight(
            self._serial_to_packager_buffer,
            self.output_buffer,
            self._board.params["stop_word"],
            self._frequency_packager,
        )

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
        time.sleep(0.05)
        self.init_packager()
        self.init_serial_reader()

    def stop_capture(self):
        """Stops the capturing of data via the interface."""
        # self.stop_workers()
        if self._worker_serial_reader:
            self._worker_serial_reader.stop()
            self._worker_serial_reader.join()

        if self.worker_packager:
            self.worker_packager.stop()
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
