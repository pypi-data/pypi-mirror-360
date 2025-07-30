""" Aquisitions groups of store events.
"""
import time
from collections import deque
from functools import reduce
from typing import Deque, Union

from naludaq.helpers.helper_functions import get_package_versions
from naludaq.models import acq_converters

Event = deque
_NoneType = type(None)
_no_value = object()


class _AcquisitionLikeMeta(type):
    """Metaclass for the `AcquisitionLike` type"""

    def __instancecheck__(self, instance) -> bool:
        return isinstance(instance, (list, deque, Acquisition))


class AcquisitionLike(metaclass=_AcquisitionLikeMeta):
    """Utility class describing behavior common to Acquisitions.

    Examples:
    ```py
    >>> isinstance([], AcquisitionLike)
    True
    >>> isinstance(my_acquisition, AcquisitionLike)
    True
    ```
    """


def _make_property(
    path: tuple, default=_no_value, setter=True, expected_type: type = _no_value
):
    head, tail = path[:-1], path[-1]

    @property
    def getter(self: "Acquisition"):
        value = reduce(dict.__getitem__, head, self.as_dict())
        if default is not _no_value:
            return value.setdefault(tail, default)
        else:
            return value[tail]

    if setter:

        @getter.setter
        def getter(self: "Acquisition", value):
            if expected_type is not _no_value and not isinstance(value, expected_type):
                raise TypeError(
                    f"{tail} must be a {expected_type}, not a {type(value)}"
                )
            reduce(dict.__getitem__, head, self.as_dict())[tail] = value

    return getter


class Acquisition:
    """Events are gathered in Acquistions.

    When you run a capture the events are gathered in an acquisition together with
    the settings used for the capture and the calibration settings used.
    Acquisitions also contains many attributes describing how the
    events were captured, including readout/trigger settings, board registers, etc.

    This class behaves as a wrapper for a `dict` and provides convenient
    accessors for specific entries. The internal `dict` should contain only
    built-in Python types in order to allow for deserialization without the need
    for the `naludaq` package installed. Do not serialize the Acquisition object
    directly!

    Duck-typing is used so that the class looks like both a `deque`
    (to access events) and a `naludaq.board.Board` (to simplify some NaluDAQ operations).

    Args:
        name (str): Acquisition name.
        acq_num (int): Acquisition id number.
        maxlen (int): Maximum number of events that can be held in the
            internal `deque`, or `None` for no maximum.
        data (dict):

    Functions:
        as_dict(): Returns the internal dictionary
        pop(): Remove and return an event.
        popleft(): Remove and return an event on the left side.
        append(event): Add on event on the right side.
        appendleft(event): Add an event on the left side.
        rotate(n): Rotate events by `n` positions right.

    Attributes:
        notes (str): Store any notes for this acquisition.
        info (dict): All information regarding the board, params and triggers
        pedestals
        caldata
        timingcal


    """

    def __init__(
        self, name: str = "", acq_num: int = 0, maxlen: int = None, data: dict = None
    ):
        self._validate_constructor_args(name, acq_num, maxlen, data)
        naludaq_version, naluscope_version = get_package_versions()

        metadata = {
            "acq_num": acq_num,
            "created_at": time.time(),
            "file_version": acq_converters.LATEST_VERSION,
            "info": {
                "connection": {},
                "readings": {},  # current, voltage, temperature
                "readout_settings": {},
                "trigger_settings": {},
            },
            "naludaq_version": naludaq_version,
            "naluscope_version": naluscope_version,
            "name": name,
            "notes": "",
            "settings": {
                "model": "",
                "params": {},
                "registers": {
                    "analog_registers": {},  # not present on UPAC
                    "control_registers": {},
                    "digital_registers": {},  # not present on UPAC
                    "i2c_registers": {},  # not present on UPAC
                },
            },
        }
        self._data = data or {
            "calibration": {
                "pedestals": None,
                "caldata": None,
                "timingcal": None,
            },
            "events": deque(maxlen=maxlen),
            "metadata": metadata,
        }
        if not self._data.get("metadata", None):
            self._data["metadata"] = metadata

    def _validate_constructor_args(
        self, name: str, acq_num: int, maxlen: int, data: dict
    ):
        """Validates arguments passed to the `__init__` method.

        Args:
            See `Acquisition.__init__`.

        Raises:
            ValueError if `data` and any other arguments are non-default.
            TypeError if the given values have the wrong type.
        """
        if data and (name or acq_num or maxlen):
            raise ValueError("When providing a data dict, other args cannot be used")
        elif not isinstance(name, str):
            raise TypeError("name must be a string")
        elif not isinstance(acq_num, int):
            raise TypeError("acq_num must be an int")
        elif not isinstance(maxlen, (int, _NoneType)):
            raise TypeError("maxlen must be an int")
        elif not isinstance(data, (dict, _NoneType)):
            raise TypeError("data must be a dict")

    def as_dict(self) -> dict:
        """Returns the internal dict holding the acquisition data."""
        return self._data

    events: Deque[Event] = _make_property(["events"])

    # ========================= calibration =========================
    pedestals: dict = _make_property(
        ["calibration", "pedestals"], expected_type=(dict, _NoneType)
    )
    caldata: dict = _make_property(
        ["calibration", "caldata"], expected_type=(dict, _NoneType)
    )
    timingcal: list = _make_property(
        ["calibration", "timingcal"], expected_type=(list, _NoneType)
    )

    # ========================= metadata =========================
    metadata: dict = _make_property(["metadata"], expected_type=dict)

    acq_num: int = _make_property(["metadata", "acq_num"], expected_type=int)
    created_at: float = _make_property(["metadata", "created_at"], expected_type=float)
    file_version: str = _make_property(["metadata", "file_version"], expected_type=str)
    naludaq_version: str = _make_property(
        ["metadata", "naludaq_version"], expected_type=str
    )
    naluscope_version: str = _make_property(
        ["metadata", "naluscope_version"], expected_type=str
    )
    name: str = _make_property(["metadata", "name"], expected_type=(str, int))
    notes: str = _make_property(["metadata", "notes"], expected_type=str)

    connection_info: dict = _make_property(
        ["metadata", "info", "connection"], expected_type=(dict, _NoneType)
    )
    readout_settings: dict = _make_property(
        ["metadata", "info", "readout_settings"], expected_type=(dict, _NoneType)
    )
    trigger_settings: dict = _make_property(
        ["metadata", "info", "trigger_settings"], expected_type=(dict, _NoneType)
    )
    readings: dict = _make_property(
        ["metadata", "info", "readings"], expected_type=(dict, _NoneType)
    )

    # ========================= Quack like a Board =========================
    model: str = _make_property(
        ["metadata", "settings", "model"], default="", expected_type=str
    )
    channels: int = _make_property(
        ["metadata", "settings", "params", "channels"], default=None, expected_type=int
    )
    dac_values: dict = _make_property(
        ["metadata", "settings", "params", "ext_dac", "channels"],
        default=None,
        expected_type=dict,
    )
    ext_dac: dict = _make_property(
        ["metadata", "settings", "params", "ext_dac"], default=None, expected_type=dict
    )
    params: dict = _make_property(
        ["metadata", "settings", "params"],
        default=None,
        expected_type=(dict, _NoneType),
    )
    registers: dict = _make_property(
        ["metadata", "settings", "registers"],
        default=None,
        expected_type=(dict, _NoneType),
    )

    # ========================= Quack like a Deque =========================
    def pop(self) -> Event:
        return self.events.pop()

    def popleft(self) -> Event:
        return self.events.popleft()

    def append(self, evt: Event):
        self.events.append(evt)

    def appendleft(self, evt: Event):
        self.events.appendleft(evt)

    def extend(self, evts):
        self.events.extend(evts)

    def extendleft(self, evts):
        self.events.extendleft(evts)

    def clear(self):
        self.events.clear()

    def rotate(self, n: int = 1):
        self.events.rotate(n)

    def remove(self, evt: Event):
        self.events.remove(evt)

    def reverse(self):
        self.events.reverse()

    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self):
        return self.events.__iter__()

    def __getitem__(self, k) -> Event:
        return self.events[k]

    def __setitem__(self, k, v: Event):
        self.events[k] = v

    def __eq__(self, other: Union[list, deque, "Acquisition"]):
        if isinstance(other, (list, deque)):
            return self.events == other
        elif isinstance(other, Acquisition):
            return self.events == other.events
        return False
