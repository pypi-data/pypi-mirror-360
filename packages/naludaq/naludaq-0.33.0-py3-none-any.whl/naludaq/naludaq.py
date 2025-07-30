"""Facade for all the underlying controllers.

This is the class to import to talk to all aspects of the board.
It contains all the aspects of the board.
Talk to the board,
receive data
setup connection
generate pedestals
storing data.
"""
import os
import time
from collections import deque
from copy import deepcopy
from logging import getLogger

from naludaq.backend import AcquisitionManager, RemoteAcquisition
from naludaq.backend.exceptions import BackendError
from naludaq.board import init_hardware, startup_board
from naludaq.controllers import get_board_controller, get_readout_controller
from naludaq.daq import LightDaq as DataAcquisitionController
from naludaq.daq.hiperdaq import HiperDaq as hDAQ
from naludaq.daq.preprocess import Preprocess
from naludaq.helpers import event_transfer_time
from naludaq.io import io_manager
from naludaq.tools.pedestals import get_pedestals_controller
from naludaq.tools.waiter import EventWaiter

LOGGER = getLogger(__name__)


class NaluDaq:
    """High-Level interface for the Naludaq using interactive or GUI.

    Creates an interface to the different components required to run the board.

    Args:
        board_model(str): The model of the board.
        working_dir(str): location on disk to store data.
    """

    def __init__(self, board, working_dir, start_workers=True):
        self.board = board
        if not os.path.isdir(working_dir):
            raise NotADirectoryError(
                f"NaluDaq init, directory not found: {working_dir}"
            )

        if not self.board.using_new_backend:
            self.daq = DataAcquisitionController(board, working_dir, start_workers)
            self.daq.preprocess = Preprocess(board)

        self.readout_settings = {
            "trig": "ext",
            "lb": "trigrel",
            "acq": "raw",
            "ped": "zero",
            "readoutEn": True,
            "singleEv": False,
        }

        self.is_capturing = False
        self.is_connected = False

    def init_board(self) -> bool:
        """Initializes hardware.

        Runs through the board initialization sequence.
        This initialization is board/model specific and requires the correct boardparams.
        It also requires an active connection with the board.

        Returns:
            True if the init is successful.
        """
        return init_hardware(self.board)

    def reset_board(self):
        """Reset the board.

        Sends a digital reset command to the board and resets the fpga.
        It will not wipe any settings made by the user.
        """
        get_board_controller(self.board).digital_reset()
        time.sleep(0.25)
        get_board_controller(self.board).digital_reset()

    def generate_pedestals(self):
        """Generate pedestals.

        Generate pedestals for the supplied board.
        """
        get_pedestals_controller(self.board).generate_pedestals()

    def save_current_pedestals_to_disk(self, filename):
        """Save current generated pedestals.

        Args:
            filename(str): full, correct path.
        """
        self.save_pedestals_to_disk(self.board.pedestals, filename)

    def save_pedestals_to_disk(self, pedestals, filename):
        """Save pedestals.

        Args:
            filename(str): full, correct path.
        """
        get_pedestals_controller(self.board).save_pedestals(pedestals, filename)

    def load_pedestals_from_disk(self, filename):
        """Save pedestals.

        Args:
            filename(str): full, correct path.
        """
        return get_pedestals_controller(self.board).load_pedestals(filename)

    def export_pedestals_as_csv(self, pedestals, filename):
        """Save pedestals.

        Args:
            pedestals(Pedestals): Pedestals object to save.
            filename(str): full, correct path.
            time_per_channel (bool): export time per channel rather than per row.
        """
        io_manager.IOManager().export_pedestals_csv(self.board, filename, pedestals)

    def reset_pedestals(self):
        """Reset pedestals data, the pedestals and set the pedestals to None."""
        self.board.pedestals = None

    def change_trigger_value(self, channel, value):
        """Set the trigger ADC for a specific channel.

        Trigger value is the value the board will trigger on
        in triggered mode.

        By setting this value !=0 the board will trigger on that channel.
        It's possible to trigger on multiple channels.

        Args:
            channel(int): Channel number to trigger on.
            value(int): Value to trigger on.
        """
        self.board.trigger.values[channel] = value

    def update_triggers(self):
        """Send all the trigger settings to the board."""
        self.board.trigger.write_triggers()

    def set_readout_settings(self, readout_settings):
        """Updates all the trigger values at once

        Args:
            readout_settings(dict):
                trig:
                lb:
                acq:
                ped:
                readoutEn:
                singleEv:
        """
        self.readout_settings = readout_settings

    def start_acquisition(self, readouts=0):
        """Start acquiring data from the board and store it.

        Make sure to swap the output storage before starting.

        Args:
            readouts(int): Maximum amount of readouts, 0 = infinite
        """
        self.update_triggers()
        if readouts > 0:
            self.readout_settings["singleEv"] = True
            get_readout_controller(self.board).number_events_to_read(readouts)
        else:
            self.readout_settings["singleEv"] = False

        self.is_capturing = True
        if not self.board.using_new_backend:
            self.reset_pkg_num()
            self.daq.start_capture()

        get_board_controller(self.board).start_readout(**self.readout_settings)

    def stop_acquisition(self):
        """Stop acquiring data."""
        try:
            get_board_controller(self.board).stop_readout()
        except Exception as error_msg:
            LOGGER.warning("stop_acquisition can't stop due to: %s", error_msg)
        self._stop_capture()

    def _stop_capture(self):
        if self.board.using_new_backend:
            try:
                AcquisitionManager(self.board).current_acquisition = None
            except BackendError as e:
                LOGGER.error("Failed to stop capture: %s", e)
        else:
            self.daq.stop_capture()
            LOGGER.debug("Buffers: %r", self.daq.get_buffer_levels())
        self.is_capturing = False

    def change_output(self, acquisition):
        """Set the output storage.
        Appends parsed events to the storage.
        Can be either a deque or an Acquisition.

        """
        if self.board.using_new_backend:
            # TODO
            pass
        else:
            pedestals = deepcopy(self.board.pedestals)
            caldata = deepcopy(self.board.caldata)
            acquisition.caldata = caldata
            acquisition.pedestals = pedestals
            self.daq.switch_output_buffer(acquisition)

    def peek_latest_event(self) -> dict:
        """Attempt to retrieve the latest event received.

        Raises:
            IndexError: if the last event could not be read.

        Returns:
            dict: the raw event
        """
        event = None
        if self.board.using_new_backend:
            acq = AcquisitionManager(self.board).current_acquisition
            if acq is None:
                raise IndexError("Current Acquisition is not set.")
            try:
                event = acq[-1]
            except IndexError as e:
                raise e
        else:
            try:
                event = self.daq.peek_latest_event()
            except IndexError as e:
                raise e
        return event

    def change_disk_storage_directory(self, directory):
        """Save data to this folder.

        Args:
            directory: Path to a directory on disk.

        Raises:
            NotADirectoryError if directory is not found.
        """
        if self.board.using_new_backend:
            return
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"{directory} is not a valid directory.")

        self.daq.storage_directory = directory
        LOGGER.debug("Storage directory set to: %s", directory)

    def enable_disk_storage(self, enable):
        """Enable/disable store raw/parsed to disk.

        Activate the processes to store raw packages and/or parsed data to disk.
        The default directory is the project directory.
        Starts a separate thread for each data type, tapping in on the data pipeline
        and storing to the disk.

        Args:
            to_store(str): what to enable/disable "raw" or "parsed" storage
            enable(bool): Set True to enable.
        """
        if self.board.using_new_backend:
            return
        self.daq.store_to_disk = enable
        LOGGER.debug("Naludaq enable disk storage: %s", enable)

    def reset_pkg_num(self):
        """Reset the package number counter"""
        if not self.board.using_new_backend:
            self.daq.pkg_num = 0

    def update_storage_settings(self, storage_settings):
        """Updates the flags used when storing events to disk, these flags
        sets what the Preprocess does to raw events. The dict can contain
        any combination of keys.

        Args:
            storage_settings (dict): {
                correct_pedestals:
                convert_adc2mv:
                correct_timing:
                convert_samples2time:
                process_in_place:
            }
        """
        if self.board.using_new_backend:
            return
        self.daq.storage_settings = storage_settings

    def select_readout_channels(self, channels_to_read):
        """Set the channels to read on the board

        Args:
            channels_to_read: List of channel numbers to readout.

        """
        get_readout_controller(self.board).set_readout_channels(channels_to_read)

    def change_board(self, board):
        """Resetting connection to hardware, reset data acquisition and change connection.

        It will reset the connection even if the new connection params are
        the same as the old parameters.
        Need to reconnect after a change of the board.

        Args:
            board_model(str): Boardmodel, if none is given, demoboard is assumed.
        """
        if self.is_connected:
            self.disconnect()
            if self.board.using_new_backend:
                AcquisitionManager(self.board).current_acquisition = None
            else:
                self.daq.stop_capture()
            self.is_connected = False

        # update board_controller, reinitialize
        self.board = board

        # redistribute board controller
        try:
            self.daq.board = self.board
        except Exception:
            pass

    def connect(self, connection_params) -> bool:
        """Connect to the board using the set connection settings.

        Args:
            connection_params(dict):
                {"type": type of connection
                "model": Board model
                "usb_port": COM port or ttyUSB
                "usb_rate": Baud rate for uart
                "ip_addr": ip address XXX.XXX.XXX.XXX
                "ip_port": port}

        Returns:
            True if connection.
            False if connection failed.
        """
        # TODO(Marcus): Logic might be outdated, board carries to conection_params, check if this is a valid function.
        try:
            self.is_connected = startup_board(self.board)
        except (AttributeError, ConnectionError) as e_msg:
            LOGGER.error("Connect(): %s", e_msg)
            self.is_connected = False

        return self.is_connected

    def disconnect(self):
        """Disconnect gracefully from the board.

        If the connection is a serial connection it will try and lower the
        baudrate before closing.
        This will prevent the board to listen at 3M baud and the startup
        baudmatching will be much quicker.
        """
        try:
            self.board.disconnect()
        except AttributeError:
            pass
        self.board.connection = None
        self.is_connected = False
        LOGGER.debug("Board disconnected.")

    def quit(self):
        """Close connection and stop all threads/processes."""
        self.stop_acquisition()
        if not self.board.using_new_backend:
            self.daq.stop_workers()
        self.disconnect()


class UpacDaq(NaluDaq):
    """Special HACK adapter for the upac board.

    Need to be cleaned up with a proper factory.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_mode = "00"
        self.read_amount = 0

    def capture_event(self):
        """ARGH, UGLY HACK Function for software trigger!

        Seriously, AARGHH!

        """
        self.is_capturing = True
        bc = get_board_controller(self.board)
        bc.clear_buffer()
        new_buffer_size = self._current_output_buffer_len() + 1
        if not self.board.using_new_backend:
            self.daq.start_capture()

        time.sleep(0.1)
        bc.start_readout(self.trigger_mode)
        bc.toggle_trigger()
        bc.stop_readout()
        timeout = event_transfer_time(
            self.board,
            self.board.params["windows"],
            overhead=3,
        )
        waiter = EventWaiter(
            buffer=self._output_buffer(),
            amount=new_buffer_size,
            interval=0.2,
            timeout=timeout,
        )
        LOGGER.debug("Using timeout for capture: %s sec", timeout)

        try:
            waiter.start(blocking=True)
        except TimeoutError:
            raise
        finally:
            self._stop_capture()
            # self.read_amount = self.daq.pkg_num

    def reread_event(self):
        """"""
        new_buffer_size = self._current_output_buffer_len() + 1
        prev_capturing = self.is_capturing
        if not self.is_capturing:
            start_readout = self.board.model not in ["upac96"]
            self.start_acquisition(start_readout)
        get_board_controller(self.board).toggle_reread()  # toggle_trigger()

        timeout = event_transfer_time(
            self.board, self.board.params["windows"], overhead=3
        )
        waiter = EventWaiter(
            buffer=self._output_buffer(),
            amount=new_buffer_size,
            interval=0.2,
            timeout=timeout,
        )
        LOGGER.debug("Using timeout for capture: %s sec", timeout)

        try:
            waiter.start(blocking=True)
        except TimeoutError:
            raise
        finally:
            if not prev_capturing:
                self.stop_acquisition()
        # self.read_amount = self.daq.pkg_num
        # self.is_capturing = False

    def start_acquisition(self, start_readout: bool = True):
        """Start acquiring data from the board and store it.

        On certain boards starting the readout blocks the re-read functionality.
        Consult the firmware/ASIC documentation! (What documentation..?)
        Make sure to swap the output storage before starting.

        Args:
            start_readout (bool): whether to send the command to start
                the readout.
        """
        LOGGER.debug("STARTING, %s", self.trigger_mode)

        self.is_capturing = True
        self.reset_pkg_num()
        if not self.board.using_new_backend:
            self.daq.start_capture()
        if start_readout:
            get_board_controller(self.board).start_readout(self.trigger_mode)

    def stop_acquisition(self):
        """Stop acquiring data."""
        super().stop_acquisition()
        self.reset_pkg_num()

    def _output_buffer(self) -> "deque | RemoteAcquisition":
        """Returns the output buffer

        Returns:
            "deque | RemoteAcquisition": the output buffer
        """
        if self.board.using_new_backend:
            return AcquisitionManager(self.board).current_acquisition
        else:
            return self.daq.output_buffer

    def _current_output_buffer_len(self) -> int:
        """Get the current number of events in the output buffer"""
        if self.board.using_new_backend:
            return len(AcquisitionManager(self.board).current_acquisition or [])
        else:
            return len(self.daq.output_buffer)


class HiperDaq(NaluDaq):
    """Special HACK adapter for the upac board.

    Need to be cleaned up with a proper factory.
    """

    def __init__(self, board, working_dir, *args, start_workers=True, **kwargs):
        super().__init__(board, working_dir, start_workers=True)
        if not self.board.using_new_backend:
            self.daq = hDAQ(self.board, working_dir, start_workers)
            self.daq.preprocess = Preprocess(board)
        self.chips: list = [0]
        self.read_amount = 0
        self.readout_settings = {
            "trig": "ext",
            "lb": "forced",
            "acq": "raw",
            "dig_head": False,
            "ped": "zero",
            "readoutEn": True,
            "singleEv": False,
        }

    def select_readout_chips(self, chips_to_read):
        self.chips = chips_to_read

    def reset_board(self):
        """Reset the board.

        Sends a digital reset command to the board and resets the fpga.
        It will not wipe any settings made by the user.
        """
        get_board_controller(self.board).reset_board()

    def capture_event(self):
        """Send a trigger pulse to the board"""
        get_board_controller(self.board).toggle_trigger()

    def start_acquisition(self):
        """Start acquiring data from the board and store it.

        Make sure to swap the output storage before starting.

        Args:
            readouts(int): Maximum amount of readouts, 0 = infinite
        """
        self.is_capturing = True
        bc = get_board_controller(self.board)
        self.daq.pkg_num = 0
        self.daq.start_capture()
        bc.start_readout(**self.readout_settings)

    def stop_acquisition(self):
        """Stop acquiring data."""
        if self.board.connection is not None:
            try:
                get_board_controller(self.board).stop_readout()  # Nuke the board
            except Exception as error_msg:
                LOGGER.warning("stop_acquisition can't stop due to: %s", error_msg)
        self.daq.stop_capture()
        self.daq.pkg_num = 0
        self.is_capturing = False
        self.daq.get_buffer_levels()
