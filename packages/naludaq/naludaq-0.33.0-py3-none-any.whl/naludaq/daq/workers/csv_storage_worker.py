"""
"""
import multiprocessing as mp
import pathlib
import queue
import threading
import time
from datetime import datetime
from logging import getLogger

from naludaq.daq.preprocess import Preprocess
from naludaq.io.io_manager import IOManager

LOGGER = getLogger(__name__)


class Constants:
    # Cool hack to prevent serialization error
    def __init__(self, board):
        self.pedestals = (getattr(board, "pedestals", None),)
        self.params = board.params
        self.timingcal = getattr(board, "timingcal", None) or board.timingcal
        self.pedestals = getattr(board, "pedestals", None)
        self.caldata = getattr(board, "caldata", None)


class CSVStorageWorker:
    """Control class for the storage worker router and the worker."""

    def __init__(
        self,
        input_buffer,
        board,
        storage_settings,
        directory,
        namepattern="{}_event_{}",
    ):
        self.stopper = mp.Event()
        self.input_buffer = input_buffer
        self.board = board
        self.storage_settings = storage_settings
        self.intermediary_buffer = mp.Queue()
        self._directory = directory
        self._namepattern = namepattern
        self.router = None
        self.constants = Constants(board)
        self.router = deque2QueueRouter(
            self.input_buffer,
            self.intermediary_buffer,
        )
        self.worker = Queue2CSV(
            self.stopper,
            self.intermediary_buffer,
            self.constants,
            self.storage_settings,
            self.directory,
            self.namepattern,
        )

    def reset(self):
        """close the old and recreate the internal elements."""
        if self.router:
            self.router.stop()
        if self.intermediary_buffer:
            self.intermediary_buffer.close()
        self.intermediary_buffer = mp.Queue()
        self.router = deque2QueueRouter(
            self.input_buffer,
            self.intermediary_buffer,
        )
        self.worker = Queue2CSV(
            self.stopper,
            self.intermediary_buffer,
            self.board,
            self.storage_settings,
            self.directory,
            self.namepattern,
        )

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, value):
        self._directory = value
        message = ("directory", value)
        self.router.relay(message)
        # self.output_buffer.put(message)

    @property
    def namepattern(self):
        return self._namepattern

    @namepattern.setter
    def namepattern(self, value):
        message = ("pattern", value)
        self.router.relay(message)
        # self.output_buffer.put(message)
        self._namepattern = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        message = ("amount", value)
        self.router.relay(message)
        # self.output_buffer.put(message)
        self._amount = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        message = ("frequency", value)

        self.router.relay(message)
        # self.output_buffer.put(message)
        self._interval = 1 / value
        self._frequency = value

    def start(self):
        self.router.start()
        self.worker.start()

    def stop(self):
        self.router.stop()
        self.stopper.set()

    def buffer_level(self):
        """Returns a string wtih the buffer levels."""
        return f"{len(self.input_buffer)}, {self.intermediary_buffer.qsize()}"


class deque2QueueRouter(threading.Thread):
    """Communicates with the worker.

    All communication with the process is sent through this thread.


    """

    def __init__(self, input_buffer, output_buffer):
        super().__init__()
        self.amount = -1

        self.input_buffer = input_buffer
        self.output_buffer = output_buffer
        self._interval = 1 / 100
        self.running = True

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, value):
        self._directory = value
        message = ("directory", value)
        self.relay(message)

    @property
    def namepattern(self):
        return self._namepattern

    @namepattern.setter
    def namepattern(self, value):
        message = ("namepattern", value)
        self.relay(message)
        self._namepattern = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        # message = ("amount", value)
        # self.relay(message)
        self._amount = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        message = ("frequency", value)
        self.relay(message)
        self._interval = 1 / value
        self._frequency = value

    def relay(self, message):
        """Relay a message to the worker.

        Args:
            message (tuple): Sends a message (command(str), value(object)), must be pickleable.
        """
        if not isinstance(message, tuple):
            raise TypeError("Message must be a tuple")
        if not isinstance(message[0], str):
            raise ValueError("First part of message mst be a command.")
        try:
            self.output_buffer.put(message)
        except ValueError:
            raise ValueError("Communication path to worker is closed.")

    def run(self):
        """ """
        self._workloop()

    def stop(self):
        """ """
        self.output_buffer.put(("Stop", []))
        self.running = False

    def _workloop(self):
        """Run in thread, takes data from output_buffer and puts ina queue for CSV writer"""
        interval = self._interval  # 1/100 # 100Hz
        index = 0

        while self.running and (self.amount - index != 0):
            frametime = time.perf_counter()
            if index < len(self.input_buffer):
                evt = self.input_buffer[index]
                cmd = "save"
                index += 1
                message = (cmd, evt)
                self.output_buffer.put(message)

            try:
                time.sleep(frametime + interval - time.perf_counter())
            except ValueError:
                pass
        self.output_buffer.put(("stop", []))
        self.output_buffer.close()
        self.output_buffer.join_thread()


class Queue2CSV(mp.Process):
    """Worker storing the CSV files on disk from an input mp.Queue

    Also receives commands from the queue. By using the router object
    it'll route the messages to this process.
    """

    def __init__(
        self, stopper, input_buffer, constants, storage_settings, directory, namepattern
    ) -> None:
        super().__init__()
        self.daemon = True
        self.timeout = 100
        self.stopper = stopper  # mp.Event
        self.input_buffer = input_buffer  # mp.Queue
        self.preprocess = Preprocess(constants)
        self.io_manager = IOManager(constants.params)
        self.storage_settings = storage_settings
        self.directory = directory
        self.namepattern = namepattern
        self.filetype = ".csv"
        self.bad_filetype = ".bin"

    def run(self):
        self._worker_loop()

    def stop(self):
        self.running = False

    def _worker_loop(self):
        """Worker loop, runs until certain conditions are met."""
        self.running = True
        while not self.stopper.is_set() and self.running:
            try:
                message = self.input_buffer.get(block=True, timeout=self.timeout)
            except (queue.Empty, mp.TimeoutError):
                continue
            cmd = message[0]
            evt = message[1]
            if cmd.lower() == "save":
                self.parse_and_save(evt)
            elif cmd.lower() == "stop":
                self.running = False
                continue
            elif cmd.lower() == "kill":
                break
            elif cmd in ["directory", "namepattern", "frequency", "amount"]:
                try:
                    setattr(self, cmd, evt)
                except AttributeError:
                    # Not a valid command
                    pass

        # self.input_buffer.close()
        # self.input_buffer.join_thread()

    def parse_and_save(self, evt):
        """
        TODO: Modify this function with settings for filename and file path.
        """
        parsed_evt = preprocess_event(evt, self.preprocess, self.storage_settings)
        correct_ecc = self.storage_settings.get("correct_ecc", False)

        evt_num = evt.get("event_num", None)
        timestamp = evt.get("created_at", None)
        if timestamp is None:
            timestamp = datetime.now().strftime("%y-%m-%d_%H-%M-%S")
        else:
            timestamp = datetime.fromtimestamp(timestamp)
            timestamp = timestamp.strftime("%y-%m-%d_%H-%M-%S")
        if evt_num is not None:
            filename = self.namepattern.format(timestamp, evt_num)
            filepath = pathlib.Path(self.directory) / (filename + self.filetype)
            bad_filepath = pathlib.Path(self.directory) / (filename + self.bad_filetype)
        else:
            filepath = unique_path(self.directory, self.namepattern)
            bad_filepath = unique_path(self.directory, self.namepattern)
        ecc_errors = parsed_evt.get("ecc_errors", None)
        if correct_ecc and ecc_errors is not None:
            filename = (
                filepath.stem + f"_ecc_errors_{len(ecc_errors)}" + filepath.suffix
            )
            filepath = filepath.parent / filename
            errorname = filepath.stem + "_errors" + ".csv"
            errorpath = filepath.parent / errorname
            self.io_manager.export_errors_csv(errorpath, ecc_errors)
        if parsed_evt.get("data", None) is not None:
            self.io_manager.export_acq_to_csv(filepath, [parsed_evt])
        else:
            self.io_manager.export_acq_to_bin(bad_filepath, [evt])


def preprocess_event(event, preprocess, storage_settings):
    """Create a parsed and pedestals corrected event from raw input.

    Args:
        event (dict): raw event
        preprocess (Preprocess): Processor to convert raw -> parsed events
        storage_settings (dict): Settings for how preprocess will parse events

    Returns:
        event dictionary with parsed and pedestals corrected event.
    """
    if event.get("data", None) is None:
        try:
            event = preprocess.run(
                event,
                **storage_settings,
            )
        except Exception:
            event = {}
            # raise

    return event


def unique_path(directory, name_pattern):
    counter = 0
    while True:
        counter += 1
        path = directory / name_pattern.format(counter)
        if not path.exists():
            return path
