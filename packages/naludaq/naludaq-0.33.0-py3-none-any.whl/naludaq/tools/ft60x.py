"""Tools to help explore FT600 connected devices
"""
import functools
from contextlib import contextmanager

from naludaq.board.connections.connection_factory import USB3_AVAILABLE
from naludaq.helpers.exceptions import FTDIError

if USB3_AVAILABLE:
    import ftd3xx as ftd
    import ftd3xx.defines


def is_d3xx_available() -> bool:
    """Check if FTDI is available. This module can still be loaded without FTDI,
    so use this function if it is necessary to test the presence of drivers.
    """
    return USB3_AVAILABLE


def requires_ftd3xx(func):
    """Decorator. Use on functions to raise an FTDIError when FTDI is not present."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not USB3_AVAILABLE:
            raise FTDIError(
                "FTDI is not available because the drivers could not be found or loaded."
            )
        return func(*args, **kwargs)

    return wrapper


@requires_ftd3xx
def list_ft60x_devices() -> dict:
    """List all available ft60x devices.

    Returns:
        dict: the available devices formatted as {index: {<info>}}
    """
    ftd.createDeviceInfoList()
    devices = ftd.getDeviceInfoList() or {}
    devices = {
        i: {
            "id": device.ID,
            "serial": device.SerialNumber.decode(),
            "description": device.Description.decode(),
            "flags": device.Flags,
            "log_id": device.LocId,
            "is_open": (device.Flags & ftd3xx.defines.FT_FLAGS_OPENED) != 0,
        }
        for i, device in enumerate(devices)
    }
    return devices


@contextmanager
def connect(*args, **kwds):
    connection = _get_connection(*args, **kwds)
    try:
        yield connection
    finally:
        connection.close()


def _get_connection(index):
    devices = ftd.getDeviceInfoList()
    connection = ftd.create(devices[index].ID)
    return connection


@requires_ftd3xx
def serial_from_index(index):
    """Return the serialnumber from the index number"""

    connection = _get_connection(index)
    if connection is None:
        raise ConnectionError(f"Can't connect to hardware at index: {index}.")
    cfg = connection.getChipConfiguration()
    connection.close()

    desc = bytearray(cfg.StringDescriptors)
    d = desc[desc[0] + desc[desc[0]] + 2 :]

    ser_no = ""
    for c in range(2, len(d), 2):
        if d[c] == 0:
            continue
        ser_no += "{0:c}".format(d[c])

    return ser_no


@requires_ftd3xx
def index_from_serial(serial_no: str) -> int:
    """Return the serial number for an index"""
    devices = ftd.getDeviceInfoList()
    if len(devices) == 0:
        raise ConnectionError("Can't find any connected hardware.")
    for device in devices:
        idx = device.ID
        try:
            serno = serial_from_index(idx)
        except ConnectionError:
            continue
        if len(serial_no) > len(serno):
            raise ValueError("Serial number is longer than board serial number")

        if serno[-len(serial_no) :] == serial_no:
            return idx
    raise ConnectionError("No board with that serial number found.")
