"""Utilities for accessing acquisitions.

There are a few acquisition classes, which each provide a different way to access acquisitions:

- RemoteAcquisition - access an acquisition through the server.
- LocalAcquisition - access an acquisition in memory.
- DiskAcquisition - access an acquisition loaded from disk.
- TemporaryAcquisition - same as a remote acquisition, but only exists for as long as you need it.

Each of these types is useful in different situations, and provide roughly the same basic interface.
It is recommended to limit use of the RemoteAcquisition type to only where it is necessary, as it is
by far the slowest and most resource-intensive.
"""
import copy
import gzip
import logging
import mmap
import os
import pickle
import struct
from collections import defaultdict, deque
from copy import deepcopy
from pathlib import Path
from typing import Iterator

import numpy as np
import yaml

from naludaq.backend.context import Context
from naludaq.backend.exceptions import AcquisitionError, BackendError
from naludaq.helpers.exceptions import BadDataError
from naludaq.models import Acquisition
from naludaq.parsers import get_parser
from naludaq.tools.waiter import EventWaiter

logger = logging.getLogger("naludaq.backend.acquisition")

AVAILABLE_MISC_DATA_KEYS = ["pedestals", "caldata", "timingcal", "readout_metadata"]

# Disallowed characters for names on windows/linux
# https://stackoverflow.com/questions/4814040/allowed-characters-in-filename
DISALLOWED_ACQ_NAME_CHARACTERS = [
    "\x00",
    "\\",
    "/",
    ":",
    "*",
    "?",
    '"',
    "<",
    ">",
    "|",
    "\n",
]


class RemoteAcquisition:
    _MISC_DATA_CACHE = defaultdict(dict)
    _METADATA_CACHE = {}

    def __init__(self, context: Context, name: str):
        """A utility for using the backend's REST API to access
        acquisition located on the server.

        All operations on the acquisition are performed through HTTP requests.

        Args:
            context (Context): context used to communicate with the server.
            name (str): name of the acquisition.
        """
        self._name = name
        self._context = context

    @property
    def name(self) -> str:
        """Get/set the name of the acquisition.

        Raises:
            ValueError: if the name (when set) is not valid
        """
        return self._name

    @name.setter
    def name(self, name: str):
        if name == self._name:
            return
        _validate_acq_name_or_raise(name)
        try:
            self.context.client.put(
                "/acq/move", params={"source_name": self._name, "dest_name": name}
            )
        except ValueError as e:
            raise ValueError("Invalid destination acquisition name") from e
        except Exception as e:
            raise AcquisitionError("Could not rename acquisition") from e
        self._name = name

    @property
    def context(self) -> Context:
        """The client used to communiate with the remote"""
        return self._context

    def __eq__(self, other: object) -> bool:
        """Checks if two acquisitions represent the same physical acquisition on the same remote"""
        return (
            isinstance(other, RemoteAcquisition)
            and self._name == other._name
            and self._context == other._context
        )

    def __hash__(self) -> int:
        """Compute the hash for this object"""
        return hash(self._name)

    def __len__(self) -> int:
        """Get the number of events in the acquisition"""
        return self.length

    def __getitem__(self, index: "int | slice | list") -> "bytes | list[bytes]":
        """Get events from the remote"""
        if isinstance(index, int):
            return self.raw_event(index)
        if isinstance(index, slice):
            start, stop, step = index.indices(self.length)
            return [self.raw_event(x) for x in range(start, stop, step)]
        if isinstance(index, list):
            return [self.raw_event(x) for x in index]
        raise TypeError("Index must be int or slice")

    def __iter__(self) -> Iterator[dict]:
        """Iterate over raw events"""
        return (self[i] for i in range(len(self)))

    @property
    def length(self) -> int:
        """Get the number of events in the acquisition"""
        info = self._get_info_or_raise(len=True)
        return info["len"]

    @property
    def path(self) -> str:
        """Get the path to the acquisition on the remote"""
        return self._get_info_or_raise(path=True)["path"]

    @property
    def metadata(self) -> dict:
        """Get the acquisition metadata."""
        cache = RemoteAcquisition._METADATA_CACHE
        key = self._cache_key()
        metadata = cache.get(key, None)
        if metadata is None:
            info = self._get_info_or_raise(metadata=True)
            metadata = yaml.safe_load(info["metadata"])
            cache[key] = metadata
        return metadata

    @property
    def params(self) -> dict:
        """Get params from the acq metadata"""
        return self.metadata["params"]

    @property
    def exists(self) -> bool:
        """Checks if this acquisition exists on the remote"""
        try:
            _ = self.length
        except BackendError:
            return False
        return True

    @property
    def readout_metadata(self) -> "dict | None":
        """Get/set the readout metadata for this acquisition"""
        return self._fetch_misc_data("readout_metadata")

    @readout_metadata.setter
    def readout_metadata(self, readout_metadata: "dict | None"):
        self._store_misc_data("readout_metadata", readout_metadata)

    @property
    def pedestals(self) -> "dict | None":
        """Get/set the pedestals for this acquisition"""
        peds = self._fetch_misc_data("pedestals_calibration")
        if isinstance(peds, dict):
            converted_peds = {
                "data": np.array(peds["data"]),
                "rawdata": np.array(peds["rawdata"]),
                "params": peds.get("params", {}),
            }
            # if the data is already a numpy array, this means it was created in the old misc
            # data format. Send it back to the remote to convert it to the new format
            if isinstance(peds["data"], np.ndarray):
                try:
                    self.pedestals = converted_peds
                except Exception as e:
                    logger.error(
                        "Failed to upgrade pedestals to new format", exc_info=e
                    )
            return converted_peds
        return None

    @pedestals.setter
    def pedestals(self, peds: "dict | None"):
        if peds:
            peds = {
                "data": peds["data"].tolist(),
                "rawdata": peds["rawdata"].tolist(),
                "params": peds.get("params", {}),
            }
        self._store_misc_data("pedestals_calibration", peds)

    @property
    def caldata(self) -> "dict | None":
        """Get/set the adc2mv calibration for this acquisition"""
        return self._fetch_misc_data("adc2mv_calibration")

    @caldata.setter
    def caldata(self, adc2mv: "dict | None"):
        self._store_misc_data("adc2mv_calibration", adc2mv)

    @property
    def timingcal(self) -> "list | None":
        """Get/set the timing calibration for this acquisition"""
        return self._fetch_misc_data("timing_calibration")

    @timingcal.setter
    def timingcal(self, timingcal: "list | None"):
        self._store_misc_data("timing_calibration", timingcal)

    def create(self, metadata: dict):
        """Creates the acquisition on the remote.

        Args:
            metadata (dict): metadata to store in the acquisition

        Raises:
            HttpError: if the acquisition exists, or could not be created.
        """
        self._context.client.post(
            "/acq",
            params={"name": self._name},
            json={"metadata": yaml.dump(metadata)},
        )

    def delete(self):
        """Deletes the acquisition on the remote"""
        self.context.client.delete(
            "/acq",
            params={"name": self._name},
        )

    def stream(
        self, timeout: float = 0.5, interval: float = 0.010, start: int = 0
    ) -> Iterator[bytes]:
        """An iterator over events which can be used to stream data during a readout.

        The stream ends when the retrieving the next event times out.
        Note that the iterator only sleeps while at the end of the acquisition;
        for events before the end the stream will run as fast as possible.

        Args:
            timeout (float): timeout in seconds for receiving an event.
            interval (float): the interval in seconds at which to check for events.
            start (int): the event at which to start the stream.
                -1 means to start past the end of the acquisition and wait for a new
                event. This is useful for streaming during a readout.
        """
        index = _resolve_index_or_default(start, len(self) + 1, 0)
        while True:
            waiter = EventWaiter(
                buffer=self,
                amount=index + 1,
                interval=interval,
                timeout=timeout,
            )
            try:
                waiter.start(blocking=True)
            except TimeoutError:
                raise
            try:
                event = self[index]
            except IndexError as e:
                raise TimeoutError("Timed out while waiting for an event") from e
            yield event
            index += 1

    def stream_parsed(
        self,
        timeout: float = 0.5,
        interval: float = 0.010,
        start: int = 0,
        skip_bad=True,
        parser=None,
    ) -> Iterator[dict]:
        """An iterator over parsed events. See the `stream()` documentation for more details.

        Events which cannot be parsed are ignored.

        Args:
            start (int): the event at which to start the stream.
            parser (Parser): the parser to use
            timeout (float): timeout in seconds for receiving an event.
            interval (float): the interval in seconds at which to check for events.
            skip_bad (bool): whether to skip invalid events.
        """
        parser = parser or get_parser(self.params)
        for event in self.stream(timeout, interval, start):
            try:
                event = parser.parse(event)
            except BadDataError:
                if not skip_bad:
                    raise
            if "data" in event:
                yield event
            elif not skip_bad:
                raise BadDataError("Got an invalid event")

    def transfer(self, indices: list[int] = None) -> "LocalAcquisition":
        """Transfer a portion of the events from this remote acquisition
        into a `LocalAcquisition`.

        Warning: calling this method is expensive, use wisely.

        Args:
            indices (list[int]): indices of events to transfer. If not
                provided, all events are transferred. This can be
                very costly!

        Returns:
            LocalAcquisition: The local acquisition.
        """
        if indices is None:
            indices = range(len(self))
        events = [self.raw_event(i) for i in indices]
        misc_data = {}
        for name in AVAILABLE_MISC_DATA_KEYS:
            try:
                misc_data[name] = getattr(self, name)
            except Exception:
                pass
        return LocalAcquisition(
            name=self.name,
            metadata=deepcopy(self.metadata),
            events=events,
            misc_data=misc_data,
        )

    def raw_event(self, index: int) -> bytes:
        """Get a raw event at the given index"""
        index = _resolve_index_or_raise(index, len(self))
        rawdata = self.context.client.get_binary(
            "/acq/event",
            params={"acquisition": self._name, "index": index},
        )
        return _build_raw_event_dict(rawdata, index)

    def parsed_event(self, parser, index: int) -> dict:
        """Convenience function for getting a parsed event

        Args:
            parser (Parser): the parser to use
            index (int): index of the event

        Returns:
            dict: the parsed event
        """
        return parser.parse(self.raw_event(index))

    def set_output(self):
        """Use this acquisition as the output for readouts"""
        self.context.client.put(
            "/acq/output",
            params={"name": self._name},
        )

    def _get_info_or_raise(
        self,
        len: bool = False,
        path: bool = False,
        metadata: bool = False,
        chunk_count: bool = False,
        total_size: bool = False,
    ) -> dict:
        """Retrieve information about this acquisition"""
        return self.context.client.get_json(
            "acq/show",
            params={
                "name": self._name,
                "len": int(len),
                "path": int(path),
                "metadata": int(metadata),
                "chunk_count": int(chunk_count),
                "total_size": int(total_size),
            },
        )

    def invalidate_cache(self):
        """Invalidate the misc data cache for this acquisition."""
        cache = RemoteAcquisition._MISC_DATA_CACHE
        try:
            del cache[self._cache_key()]
        except Exception:
            pass  # not an error

    def _fetch_misc_data(self, type: str):
        """Fetch misc data cache, or from the acquisition on miss.

        Args:
            type (str): the type of misc data

        Raises:
            AcquisitionError: if the misc data is invalid

        Returns:
            object: The deserialized misc data
        """
        missing = object()
        key = self._cache_key()
        cache = RemoteAcquisition._MISC_DATA_CACHE
        result = cache[key].get(type, missing)
        if result is missing:
            try:
                result = self._fetch_misc_data_remote(type)
            except AcquisitionError:
                raise
            cache[key][type] = result
        return result

    def _store_misc_data(self, type: str, obj):
        """Serializes and stores the misc data in the cache and acquisition.

        Args:
            type (str): the misc data type name
            obj (object): the misc data

        Raises:
            ValueError: if the misc type is invalid or the object could not
                be serialized.
        """
        cache = RemoteAcquisition._MISC_DATA_CACHE
        cache[self._cache_key()][type] = obj
        try:
            self._store_misc_data_remote(type, obj)
        except ValueError:
            raise

    def _fetch_misc_data_remote(self, type: str):
        """Read misc data from the acquisition.

        Args:
            type (str): the type of misc data

        Raises:
            AcquisitionError: if the misc data is invalid

        Returns:
            object: The deserialized misc data
        """
        try:
            response = self._context.client.get(
                "/acq/misc-data",
                params={"acquisition": self._name, "type": type},
            )
        except ValueError:  # means there is no misc data
            return None
        try:
            return _deserialize_misc_data(response.content)
        except ValueError as e:
            raise AcquisitionError(f"Misc data for {type} is malformed") from e

    def _store_misc_data_remote(self, type: str, obj):
        """Serializes and stores the misc data in the acquisition.

        Args:
            type (str): the misc data type name
            obj (object): the misc data

        Raises:
            ValueError: if the misc type is invalid or the object could not
                be serialized.
        """
        try:
            data = _serialize_misc_data(obj)
        except ValueError:
            raise
        try:
            self._context.client.put_binary(
                "/acq/misc-data",
                data=data,
                params={"acquisition": self._name, "type": type},
            )
        except ValueError as e:
            raise ValueError(f"Invalid misc data name '{type}'") from e

    def _cache_key(self):
        """Get a unique-ish key representing this acquisition to use for the misc data cache"""
        return (self.context.address, self.name)


class TemporaryAcquisition(RemoteAcquisition):
    def __init__(self, context: Context, name: str, metadata: dict):
        """A temporary version of the remote acquisition.

        An acquisition is created on the remote when a `TemporaryAcquisition`
        is instantiated, and deleted when the object is deleted or, if used
        as a context manager, when the context exits.

        Args:
            client (HttpClient): the client
            name (str): name of the acquisition. This must be unique on the remote!
            metadata (dict): metadata to store in the acquisition.
        """
        super().__init__(context, name)
        self.create(metadata)

    def __enter__(self) -> "TemporaryAcquisition":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.exists:
            self.delete()


class LocalAcquisition:
    def __init__(
        self,
        name: str,
        metadata: dict,
        events: list[dict],
        misc_data: dict[str, object],
    ):
        """Local (RAM) copy of a slice of an acquisition.

        Converting a remote acquisition to a local one may be useful in the following cases:
        - the data needs to be retained after the server is shut down/disconnected.
        - the data needs to be modified.
        - the up-front cost of transferring the data is preferred to the cost of
          transferring data while processing it.
        - the acquisition needs to be converted to a legacy format.

        Args:
            name (str): acquisition name
            metadata (dict): acquisition metadata
            events (list[dict]): raw events from the remote
            misc_data (dict[str, object]): misc_data data
        """
        self._name = name
        self._metadata = metadata
        self._events = events
        self._misc_data = misc_data

    @property
    def name(self) -> str:
        """Acquisition name"""
        return self._name

    @property
    def metadata(self) -> dict:
        """Acquisition metadata"""
        return self._metadata

    @property
    def events(self) -> list[dict]:
        """List of events transferred from the remote"""
        return self._events

    @property
    def readout_metadata(self) -> "dict | None":
        """Get/set the readout metadata for this acquisition"""
        return self._misc_data.get("readout_metadata", None)

    @readout_metadata.setter
    def readout_metadata(self, metadata: "dict | None"):
        self._misc_data["readout_metadata"] = metadata

    @property
    def pedestals(self) -> "dict | None":
        """Get/set the pedestals for this acquisition"""
        peds = self._misc_data.get("pedestals", None)
        if isinstance(peds, dict):
            peds = {
                "data": np.array(peds["data"]),
                "rawdata": np.array(peds["rawdata"]),
                "params": peds.get("params", {}),
            }
        return peds

    @pedestals.setter
    def pedestals(self, peds: "dict | None"):
        self._misc_data["pedestals"] = peds

    @property
    def caldata(self) -> "dict | None":
        """Get/set the adc2mv calibration for this acquisition"""
        return self._misc_data.get("caldata", None)

    @caldata.setter
    def caldata(self, adc2mv: "dict | None"):
        self._misc_data["caldata"] = adc2mv

    @property
    def timingcal(self) -> "list | None":
        """Get/set the timing calibration for this acquisition"""
        return self._misc_data.get("timingcal", None)

    @timingcal.setter
    def timingcal(self, timingcal: "list | None"):
        self._misc_data["timingcal"] = timingcal

    def __len__(self) -> int:
        """Number of events in the local copy"""
        return len(self._events)

    def __getitem__(self, index: "int | slice") -> list[dict]:
        """Get a slice of the acquisition events."""
        if isinstance(index, (int, slice)):
            return self._events[index]
        raise TypeError("Index must be int or slice")

    def __iter__(self) -> Iterator[dict]:
        """Iterate over raw events"""
        return (self[i] for i in range(len(self)))

    def raw_event(self, index: int) -> dict:
        """Get a raw event at the given index"""
        index = _resolve_index_or_raise(index, len(self))
        return self.events[index]

    def parsed_event(self, parser, index: int) -> dict:
        """Convenience function for getting a parsed event

        Args:
            parser (Parser): the parser to use
            index (int): index of the event

        Returns:
            dict: the parsed event
        """
        return parser.parse(self.raw_event(index))

    def parse_all(self, parser) -> list[dict]:
        """Parse all events in the local acquisition

        Args:
            parser (Parser): the parser to use

        Returns:
            list[dict]: list of parsed events
        """
        return [parser.parse(event) for event in self]

    def to_legacy_acquisition(self, deepcopy: bool = False) -> Acquisition:
        """Convert to a legacy acquisition object.

        Not all information will be transferred, only the main stuff.
        """

        def maybe_copy(x):
            return copy.deepcopy(x) if deepcopy else x

        acq = Acquisition(name=self.name)
        acq.events = deque(maybe_copy(self.events))
        acq.pedestals = maybe_copy(self.pedestals)
        acq.caldata = maybe_copy(self.caldata)
        acq.timingcal = maybe_copy(self.timingcal)
        acq.params = maybe_copy(self.metadata.get("params", {}))
        acq.registers = maybe_copy(self.metadata.get("registers", {}))
        acq.model = acq.params.get("model", None)

        return acq


class DiskChunk:
    INDEX_ENTRY_SIZE = 8

    def __init__(self, index_path: Path, bin_path: Path):
        """Utility for reading chunk files directly from disk.

        The chunk will be opened on instantiation. It is recommended to use
        this object as a context manager to ensure the chunk is closed when
        it is no longer needed.

        Args:
            index_path (Path): path to index file
            bin_path (Path): path to binary file
        """
        if not isinstance(index_path, (Path, str)) or not isinstance(
            bin_path, (Path, str)
        ):
            raise TypeError("Path must be a string or Path object")
        self._index_path = Path(index_path)
        self._bin_path = Path(bin_path)
        self._open = False
        self.open()

    @property
    def metadata(self) -> dict:
        """Get the chunk metadata

        Raises:
            IOError: if the chunk is not open
        """
        self._raise_if_closed()
        return self._metadata

    @property
    def version(self) -> int:
        """Get the chunk format revision number.

        Raises:
            IOError: if the chunk is not open
        """
        self._raise_if_closed()
        return self._version

    def __len__(self) -> int:
        """Get the number of events in the chunk

        Raises:
            IOError: if the chunk is not open
        """
        self._raise_if_closed()
        return len(self._index_mmap) // DiskChunk.INDEX_ENTRY_SIZE

    def __del__(self):
        """Close the chunk file"""
        self.close()

    def __enter__(self):
        """Context manager enter"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit"""
        self.close()

    def open(self):
        self._index_file = open(self._index_path, "rb+")
        self._bin_file = open(self._bin_path, "rb+")
        self._index_mmap = mmap.mmap(
            self._index_file.fileno(), os.path.getsize(self._index_path)
        )
        self._bin_mmap = mmap.mmap(
            self._bin_file.fileno(), os.path.getsize(self._bin_path)
        )
        self._open = True

        self._version = self._read_bin_header()["version"]
        self._metadata = self._read_metadata()
        self._parser = get_parser(self._metadata["params"])

    def close(self):
        """Close the chunk file"""
        if self._open:
            self._index_mmap.close()
            self._index_file.close()
            self._bin_mmap.close()
            self._bin_file.close()

    def raw_event(self, index: int) -> dict:
        """Get a raw event from the chunk.

        Args:
            index (int): index of the event in the chunk.

        Returns:
            dict: the raw event

        Raises:
            IndexError: if the index is out of bounds
            IOError: if the chunk is closed
        """
        self._raise_if_closed()
        index = _resolve_index_or_raise(index, len(self))
        start = index * DiskChunk.INDEX_ENTRY_SIZE
        end = start + DiskChunk.INDEX_ENTRY_SIZE
        entry = self._index_mmap[start:end]
        offset, length = struct.unpack("II", entry)
        event = self._bin_mmap[offset : offset + length]
        return _build_raw_event_dict(event, index)

    def parsed_event(self, index: int) -> dict:
        """Get a parsed event from the chunk.

        Uses metadata stored in the chunk file to parse the data.

        Args:
            index (int): index of the event in the chunk.

        Returns:
            bytes: the parsed event

        Raises:
            IndexError: if the index is out of bounds
            IOError: if the chunk is closed
        """
        self._raise_if_closed()
        return self._parser.parse(self.raw_event(index))

    def _read_metadata(self) -> dict:
        """Read metadata from the bin file.

        Raises:
            IOError: if the chunk is closed
        """
        self._raise_if_closed()
        metadata_length = self._read_bin_header()["metadata_length"]
        metadata = self._bin_mmap[8 : 8 + metadata_length]
        return yaml.safe_load(metadata)

    def _read_bin_header(self) -> dict:
        """Read the header from the binary file.

        Returns:
            dict: contains keys "version" and "metadata_length"

        Raises:
            IOError: if the chunk is closed
        """
        self._raise_if_closed()
        version, _, metadata_length = struct.unpack("HHI", self._bin_mmap[:8])  # hello!
        return {
            "version": version,
            "metadata_length": metadata_length,
        }

    def _raise_if_closed(self):
        if not self._open:
            raise IOError("Chunk is closed")


class DiskAcquisition:
    def __init__(self, path: Path, parse: bool = True):
        """Utility for accessing acquisition directly from disk.

        The acquisition will be opened on instantiation. It is recommended to use
        this object as a context manager to ensure the acquisition is closed when
        it is no longer needed.

        Important: the acquisition should not be mutated while this object is alive.
        If the acquisition changes, the DiskAcquisition must be recreated.

        Args:
            path (Path): path to the acquisition folder.

        Raises:
            InvalidAcquisitionError: if the path is not a valid acquisition.
        """
        if not isinstance(path, (Path, str)):
            raise TypeError("Path must be a string or Path object")
        path = Path(path).resolve()
        if not DiskAcquisition._is_acquisition(path):
            raise AcquisitionError("Not a valid acquisition")
        self.parse = parse
        self._root = path
        self._open = False
        self.open()

    @property
    def parse(self) -> bool:
        """Whether to parse events when getting them"""
        return self._parse

    @parse.setter
    def parse(self, value: bool):
        self._parse = value

    def __len__(self) -> int:
        """Get the number of events in the acquisition"""
        return self._event_count

    def __del__(self):
        """Close the acquisition"""
        self.close()

    def __enter__(self) -> "DiskAcquisition":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __getitem__(self, index: "int | slice") -> "dict | list[dict]":
        """Get one or more parsed event from the acquisition.

        Args:
            index (int | slice): index(es) of the event(s) in the acquisition.

        Returns:
            "dict | list[dict]": the event(s)

        Raises:
            IndexError: if the index is out of bounds
            IOError: if the acquisition is closed
        """
        self._raise_if_closed()
        result = None
        if self._parse:
            fn = self.parsed_event
        else:
            fn = self.raw_event
        if isinstance(index, int):
            index = _resolve_index_or_raise(index, len(self))
            result = fn(index)
        elif isinstance(index, slice):
            result = [fn(i) for i in range(*index.indices(len(self)))]
        elif isinstance(index, list):
            result = [fn(i) for i in index]
        else:
            raise TypeError("Index must be an int or slice")
        return result

    def open(self):
        """Open the acquisition for reading.

        If the acquisition is already open, this is a no-op.
        """
        if self._open:
            return
        self._chunks = self._find_chunks()
        self._event_count = sum(len(chunk) for chunk in self._chunks)
        with open(self._root / "metadata.yml", "r") as f:
            self._metadata = yaml.safe_load(f)
        self._open = True

    def close(self):
        """Close the acquisition"""
        for chunk in self._chunks:
            chunk.close()
        self._chunks = []
        self._open = False

    @property
    def chunks(self) -> list[DiskChunk]:
        """Get a list of chunks in the acquisition"""
        return self._chunks.copy()

    @property
    def metadata(self) -> dict:
        """Get the acquisition metadata"""
        self._raise_if_closed()
        return self._metadata

    @property
    def params(self) -> dict:
        """Get parameters describing the board"""
        return self._metadata.get("params", {})

    @property
    def readout_metadata(self) -> "dict | None":
        """Get/set the readout metadata for this acquisition"""
        return self._fetch_misc_data("readout_metadata")

    @readout_metadata.setter
    def readout_metadata(self, metadata: "dict | None"):
        self._store_misc_data("readout_metadata", metadata)

    @property
    def pedestals(self) -> "dict | None":
        """Get/set the pedestals for this acquisition"""
        peds = self._fetch_misc_data("pedestals_calibration")
        if isinstance(peds, dict):
            peds = {
                "data": peds["data"],
                "rawdata": peds["rawdata"],
                "params": peds.get("params", {}),
            }
        return peds

    @pedestals.setter
    def pedestals(self, peds: "dict | None"):
        if isinstance(peds, dict):
            peds = {
                "data": peds["data"].tolist(),
                "rawdata": peds["rawdata"].tolist(),
                "params": peds.get("params", {}),
            }
        self._store_misc_data("pedestals_calibration", peds)

    @property
    def caldata(self) -> "dict | None":
        """Get/set the adc2mv calibration for this acquisition"""
        return self._fetch_misc_data("adc2mv_calibration")

    @caldata.setter
    def caldata(self, adc2mv: "dict | None"):
        self._store_misc_data("adc2mv_calibration", adc2mv)

    @property
    def timingcal(self) -> "list | None":
        """Get/set the timing calibration for this acquisition"""
        return self._fetch_misc_data("timing_calibration")

    @timingcal.setter
    def timingcal(self, timingcal: "list | None"):
        self._store_misc_data("timing_calibration", timingcal)

    def raw_event(self, index: int) -> bytes:
        """Get a raw event from the acquisition.

        Args:
            index (int): index of the event

        Returns:
            bytes: the raw event data

        Raises:
            IndexError: if the index is out of bounds
            IOError: if the acquisition is not open
        """
        self._raise_if_closed()
        chunk, index_in_chunk = self._map_to_chunk(index)
        return chunk.raw_event(index_in_chunk)

    def parsed_event(self, index: int) -> bytes:
        """Get a parsed event from the acquisition.

        Args:
            index (int): index of the event

        Returns:
            bytes: the raw event data

        Raises:
            IndexError: if the index is out of bounds
            IOError: if the acquisition is not open
        """
        self._raise_if_closed()
        chunk, index_in_chunk = self._map_to_chunk(index)
        return chunk.parsed_event(index_in_chunk)

    def _map_to_chunk(self, index: int) -> tuple[DiskChunk, int]:
        """Map an absolute index to a chunk and a relative index.

        Args:
            index (int): the absolute event index

        Raises:
            IndexError: if the index is out of bounds

        Returns:
            tuple[DiskChunk, int]: the chunk the index corresponds to and the
                event number relative to the chunk.
        """
        for chunk in self._chunks:
            if index < len(chunk):
                return (chunk, index)
            index -= len(chunk)
        raise IndexError("Index out of bounds")

    def _find_chunks(self) -> list[DiskChunk]:
        """Find all chunks located in the acquisition folder.

        Returns:
            list[DiskChunk]: list of chunks
        """
        count = 0
        output = []
        while True:
            index_path = self._root / f"{count}.idx"
            bin_path = self._root / f"{count}.bin"
            if not index_path.exists():
                break
            chunk = DiskChunk(index_path, bin_path)
            output.append(chunk)
            count += 1
        return output

    def _fetch_misc_data(self, type: str):
        """Read misc data from the acquisition.

        Args:
            type (str): the type of misc data

        Returns:
            object: The deserialized misc data

        Raises:
            AcquisitionError: if the misc data is invalid
            IOError: if the acquisition is not open
        """
        self._raise_if_closed()
        try:
            with open(self._root / type, "rb") as f:
                data = f.read()
        except Exception:  # means there is no misc data
            return None
        try:
            return _deserialize_misc_data(data)
        except ValueError as e:
            raise AcquisitionError(f"Misc data for {type} is malformed") from e

    def _store_misc_data(self, type: str, obj):
        """Serializes and stores the misc data in the acquisition.

        Args:
            type (str): the misc data type name
            obj (object): the misc data

        Raises:
            ValueError: if the misc type is invalid or the object could not
                be serialized.
            IOError: if the acquisition is not open
        """
        self._raise_if_closed()
        try:
            data = _serialize_misc_data(obj)
        except ValueError:
            raise
        with open(self._root / type, "wb") as f:
            f.write(data)

    def _raise_if_closed(self):
        if not self._open:
            raise IOError("Acquisition is not open")

    @staticmethod
    def _is_acquisition(root: Path) -> bool:
        """Check if the given path is a valid acquisition"""
        return root.is_dir() and (root / "metadata.yml").exists()


def _build_raw_event_dict(rawdata: bytes, index: int) -> dict:
    """Build the raw event dict from raw raw data.

    Args:
        rawdata (bytes): the raw raw data.
        index (int): the event index

    Returns:
        dict: the event dict
    """
    return {
        "rawdata": rawdata,
        "event_num": index,
        "pkg_num": index,
    }


def _resolve_index_or_raise(index: int, length: int) -> int:
    """Convert a negative index to a positive one.

    Args:
        index (int): the index in the collection
        length (int): the length of the collection

    Raises:
        IndexError: if the index is invalid

    Returns:
        int: the resolved index
    """
    if index < 0 and length > 0:
        index = (length + index) % length
    if not 0 <= index < length:
        raise IndexError(
            f"Index {index} out of bounds for acquisition of length {length}"
        )
    return index


def _resolve_index_or_default(index: int, length: int, default: int) -> int:
    """Convert a negative index to a positive one, or return a
    provided default if the index is invalid.

    Args:
        index (int): the index in the collection
        length (int): the length of the collection
        default (int): the default value

    Returns:
        int: the resolved index, or the default if the index is invalid
    """
    try:
        index = _resolve_index_or_raise(index, length)
    except IndexError:
        index = default
    return index


def _serialize_misc_data(obj) -> bytes:
    """Serialize misc data.

    Args:
        obj (object): the misc data.

    Raises:
        ValueError: if the data could not be serialized.

    Returns:
        bytes: the serialized misc data.
    """
    # Compression level seriously affects how long this takes,
    # don't put it above 3
    try:
        return gzip.compress(pickle.dumps(obj), compresslevel=3)
    except (pickle.PicklingError, gzip.BadGzipFile) as e:
        raise ValueError("Cannot serialize misc data") from e


def _deserialize_misc_data(data: bytes) -> object:
    """Deserialize misc data.

    Args:
        data (bytes): the serialized data.

    Raises:
        ValueError: if the data could not be deserialized

    Returns:
        object: the misc data
    """
    try:
        return pickle.loads(gzip.decompress(data))
    except (pickle.PicklingError, gzip.BadGzipFile, EOFError) as e:
        raise ValueError("Cannot deserialize misc data") from e


def _validate_acq_name_or_raise(name: str):
    """Check whether the given name can be used for an acquisition.

    This isn't a full check since that would be insane. For example
    there are hundreds of unicode control codes that aren't checked.
    This method will only catch the most common naming mistakes a user
    might make.

    Args:
        name (str): acquisition name

    Raises:
        TypeError: if the name is not a string
        ValueError: if the name is zero-length or contains invalid characters
    """
    if not isinstance(name, str):
        raise TypeError("Name must be a string")
    if len(name) == 0:
        raise ValueError("Name cannot have zero length")
    if any(x in name for x in DISALLOWED_ACQ_NAME_CHARACTERS):
        raise ValueError("Name contains an invalid character")
    # Catch ".", "..", and trailing period on Windows
    if name.startswith(".") or name.endswith("."):
        raise ValueError("Name cannot start or end with '.'")
    # Windows thing
    if name.startswith(" ") or name.endswith(" "):
        raise ValueError("Name cannot start or end with space character")
