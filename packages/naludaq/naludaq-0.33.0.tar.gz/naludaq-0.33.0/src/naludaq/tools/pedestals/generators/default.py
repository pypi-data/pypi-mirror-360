"""Default pedestals generator.

Background:

    Pedestals are used to compensate for imperfections in the chip manufacturing
    process, by capturing enough events from the storage array it's possible to
    statistically rule out data originating from these imperfections rather
    than the real world event.


The pedestals generator essentially captures enough events to contain several data points from the entire sampling array
and averages them to create a "pedestal value" for each sample. Most boards allow portions of the sampling array to be
read out (known as "blocks"), while others require the entire sampling array to be read out (e.g. UDC16).

It is recommended that a few warmup events be included in the pedestals generation parameters. This allows the board
to settle and lessens the effect of temperature drift on the pedestals.

Developers:

    Specialized pedestals generators may exist for different for different boards, but all should be
    based on this class. A common base will provide the highest level of compatibility and maintainability.

    The data capture portion of the pedestals generation revolves around the data collector. Check out the documentation
    if you are unfamiliar with it. A highly-extensible pipeline is created from the data collector which handles validation,
    progress reporting, cancelling, and warmup events. The data collector handles the lower-level details and lets the
    pedestals generator avoid worrying about board intrinsics and handling hardware-related errors & edgecases.

    Because of the inherent uncertainty of the hardware, pedestals generation can fail unexpectedly and frequently. It is
    important to provide descriptive and helpful error messages to the user. A good error message should include a reason
    why the pedestals generation failed, what the user can do to fix it, and what to do if that doesn't work.
"""
import copy
import gzip
import logging
import math
import os
import pickle
from functools import partial
from typing import Iterable

import numpy as np

from naludaq.board import Board
from naludaq.communication import ControlRegisters, DigitalRegisters
from naludaq.controllers import get_readout_controller
from naludaq.helpers import FancyIterator, validations
from naludaq.helpers.exceptions import (
    IterationError,
    OperationCanceledError,
    PedestalsDataCaptureError,
    PedestalsIOError,
)
from naludaq.tools.data_collector import get_data_collector
from naludaq.tools.metadata import Metadata
from naludaq.tools.pedestals.pedestals_processor import is_outlier

LOGGER = logging.getLogger("naludaq.pedestals_controller")  # pylint: disable=invalid-name


class PedestalsGenerator:
    """Pedestals controller manages the pedestals generation.

    The pedestals are used to reduce noise originating from the chip itself.
    By capturing data from the board it's possible to use the mean value of x events to
    generate an average error for every sample. Since this average is
    an effect of the imperfections in the chip, subtracting the average counteracts
    the effect of the imperfections.

    The average is improving with 1/sqrt(n).

    This controller relies on an external data acquisiton capturing data to the
    .pedstore buffer it also relies on a board with an active connection to
    communicate with the hardware.

    The pedestals can then be used by the parser to remove the noise.

    Args:
        board:
        num_captures (int): Number of datapoints per sample, used for averaging the values.
        num_warmup_events (int): Number of initial events to discard. Helps the board
            settle and excludes events that may skew the pedestals.
        channels (list[int]): list of channels to generate pedestals for. Any channels excluded
            will result as `np.nan` in the generated pedestals.

    Attributes:
        num_captures: How many datapoints/samplepoint used to calculate the average.

    Raises:
        NotImplementedError if the given board does not support pedestals.
    """

    def __init__(
        self,
        board: Board,
        num_captures: int = 10,
        num_warmup_events: int = 10,
        channels=None,
        timeout_overhead=None,
    ):
        if not board.is_feature_enabled("pedestals"):
            raise NotImplementedError(
                f'Board "{board.model}" does not have support for pedestals.'
            )
        self._board = board

        self._progress = []
        self._cancel = False

        self.attempts = 10
        self.num_captures = num_captures
        self.num_warmup_events = num_warmup_events
        self.block_size = self.board.params["pedestals_blocks"]
        self._dc = get_data_collector(board)
        self.channels = channels or range(self.board.channels)

        self._dc.channels = self.channels
        self._dc.forced = True
        self._dc.timeout_overhead = timeout_overhead or self.board.params.get(
            "timeout_overhead", 10.0
        )
        self._current_block = 0
        self._current_start_window = 0
        self._debug_raw_events = []

    @property
    def filter_outliers(self) -> bool:
        """Get/set whether to filter outliers from the pedestals."""
        return self.board.params.get("pedestals", {}).get("filter_outliers", False)

    @filter_outliers.setter
    def filter_outliers(self, value: bool):
        """Set whether to filter outliers from the pedestals."""
        if not isinstance(value, bool):
            raise TypeError("filter_outliers must be a boolean value")
        self.board.params.get("pedestals", {})["filter_outliers"] = value

    @property
    def outlier_threshold(self) -> float:
        """Get/set the outlier threshold for pedestals."""
        return self.board.params.get("pedestals", {}).get("outlier_threshold", 30.0)

    @outlier_threshold.setter
    def outlier_threshold(self, value: float):
        """Set the outlier threshold for pedestals."""
        if not isinstance(value, (int, float)):
            raise TypeError("outlier_threshold must be a numeric value")
        self.board.params.get("pedestals", {})["outlier_threshold"] = value

    @property
    def board(self):
        """Get/set board for pedestals capture.

        Raises:
            NotImplementedError if the given board does not support pedestals.
        """
        return self._board

    @property
    def progress(self):
        """Get/Set the progress message queue.

        This is a hook the read the progress if running threads.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    @property
    def channels(self) -> list[int]:
        """Get/set the channels that will be read out. Any channels not enabled will result
        in NANs for that channel.
        """
        return self._dc.channels

    @channels.setter
    def channels(self, channels: Iterable[int]):
        validations.validate_channel_sequence_or_raise(self.board.params, channels)
        self._dc.channels = list(channels)

    @property
    def num_captures(self) -> int:
        """Get/set the number of events per block."""
        return self._num_captures

    @num_captures.setter
    def num_captures(self, num_captures: int):
        validations.validate_positive_int_or_raise(num_captures)
        self._num_captures = num_captures

    @property
    def num_warmup_events(self) -> int:
        """Get/set the number of warmup events per block."""
        return self._num_warmup_events

    @num_warmup_events.setter
    def num_warmup_events(self, num_warmup_events: int):
        validations.validate_non_negative_int_or_raise(num_warmup_events)
        self._num_warmup_events = num_warmup_events

    @property
    def block_size(self) -> int:
        """Get/set the number of windows per block"""
        return self._block_size

    @block_size.setter
    def block_size(self, block_size: int):
        validations.validate_positive_int_or_raise(block_size)
        if block_size > self.board.params["windows"]:
            raise ValueError("Block size cannot be larger than the number of windows")
        self._block_size = block_size

    @property
    def metadata(self) -> Metadata:
        """Get a proxy object to use for accessing pedestals metadata."""
        return Metadata(self.board.pedestals)

    @property
    def raw_events(self) -> list[dict]:
        """List of events used to last generate the pedestals.

        These events are parsed, and otherwise not modified in any way.
        They can be used for analysis! 🥳🎉
        """
        return self._debug_raw_events

    def generate_pedestals(self):
        """Generates pedestals and stores them in the board.pedestals.

        Pedestals stored on the board, they will be used on the next acquisition.

        If canceled, the board is set back to its previous state, and no pedestals
        are generated.
        """
        self._cancel = False
        old_pedestals = self.board.pedestals
        self._debug_raw_events = []

        self._update_progress(0, "Saving board state")
        backup = self._backup_settings()

        self.reset_pedestals()
        self._store_board_metadata()

        try:
            self._generate_pedestals_metadata_pre()
            blocks = self._capture_data_for_pedestals()
            self._generate_pedestals_metadata_post()
        except (OperationCanceledError, KeyboardInterrupt):
            self.board.pedestals = old_pedestals
        except:
            self.board.pedestals = old_pedestals
            raise
        else:  # else runs before finally if no error is raised
            self._update_progress(80, "Processing data")
            self._store_raw_data(blocks)
            if self.filter_outliers:
                self._generate_and_store_outlier_mask()
            self._store_averaged_data()
        finally:
            self._update_progress(90, "Restoring board state")
            self._restore_backup_settings(backup)

    def cancel(self):
        """Cancels the pedestals generation as soon as possible.
        No pedestals are generated, and the board is restored to
        its previous state.

        Can only be called from a separate thread.
        """
        self._cancel = True

    def reset_pedestals(self):
        """Remove the current pedestal data.

        Replaces the pedestals with a set of blank pedestals. All values set
        to zero with the shape set from board params.
        """
        self.board.pedestals = self._create_empty_pedestals(self._num_captures)

    def _backup_settings(self) -> dict:
        """Backup settings that might get overwritten to a dict.

        Returns:
            dict with the backup settings:
                'readout_channels',
                'control_registers',
                'digital_registers'
        """
        backup = {
            "readout_channels": get_readout_controller(
                self.board
            ).get_readout_channels(),
            "control_registers": copy.deepcopy(
                self.board.registers.get("control_registers", {})
            ),
            "digital_registers": copy.deepcopy(
                self.board.registers.get("digital_registers", {})
            ),
        }

        return backup

    def _restore_backup_settings(self, backup_settings: dict):
        """Restore all backuped settings to the board.

        Returns:
            True if settings have been restored, False if no old settings were found.
        """
        if not backup_settings:
            return

        channels = backup_settings.get("readout_channels", None)
        if channels is not None:
            get_readout_controller(self.board).set_readout_channels(channels)

        # Restore backup
        for register_space in ["control_registers", "digital_registers"]:
            backup_registers = backup_settings.get(register_space, None)
            if backup_registers is not None:
                self._update_registers(self.board.registers[register_space], backup_registers)
        DigitalRegisters(self.board).write_all()
        ControlRegisters(self.board).write_all()

    def _update_registers(self, base, back):
        for k, v in back.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                self._update_registers(base[k], v)
            else:
                base[k] = v
        return base

    # ================================================================================
    # Capture
    # ================================================================================
    def _capture_data_for_pedestals(self, *args, **kwargs) -> list[list[dict]]:
        """Capture raw data for pedestals.

        Returns:
            list[list[dict]]: list of data for blocks. Warmup events
                are removed from the output.

        Raises:
            PedestalsDataCaptureError: if pedestals failed to generate.
            OperationCanceledError: if pedestals generation was cancelled.
        """
        LOGGER.debug(
            "Capturing pedestals for %s. Block size=%s, channels=%s",
            self.board.model,
            self.block_size,
            self.channels,
        )
        self._current_block = 0
        blocks = []
        total_windows = self.board.params["windows"]
        for start_window in range(0, total_windows, self.block_size):
            self._raise_if_canceled()
            self._set_read_window(start_window)
            block = self._capture_block_or_raise(self._num_captures)
            blocks.append(block)
            self._current_block += 1
        return blocks

    def _capture_block_or_raise(self, captures: int) -> list[dict]:
        """Attempts to capture a data for the given block.

        Args:
            captures (int): number of events in the block (captures + warmup)

        Returns:
            list[dict]: list of events

        Raises:
            PedestalsDataCaptureError: if the necessary number of events could not be captured.
            OperationCanceledError: if pedestals generation was cancelled.
        """
        stages = self._create_data_pipeline()
        try:
            return stages.take(captures).collect()
        except (TimeoutError, IterationError) as e:
            LOGGER.error("Failed to generate pedestals: %s", e)
            msg = (
                "Failed to capture enough events. The board may be unresponsive "
                "and need to be power cycled/reinitialized."
            )
            raise PedestalsDataCaptureError(msg) from e
        except OperationCanceledError:
            raise

    def _create_data_pipeline(self) -> FancyIterator:
        """Create a chainable FancyIterator over the data.

        The iterator is unbounded, so it is necessary to `.take()` or limit the
        iterator in some fashion when actual data collection is performed.

        Subclasses can tack on additional stages to the chain to modify or filter the data.

        Default stages:
        - cancel check
        - progress update
        - event validation filter
        - skip warmup events
        """
        pipeline = self._dc.iter_inf(attempts=self.attempts)
        pipeline = pipeline.for_each(lambda _: self._raise_if_canceled)
        pipeline = self._create_validation_stage(pipeline)
        pipeline = self._create_progress_update_stage(pipeline)
        pipeline = pipeline.skip(self._num_warmup_events)
        return pipeline

    def _create_validation_stage(self, pipeline: FancyIterator) -> FancyIterator:
        """Create a stage that validates the captured data and filters out invalid events.

        Args:
            pipeline (FancyIterator): the pipeline to chain the new stage to
        """
        lookback = self._current_start_window
        expected = self._calculate_expected_window_labels(lookback, self.block_size)
        validator = partial(self._validate_event, expected_window_labels=expected)
        return pipeline.filter(validator, exclusion_limit=10)

    def _create_progress_update_stage(self, pipeline: FancyIterator) -> FancyIterator:
        """Create a stage that updates the progress message.

        Args:
            pipeline (FancyIterator): the pipeline to chain the new stage to
        """
        n_blocks = math.ceil(self.board.params["windows"] / self.block_size)
        events_per_block = self._num_warmup_events + self._num_captures
        total_events = n_blocks * events_per_block
        min_progress = 20
        max_progress = 80

        def inner(x):
            idx_in_block = x[0]
            abs_idx = self._current_block * events_per_block + idx_in_block
            percent = (
                min_progress + (max_progress - min_progress) * abs_idx / total_events
            )
            msg = (
                f"Capturing block {self._current_block + 1}/{n_blocks}, "
                f"event {idx_in_block + 1}/{events_per_block}"
            )
            self._update_progress(percent, msg)

        return pipeline.enumerate().for_each(inner).unenumerate()

    def _validate_event(self, event: dict, expected_window_labels: list[int]) -> bool:
        """Reimplemented to check all channels.

        Windows can be missing from individual channels on HDSoC.
        """
        for channel in self.channels:
            labels = event["window_labels"][channel]
            try:
                is_bad = np.any(labels != expected_window_labels)
            except Exception as error_msg:
                LOGGER.error(f"Event validation failed due to: {error_msg}")
                return False
            if is_bad:
                LOGGER.warning(
                    "Expected windows: %s != returned: %s",
                    expected_window_labels,
                    labels,
                )
                return False
        return True

    def _calculate_expected_window_labels(self, start_window, block_size) -> list[int]:
        """Calculate the expected window labels for a block.

        Args:
            start_window (int): start window of the block.
            block_size (int): Number of windows captured per block.

        Returns:
            List of expected window numbers.
        """
        windows = self.board.params["windows"]
        return np.arange(start_window, start_window + block_size) % windows

    def _read_window(self, start_window: int) -> tuple[int, int, int]:
        """Compute the read window based on the given start window.

        windows: set to block size
        lookback: set to the given start window
        write_after_trig: all windows
        """
        return (self.block_size, start_window, self.board.params["windows"])

    def _set_read_window(self, start_window: int):
        """Set the read window for the data collector."""
        window = self._read_window(start_window)
        self._current_start_window = window[1]
        self._dc.set_window(*window)

    # ================================================================================
    # Processing
    # ================================================================================
    def _create_empty_pedestals(self, num_captures: int):
        """Build the structure for raw pedestals data."""
        return {
            "data": np.full(
                shape=(
                    self.board.params["channels"],
                    self.board.params["windows"],
                    self.board.params["samples"],
                ),
                fill_value=np.nan,
            ),
            "rawdata": np.full(
                shape=(
                    self.board.params["channels"],
                    self.board.params["windows"],
                    self.board.params["samples"],
                    num_captures,
                ),
                fill_value=np.nan,
            ),
        }

    def _store_raw_data(self, blocks: list[list[dict]]):
        """Store raw data from blocks into the pedestals dict.

        Args:
            blocks (list[list[dict]]): blocks to store
        """
        block_size = self.block_size
        raw_data = self.board.pedestals["rawdata"]
        for block_idx, block in enumerate(blocks):
            for capture_number, event in enumerate(block):
                for chan in range(self.board.params["channels"]):
                    if chan not in self.channels:
                        continue
                    for window_num in range(block_size):
                        window = window_num + block_idx * block_size
                        # Avoid rolling over and overwrite block 0
                        if block_idx != 0 and (window < block_size):
                            continue
                        # avoid window number rolling over
                        if window >= self.board.params["windows"]:
                            continue
                        for sample in range(self.board.params["samples"]):
                            index = sample + window_num * self.board.params["samples"]
                            try:
                                data = event["data"][chan][index]

                                raw_data[chan, window, sample][capture_number] = data
                            except Exception:
                                LOGGER.debug(
                                    "Event doesn't contain data, block: %s, capnum: %s, chan %s, idx: %s",
                                    block_idx,
                                    capture_number,
                                    chan,
                                    index,
                                )

    def _generate_and_store_outlier_mask(self):
        """Generate pedestals outlier mask from raw data.

        Will create a mask for each individual sample in each individual event.
        The mask will be set to True for outliers, and False for normal values.
        """
        self.board.pedestals["outlier_mask"] = np.empty(
            shape=self.board.pedestals["rawdata"].shape, dtype=np.intp
        )
        threshold = self.outlier_threshold
        for chan in range(self.board.channels):
            chan_ped_data = self.board.pedestals["rawdata"][chan]
            chan_outlier_indexes = is_outlier(chan_ped_data, threshold, axis=None)
            self.board.pedestals["outlier_mask"][chan] = chan_outlier_indexes

    def _store_averaged_data(self):
        """Generate processed pedestals data from the raw data."""
        raw_data = self.board.pedestals["rawdata"].copy()
        if self.filter_outliers:
            raw_data = np.where(self.board.pedestals["outlier_mask"], np.nan, raw_data)
        self.board.pedestals["data"] = np.nanmean(raw_data, axis=3)

    # ================================================================================
    # Metadata
    # ================================================================================
    def _generate_pedestals_metadata_pre(self):
        """Adds some metadata to the pedestals dict. Called immediately
        before the pedestals data will be captured.
        """
        self._store_board_metadata()
        self._store_sensor_readings()

    def _generate_pedestals_metadata_post(self):
        """Adds some metadata to the pedestals dict. Called immediately
        after the pedestals data has been captured.
        """
        self._store_sensor_readings()

    def _store_board_metadata(self):
        """Store board params/registers into pedestals metadata"""
        self.metadata.set_configuration(self.board)

    def _store_sensor_readings(self):
        """Store sensor readings into pedestals metadata"""
        LOGGER.debug("Storing sensor metadata")
        self.metadata.store_sensor_readings(self.board)

    # ================================================================================
    # Import/Export
    # ================================================================================
    @staticmethod
    def save_pedestals(pedestals, filename):  # TODO(v.0.1.23): Use IO module.
        """Save the pedestal in binary format for backwards compatibility."""
        if not isinstance(pedestals, dict):
            raise TypeError(f"pedestals must be a dict, got {type(pedestals)}")
        if filename is None:
            raise TypeError("Supplied pathname is NoneType.")
        path, _ = os.path.split(filename)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a valid directory: {path}")

        try:
            with gzip.GzipFile(filename, "wb", compresslevel=4) as f:
                pickle.dump(pedestals, f, protocol=pickle.HIGHEST_PROTOCOL)
        except IOError as e:
            raise PedestalsIOError(f"File could not be written: {e}")
        except pickle.PicklingError as e:
            raise PedestalsIOError(f"Object cannot be serialized: {e}")

    def load_pedestals(self, filename):  # TODO(v.0.1.23): Use IO module.
        """Load the pedestal gziped and pickled.

        The pedestals object is loaded to both self.pedestals
        and is returned.

        Args:
            filename: valid filename

        Returns:
            Pedestals data.
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"No file found: {filename}")
        try:
            with gzip.GzipFile(filename, "rb") as f:
                outped = pickle.load(f)
        except EOFError:
            raise PedestalsIOError("Unexpected end of file")
        except IOError as e:
            raise PedestalsIOError(f"File could not be loaded: {e}")
        except pickle.UnpicklingError as e:
            raise PedestalsIOError(f"Not a valid pickle file: {e}")
        else:
            if not isinstance(outped, dict):
                raise TypeError(f"Not a valid Pedestals file: {filename}")
            self.board.pedestals = outped
            return outped

    # ================================================================================
    # Helpers
    # ================================================================================

    def _raise_if_canceled(self):
        """Raise an ``OperationCanceledError`` if the cancel flag is set."""
        if self._cancel:
            raise OperationCanceledError("Pedestals generation was canceled.")

    def _update_progress(self, percent: float, message: str):
        """Updates a progress "receiver" with a percent and message.

        The receiver can be a list or deque of (percent, message) tuples,
        or a ProgressDialog (for use with NaluScope).

        Args:
            percent (float): the percent completion of the task
            message (str): a description of what is currently taking place
        """
        progress = self._progress
        if progress is None:
            LOGGER.debug("%s | %s", percent, message)
            return
        else:
            progress.append((percent, message))
