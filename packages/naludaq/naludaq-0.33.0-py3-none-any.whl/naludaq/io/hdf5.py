"""Class for saving/loading acquisitions, events, and pedestals
in HDF5 format. See the README for more information on the data format.

Events are grouped into sets of fixed size called "blocks." The
events within a block are stitched together into large matrices.
Storing the events in blocks is necessary because for extremely
large events, a single matrix is too much for HDF5 to handle.
Additionally, this opens up the possibility for writing data to disk
as soon as it comes back from the board.
"""
import itertools
import logging
import math
import os
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Deque, List, Union

import h5py
import numpy as np

import naludaq
from naludaq.board import Board
from naludaq.board.params import _calculate_channel_shift
from naludaq.helpers.exceptions import BadDataError
from naludaq.models import Acquisition, acq_converters
from naludaq.parsers import get_parser

LOGGER = logging.getLogger(__name__)


# Used to load values as the correct type
_DATETIME_CONVERTER = lambda x: datetime.fromtimestamp(x)
_PATHLIB_CONVERTER = lambda x: Path(x)
_BYTES_CONVERTER = lambda x: x[()].tobytes()
_INT_CONVERTER = lambda x: int(x)


class HDF5File:
    def __init__(
        self, path: Path, mode: str, board: Board, compression="gzip", block_size=1024
    ) -> None:
        """IO class for reading and writing NaluDAQ data structures
        to/from an HDF5 file.

        # WARNING
        This class cannot handle events from boards other than specified in the
        `board` argument.

        Args:
            path (Path): the path of the file to read/write
            mode (str): the mode, either 'r' (read) or 'w' (write)
            board (Board): the board object. If mode='r', then can be None.
            compression (str): the compression format to use when writing datasets.
                Must be 'gzip' or None.
            block_size (int): the maximum number of events that can fit inside a block.

        Raises:
            PermissionError if the file cannot be opened
            FileNotFoundError if reading and the file does not exist
            BaseException in any other cases (TODO: determine cases)
        """
        if type(mode) != str:
            raise TypeError(f"Mode must be a string, not {type(mode)}")
        elif mode.lower() not in ["r", "w"]:
            raise ValueError(f"Mode must be either 'r' or 'w', not {mode}")
        elif not isinstance(path, (str, Path)):
            raise TypeError(f"Path must be str or Path, not {type(path)}")
        elif type(board) != Board and mode.lower() == "w":
            raise TypeError(f"Board must be a naludaq.board.Board, not {type(board)}")
        elif compression is not None and type(compression) != str:
            raise TypeError(f"Compression must be a string, not {type(compression)}")
        elif compression not in ["gzip", None]:
            raise ValueError(f"Compression must be 'gzip' or None, not {compression}")
        elif type(block_size) != int:
            raise TypeError(f"Block size must be an int, not {type(block_size)}")
        elif block_size <= 0:
            raise ValueError(f"Block size must be positive")

        self.path = Path(path)
        self._board = board
        self._cancel = False
        self._progress = []
        self._mode = mode
        self._compression = compression
        self._block_size = block_size

        try:
            self._file = h5py.File(str(self.path), self._mode)
        except PermissionError as e:
            LOGGER.error(f"Cannot open file: {e}")
            raise e
        except FileNotFoundError as e:
            LOGGER.error(f"File does not exist: {e}")
            raise e
        except BaseException as e:
            LOGGER.error(f"Failed to import HDF5 acquisition: {e}")
            raise e

    @property
    def has_events(self) -> bool:
        """Gets whether the file contains events."""
        return "events" in self._file

    @property
    def has_metadata(self) -> bool:
        """Gets whether the file contains acquisition metadata."""
        return "metadata" in self._file

    @property
    def has_pedestals(self) -> bool:
        """Gets whether the file contains pedestals calibration data."""
        return "pedestals" in self._file.get("calibration", {})

    @property
    def has_caldata(self) -> bool:
        """Gets whether the file contains adc2mv calibration data."""
        return "caldata" in self._file.get("calibration", {})

    @property
    def has_timingcal(self) -> bool:
        """Gets whether the file contains timing calibration data."""
        return "timingcal" in self._file.get("calibration", {})

    @property
    def num_events(self) -> int:
        """Gets the number of events the file contains."""
        if self.has_events:
            return self._file["events"].attrs["event_count"]
        else:
            return 0

    @property
    def num_blocks(self) -> int:
        """Gets the number of blocks the file contains."""
        if self.has_events:
            return len(self._file["/events/blocks"])
        return 0

    @property
    def block_size(self) -> int:
        """Gets the size of event blocks.

        If mode is 'r' and the acquisition contains events,
        the block size specification contained in the file is returned.
        Otherwise, the value specified in this class' constructor
        is returned.
        """
        if self._mode == "r" and self.has_events:
            return self._file["events"].attrs["max_block_size"]
        return self._block_size

    @property
    def enabled_channels(self):
        """Gets a list of enabled channels stored in the file.
        Returns None if the file is not an acquisition.
        """
        if self.has_events:
            return list(self._file["events"].attrs["enabled_channels"][()])
        return None

    @property
    def num_channels(self):
        """Gets the total number of channels from the file.
        Returns 0 if the file is not an acquisition.
        """
        if self.has_events:
            return self._file["events"].attrs["channel_count"]
        elif self.has_metadata:
            return self._file["metadata"]["settings"]["params"].attrs["channels"]
        return 0

    @property
    def progress(self):
        """Get/set the progress list. In a multithreaded context this can be used to read the
        status of a long-running function.

        When setting the progress list, the object must have an `append` method.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, _, __):
        """Exit method for context manager. Closes the file.

        If the `cancel()` method was called or an exception was raised
        while writing, the partial output file is removed.
        """
        try:
            self._file.close()
        except:
            pass

        # Remove partial file if erred or canceled
        if self._mode == "w" and (exc_type or self._cancel):
            try:
                os.remove(self.path)
            except:
                pass

        self.progress.append((100, "Done"))

    def cancel(self):
        """Cancels any and all IO operations as soon as possible.
        If writing, the output file is deleted.
        If reading, no result is returned.

        Can only be called from a separate thread.
        """
        self._cancel = True

    # ============================= Write Operations =============================
    def write_acquisition(
        self,
        acq: Union[deque, list, Acquisition],
        calibration: bool = True,
        metadata: Union[bool, Acquisition] = True,
    ):
        """Writes an acquisition to the file.

        # WARNING
        All events given must be from the _same_ acquisition, or this function
        may fail.

        Args:
            acq (deque, list, or Acquisition): the acquisition to write.
            calibration (bool, dict): whether to include pedestals in the output file.
            metadata (bool, Acquisition): whether to include acquisition metadata
                in the output file. If `metadata` is an Acquisition object,
                it is used as the source of metadata for the output file -- this is
                useful if `acq` is a subset of an original acquisition.

        Raises:
            TypeError if one or more of the arguments are of an invalid type.
            ValueError if the acquisition or pedestals are in an invalid format.
        """
        if not isinstance(acq, (deque, list, Acquisition)):
            raise TypeError(
                f"'acq' must be a deque, list, or Acquisition, not {type(acq)}"
            )
        elif not isinstance(calibration, bool):
            raise TypeError(
                f"'calibration' must be a bool or dict, not {type(calibration)}'"
            )
        elif not isinstance(metadata, (bool, Acquisition)):
            raise TypeError(
                f"'metadata' must be a bool or Acquisition, not {type(metadata)}"
            )
        elif len(acq) == 0:
            raise ValueError("Must have at least one event!")

        self.write_events(acq)

        if calibration and not self._cancel:
            self.progress.append((95, "Writing calibration"))
            self.write_calibration(acq)

        if metadata and not self._cancel:
            self.progress.append((99, "Writing acquisition metadata"))
            self.write_metadata(acq)

    def write_events(self, events: Union[Deque[dict], List[dict]]):
        """Writes a bunch of events to the file.

        Data is stored into the 'events' group as a handful of datasets.
        Each dataset stores a particular attribute of _all_ events,
        and are indexed by the event number.

        Channels that are disabled (i.e. empty in the event data) are _not_
        written to the datasets in order to save space. The channel number
        corresponding to an axis in the datasets can be determined by the
        'enabled_channels` attribute.

        Args:
            events (deque, list): a deque or list of events.

        Raises:
            ValueError if there is not at least one event.
            BadDataError if there are no valid events in the acquisition
        """
        if not events:
            raise ValueError("Acquisition must have at least one event.")

        # Look ahead to the first valid event to get shape characteristics since
        # self._board cannot be trusted to have the same model/settings as the acquisition
        try:
            attrs = self._get_acq_attributes(events)
            enabled_channels = attrs["enabled_channels"]
            channel_count = attrs["channel_count"]
        except BadDataError:
            raise

        # Block size specified by user
        num_events = len(events)
        num_blocks = math.ceil(num_events / self._block_size)

        events_group = self._file.create_group("events")
        events_group.attrs["max_block_size"] = self._block_size
        events_group.attrs["event_count"] = num_events
        events_group.attrs.create(
            "enabled_channels", np.array(enabled_channels), dtype=np.uint16
        )
        events_group.attrs.create("channel_count", data=channel_count)

        block_links = events_group.create_dataset(
            "blocks", shape=(num_blocks,), dtype=h5py.ref_dtype
        )

        # Split events into blocks and write
        for block_idx in range(num_blocks):
            LOGGER.info(f"Writing block ({block_idx+1}/{num_blocks})")
            self.progress.append(
                (
                    85 * block_idx / num_blocks,
                    f"Writing block ({block_idx+1}/{num_blocks})",
                )
            )

            if block_idx == num_blocks - 1:
                block_events = list(
                    itertools.islice(events, block_idx * self._block_size, num_events)
                )
            else:
                block_events = list(
                    itertools.islice(
                        events,
                        block_idx * self._block_size,
                        (block_idx + 1) * self._block_size,
                    )
                )

            block_group = events_group.create_group(f"block_{block_idx}")
            block_links[block_idx] = block_group.ref
            self._write_event_block(block_group, block_events, attrs)
            if self._cancel:
                return

    def _write_event_block(self, group: h5py.Group, events: list, attrs: dict):
        """Writes a list of events to a block group.

        Args:
            parser (Parser): the parser to use for unprocessed events
            group (h5py.Group): the block group
            events (list): the events to write
            attrs (dict): the acquisition attributes from `_get_acq_attributes()`
        """
        parser = attrs["parser"]
        num_events = len(events)

        window_label_shape = attrs["window_labels"]
        channels, samples = attrs["event_data"]
        enabled_channels = attrs["enabled_channels"]

        # Allocate a bunch of empty arrays, one for each type of event property
        data = np.full((num_events, channels, samples), fill_value=0, dtype=np.uint16)
        window_labels = np.full(
            (num_events, *window_label_shape), fill_value=0, dtype=np.uint16
        )
        time = np.full((num_events, channels, samples), fill_value=0, dtype=np.uint16)
        pkg_nums = np.empty((num_events,), dtype=np.uint32)
        event_nums = np.empty((num_events,), dtype=np.uint32)
        start_windows = np.empty((num_events,), dtype=np.uint32)
        creation_times = np.empty((num_events,), dtype=np.uint64)
        bad_events = []
        event_names = {}  # Mapping of event_idx: name

        # Load up the arrays before writing to disk. One row in the arrays corresponds to one event
        for idx, event in enumerate(events):

            # Some stuff needs to be stored before parsing, in case the event is bad
            pkg_nums[idx] = event.get("pkg_num", 0)
            event_nums[idx] = event.get("event_num", 0)

            # Storing names for all events is wasteful; only store user-defined names
            name = event.get("name", None)
            if name:
                event_names[idx] = name.encode("ascii")

            # HDF5 acquisitions need parsed data
            if "data" not in event:
                try:
                    parsed = parser.parse(event)
                    parsed["name"] = event.get("name", None)
                except BadDataError as e:
                    LOGGER.info(f"Event {idx} not saved due to parsing error: {e}")
                    bad_events.append(idx)
                    continue
            else:
                parsed = event

            # Some channels may be disabled, need to store channel-by-channel.
            for chan_idx, chan in enumerate(enabled_channels):
                data[idx, chan_idx, :] = np.array(parsed["data"][chan])
                window_labels[idx, chan_idx, :] = np.array(
                    parsed["window_labels"][chan]
                )
                # if idx <= 10:
                # print(parsed['time'][chan])
                time[idx, chan_idx, :] = np.array(parsed["time"][chan], dtype=np.uint16)

            start_windows[idx] = parsed["start_window"]
            creation_times[idx] = parsed["created_at"]

            if self._cancel:
                return

        # Write all the arrays and whatnot to the file
        # self.progress.append((90, 'Storing events'))
        group.create_dataset("package_numbers", data=pkg_nums, dtype=np.uint32)
        group.create_dataset("event_numbers", data=event_nums, dtype=np.uint32)
        group.create_dataset("start_windows", data=start_windows, dtype=np.uint16)
        group.create_dataset("creation_times", data=creation_times, dtype=np.uint64)
        group.create_dataset(
            "window_labels",
            data=window_labels,
            dtype=np.uint16,
            compression=self._compression,
            compression_opts=9,
        )
        group.create_dataset(
            "data",
            data=data,
            dtype=np.uint16,
            compression=self._compression,
            compression_opts=9,
        )
        group.create_dataset(
            "time",
            data=time,
            dtype=np.uint16,
            compression=self._compression,
            compression_opts=9,
        )
        if bad_events:
            dataset = np.array(bad_events, dtype=np.uint)
            group.attrs.create("bad_events", data=dataset, dtype=np.uint)
        if event_names:
            # A list of ([event #, event name]), ends up being saved as an array of [bytes, bytes]
            event_names = np.array(list(event_names.items()))
            group.attrs.create(
                "names",
                shape=(len(event_names), 2),
                data=event_names,
                dtype=event_names.dtype,
            )

    def _get_acq_attributes(self, events: Union[Deque[dict], List[dict], Acquisition]):
        """Finds the shape of window labels/event data datasets and the enabled channels
        based on the first good event in the acquisition.

        Args:
            events (deque, list, Acquisition): the acquisition

        Raises:
            BadDataError if there are no valid events

        Returns:
            A dict of {
                'window_labels': (channel count, window count),
                'event_data': (channel count, sample count),
                'enabled_channels': [0, 1, 2, 3, 4, ...]
            }
        """
        parser = get_parser(_get_params(events, self._board))

        # Look ahead to the first valid event to get shape characteristics since
        # self._board cannot be trusted to have the same model/settings as the acquisition
        for idx, event in enumerate(events):
            try:
                # We're really only parsing one good event, so storing the output has negligible benefits
                parsed = event if "data" in event else parser.parse(event)

                samples = max([len(x) for x in parsed["data"]])
                channels = len(parsed["data"])
                enabled_channels = [
                    x for x in range(channels) if len(parsed["data"][x]) != 0
                ]
                label_count = max([len(x) for x in parsed["window_labels"]])

                # We only need valid data from one event
                return {
                    "window_labels": (len(enabled_channels), label_count),
                    "event_data": (len(enabled_channels), samples),
                    "enabled_channels": enabled_channels,
                    "channel_count": channels,  # total number of channels
                    "parser": parser,
                }
            except BadDataError as e:
                LOGGER.warning(f"Event {idx} not saved due to parser error: {e}")
            except BaseException as e:
                LOGGER.warning(f"Event {idx} not saved due to: {e}")

        # No way we can continue if we can't determine the shape
        raise BadDataError("No valid events found in acquisition")

    def write_calibration(self, acq: Acquisition):
        """Write all calibration to the file.

        If the acquisition is missing one or more types of calibration,
        there is no corresponding entry in the output file.

        ## Currently only supports pedestals.

        Args:
            acq (Acquisition): the acquisition to take calibrations from
        """
        self._file.require_group("calibration")
        if acq.pedestals:
            self.write_pedestals(acq.pedestals)
        # if acq.caldata: self.write_caldata() <---- not yet supported
        # if acq.adc2mv: self.write_adc2mv() <--- not yet supported

    def write_pedestals(self, pedestals: dict):
        """Writes a pedestals dict to the file.
        Data is stored into the 'calibration/pedestals' group.

        Args:
            pedestals (dict): the pedestals dict.

        Raises:
            ValueError if the pedestals dict is invalid
        """
        if not pedestals:
            raise ValueError("No pedestals to write")

        pedestals_data = np.array(pedestals["data"], dtype=np.uint16)

        group = self._file.require_group("calibration/pedestals")
        group.attrs["model"] = self._board.model
        group.attrs["channels"] = self._board.channels
        group.attrs["samples"] = self._board.params.get(
            "samples", len(pedestals["data"][0][0])
        )
        group.attrs["windows"] = self._board.params.get(
            "windows", len(pedestals["data"][0])
        )
        group.create_dataset(
            "data", data=pedestals_data, dtype=np.uint16, compression=self._compression
        )

    def write_event(self, event: dict):
        """Writes a single event to the file.
        This internally uses the `write_acquisition` function for
        format consistency.

        Args:
            event (dict): the event dict.
        """
        self.write_acquisition([event], calibration=False, metadata=False)

    def write_metadata(self, acq: Acquisition):
        """Stores metadata from an acquisition into a group.

        Adds several attributes to the given group.
        If `acq` is an Acquisition object, then an 'info' group is created
        holding the acquisition metadata (e.g. info, trigger_settings).

        Args:
            acq (deque, list, Acquisition): the acquisition to steal metadata from
        """
        group = self._file.require_group("metadata")
        _store_attributes(group, acq.as_dict()["metadata"])

    # ============================= Read Operations =============================
    def read_acquisition(self) -> Acquisition:
        """Reads an acquisition from the file.

        Returns:
            An acquisition object, or None if the operation
            was canceled.

        Raises:
            AttributeError if data is missing from the file.
        """
        try:
            events = self.read_events()
            if self._cancel:
                return None

            data = {
                "events": events,
                "metadata": self.read_metadata() if self.has_metadata else None,
                "calibration": {
                    "calibration": None,  # Not yet supported
                    "pedestals": self.read_pedestals() if self.has_pedestals else None,
                    "timingcal": None,  # Not yet supported
                },
            }
            acq = acq_converters.upgrade_old_acquisition(data)
        except AttributeError:
            raise

        if self._cancel:
            return None

        return acq

    def read_events(self, buffer: Union[deque, list, Acquisition] = None):
        """Reads all events from the file.

        Args:
            buffer (deque): the buffer to read into. If no buffer is
                provided, a new deque is used instead.

        Raises:
            AttributeError if one or more attributes does not exist
                in the 'events' group, or the group does not exist.

        Returns:
            The buffer, or a new deque if no buffer was provided, or
            None if the operation was canceled.
        """
        if buffer is None:
            buffer = deque()

        group = self._file.get("events", None)
        if not group:
            raise AttributeError("File does not contain events")

        # Pull all the datasets from the file
        try:
            num_events = group.attrs["event_count"]
        except AttributeError as e:
            LOGGER.error(f"Malformed data, failed to read attribute: {e}")
            raise

        # Allocate space in buffer ahead of time
        offset = len(buffer)
        buffer.extend([None] * num_events)

        # `blocks` dataset contains references that point to block groups
        block_refs = self._file["/events/blocks"]
        block_size = self.block_size
        num_blocks = self.num_blocks

        # Load up the output buffer block-by-block
        for block_idx in range(num_blocks):
            self.progress.append(
                (
                    block_idx / num_blocks * 100,
                    f"Reading block {block_idx+1}/{num_blocks}",
                )
            )
            block_group = self._file[block_refs[block_idx]]
            self._read_event_block(block_group, buffer, offset + block_idx * block_size)

            if self._cancel:
                return None

        return buffer

    def _read_event_block(
        self, group: h5py.Group, buffer: Union[deque, list, Acquisition], offset: int
    ):
        """Reads events from a block into a buffer.

        Args:
            group (int): the group to read from
            buffer (deque): the output buffer for events
            offset (int): the offset in the buffer to start at
        """
        # Pull all the datasets from the file
        try:
            data = group["data"]
            time = group["time"]
            window_labels = group["window_labels"]
            pkg_nums = group["package_numbers"]
            event_nums = group["event_numbers"]
            start_windows = group["start_windows"]
            creation_times = group["creation_times"]
            bad_events = group.attrs.get("bad_events", [])
            names = group.attrs.get("names", [])

            num_events = len(data)
            enabled_channels = self.enabled_channels
            channel_count = self.num_channels
        except AttributeError as e:
            LOGGER.error(f"Malformed data, failed to read attribute: {e}")
            raise

        # Create an event dict for each row in the arrays
        for event_idx, buffer_idx in enumerate(range(offset, offset + num_events)):
            if event_idx in bad_events:
                event = {
                    "rawdata": b"",  # raw data isn't stored in HDF5
                    "pkg_num": pkg_nums[event_idx][()],
                    "event_num": event_nums[event_idx][()],
                }
                buffer[buffer_idx] = event
                LOGGER.debug(f"Found bad event #{event_idx}")
                continue

            event = {
                "data": [[] for _ in range(channel_count)],
                "time": [[] for _ in range(channel_count)],
                "window_labels": [[] for _ in range(channel_count)],
                "pkg_num": pkg_nums[event_idx][()],
                "event_num": event_nums[event_idx][()],
                "start_window": start_windows[event_idx],
                "created_at": creation_times[event_idx],
            }
            buffer[buffer_idx] = event

            # Some channels are disabled, need to look at enabled_channels to map into dict
            for chan_idx, chan in enumerate(enabled_channels):
                event["data"][chan] = data[event_idx, chan_idx, :][()]
                event["time"][chan] = time[event_idx, chan_idx, :][()]
                event["window_labels"][chan] = window_labels[event_idx, chan_idx, :][()]

            # Some channels are disabled, need to look at enabled_channels to map into dict
            for chan_idx, chan in enumerate(enabled_channels):
                event["data"][chan] = data[event_idx, chan_idx, :][()]
                event["time"][chan] = time[event_idx, chan_idx, :][()]
                event["window_labels"][chan] = window_labels[event_idx, chan_idx, :][()]

            # Some channels are disabled, need to look at enabled_channels to map into dict
            for chan_idx, chan in enumerate(enabled_channels):
                event["data"][chan] = data[event_idx, chan_idx, :][()]
                event["time"][chan] = time[event_idx, chan_idx, :][()]
                event["window_labels"][chan] = window_labels[event_idx, chan_idx, :][()]

            if self._cancel:
                return None

        # Unnecessary to loop over the entire list for each event, so do it after
        for entry in names:
            event_num = int(entry[0].decode("ascii"))
            buffer[event_num + offset]["name"] = entry[1].decode("ascii")

            if self._cancel:
                return None

    def read_pedestals(self) -> dict:
        """Reads pedestals from the file.

        Returns:
            The pedestals dict, or None if the operation
            was canceled.

        Raises:
            AttributeError if the file does not have pedestals,
                or they are stored in an invalid format.
        """
        group = self._file.get("calibration/pedestals", None)
        if not group:
            raise AttributeError("File does not contain pedestals")

        data = group.get("data", None)
        if not data:
            raise AttributeError("Pedestals are stored in an invalid format")

        peds = {
            "data": data[()],
        }
        if self._cancel:
            return None

        return peds

    def read_metadata(self) -> dict:
        """Reads acquisition metadata from the file.

        Returns:
            A dictionary containing the metadata, or None
            if the operation was canceled.
        """
        metadata_group = self._file.get("metadata", None)
        if metadata_group is None:
            return

        type_converters = {
            "date": _DATETIME_CONVERTER,
            "acq_start": _DATETIME_CONVERTER,
            "acq_stop": _DATETIME_CONVERTER,
            "clock_file": _PATHLIB_CONVERTER,
            "stop_word": _BYTES_CONVERTER,
            "acq_num": _INT_CONVERTER,
        }
        metadata = _load_dict(metadata_group, type_converters, recursive=True)
        acq_version = metadata.get(
            "file_version", "0.2"
        )  # 0.2 is earliest HDF5 version
        acq_converters.convert(
            metadata, acq_version, acq_converters.LATEST_VERSION, in_place=True
        )

        # TRBHM needs a string stop_word instead of bytes
        if metadata.get("model", None) in ["trbhm", "dsa-c10-8"]:
            metadata["settings"]["params"]["stop_word"] = metadata["settings"][
                "params"
            ]["stop_word"].hex()

        if self._cancel:
            return None

        return metadata


def _store_attributes(group: h5py.Group, attrs: dict, recursive=True):
    """Adds a dict of attributes to a h5py group.

    Skips entries that have 'None' value.

    Args:
        group (Group): the group to add the attributes to
        attrs (dict): a dict of {name: value}
        recursive (bool): whether to create new groups for
            entries with dict values
    """
    for k, v in attrs.items():
        k = str(k)
        if v is None:  # HDF5 doesn't support None value
            continue
        elif isinstance(v, dict) and recursive:
            new_group = group.create_group(k, track_order=True)
            _store_attributes(new_group, v)
        else:
            v, dtype = _convert_for_storing(v)
            group.attrs.create(k, v, dtype=dtype)


def _load_dict(
    group: h5py.Group,
    type_conversions={},
    load_datasets=True,
    load_attrs=True,
    recursive=True,
) -> dict:
    """Loads a simple dictionary from objects in a group.

    Note that the type conversions are applied to ALL dict
    entries with the matching name, regardless of whether
    it is nested in another dict.

    Args:
        group (Group): the group to convert to a dict
        type_conversions (dict): a dict of {name: callable},
            applied to entries that have the same name. Useful
            for converting to some types like datetimes. The
            callable is given one argument: the object in
            its default h5py type.
        load_datasets (bool): whether to load datasets
        load_attrs (bool): whether to load attributes
        recursive (bool): whether to recursively load subgroups

    Returns:
        A dict containing translated data from the group.
    """
    result = {}
    type_conversions = type_conversions or {}

    if recursive:
        for k, v in group.items():
            if isinstance(v, h5py.Group):
                result[k] = _load_dict(
                    v, type_conversions, load_datasets, load_attrs, recursive
                )

    if load_datasets:
        for k, v in group.items():
            if isinstance(v, h5py.Group):
                continue
            elif (
                k in type_conversions
            ):  # TODO: add support for differentiating converters for nested dicts
                result[k] = type_conversions[k](v)
            else:
                result[k] = v[()]

    if load_attrs:
        for k, v in group.attrs.items():
            if (
                k in type_conversions
            ):  # TODO: add support for differentiating converters for nested dicts
                v = type_conversions[k](v)
            elif not isinstance(v, str):
                v = v[()]

            result[k] = v

    return result


def _convert_for_storing(value):
    """Converts a value to a type that can be stored in HDF5

    datetime -> float
    PathLike -> str
    bytes -> np.void

    Args:
        value: the value to convert

    Returns:
        A tuple of (converted value, new dtype)
    """
    dtype = None
    if isinstance(value, datetime):
        value = value.timestamp()
    elif isinstance(value, os.PathLike):
        value = str(value)
    elif isinstance(value, bytes):
        value = np.void(value)
    return value, dtype


def _get_package_versions():
    """Gets the NaluDAQ and NaluScope version strings.

    If the naluscope version cannot be determined (e.g. if it is not
    installed), then the version is returned as None

    Returns:
        A tuple of (NaluDAQ version, NaluScope version)
    """
    naludaq_version = naludaq.__version__
    try:
        import naluscope

        naluscope_version = naluscope.__version__
    except:
        naluscope_version = None

    return naludaq_version, naluscope_version


def _calculate_event_progress(num_events, event_num, min=10, max=90):
    """Calculates the progress percentage for operations that
    iterate over many events (e.g. loading, saving).

    This function can also be used to limit the number of
    progress updates emitted to avoid flooding the progress receiver:
    this function returns None if a progress update should not be
    emitted. Limits progress updates to 1 per percentage point.

    Args:
        num_events (int): the total number of events
        event_num (int): the current event number
        min (int): the starting percentage
        max (int): the ending percentage

    Returns:
        The percentage, or None if a progress update should not be emitted.
    """
    notification_interval = num_events / (max - min) or 1

    if event_num % notification_interval < 1:
        return min + event_num / notification_interval
    else:
        return None


def _get_params(acq: Acquisition, board) -> dict:
    """Get params based on info in acquisition object.

    If acquisition object doesn't contain params try using the model from the acquisition
    if model is not available, return params from the board.
    """
    if isinstance(acq, Acquisition) and acq.metadata:
        params = acq.params
        if params.get("chanshift", None) is None:
            params["chanshift"] = _calculate_channel_shift(params["chanmask"])
        return acq.params
    return board.params
