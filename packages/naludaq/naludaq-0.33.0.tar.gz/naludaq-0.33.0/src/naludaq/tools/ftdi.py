import functools

try:
    import ftd2xx as ftd

    _FTDI_AVAILABLE = True
except:
    _FTDI_AVAILABLE = False

from naludaq.helpers.exceptions import FTDIError


def is_ftdi_available() -> bool:
    """Check if FTDI is available. This module can still be loaded without FTDI,
    so use this function if it is necessary to test the presence of drivers.
    """
    return _FTDI_AVAILABLE


def requires_ftd2xx(func):
    """Decorator. Use on functions to raise an FTDIError when FTDI is not present."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not _FTDI_AVAILABLE:
            raise FTDIError(
                "FTDI is not available because the drivers could not be found or loaded."
            )
        return func(*args, **kwargs)

    return wrapper


@requires_ftd2xx
def list_ftdi_devices(valid_only: bool = False, bytes_to_str: bool = False):
    """Lists all available FTDI devices.

    Args:
        valid_only (bool): remove devices that list as empty.
        bytes_to_str (bool): convert entries that are `bytes` to `str`.

    Returns:
        A dict of {dev_index: dev_detail_dict}.
    """
    if not isinstance(valid_only, bool):
        raise TypeError(
            f'Argument "valid_only" must be bool, not {type(valid_only).__name__}'
        )
    if not isinstance(bytes_to_str, bool):
        raise TypeError(
            f'Argument "bytes_to_str" must be bool, not {type(valid_only).__name__}'
        )

    devices = ftd.listDevices() or {}  # listDevices() can return None
    devices = {
        i: {
            k: v.decode() if bytes_to_str and type(v) is bytes else v
            for k, v in ftd.getDeviceInfoDetail(i).items()
        }
        for i, _ in enumerate(devices)
    }
    if valid_only:
        return {k: v for k, v in devices.items() if len(v.get("serial", "")) != 0}
    return devices


@requires_ftd2xx
def index_from_serial(value: str) -> int:
    """Get a device index given a part of a serial number. Case sensitive!

    Args:
        serial(str): Serial number to test, can be the shortened from the end.

    Returns:
        The device index that has a matching serial number.

    Raises:
        FTDIError if there was a problem listing devices or if there
        is no device with a matching serial number.
    """
    if not isinstance(value, str):
        raise TypeError("Serial Number must be a string.")

    try:
        return (
            [
                i
                for i, detail in list_ftdi_devices().items()
                if detail["serial"].decode()[-len(value) :] == value
            ]
        )[
            0
        ]  # Will raise IndexError if there is no match
    except ftd.DeviceError:
        raise FTDIError("Failed to scan FTDI devices.")
    except IndexError:
        raise FTDIError("No device exists with a matching serial number.")


@requires_ftd2xx
def index_from_comport(comport: "str | int") -> int:
    """Retrieves the device index from the com port it is connected to.

    Args:
        comport (str, int): the comport. If a string, must be formatted
            as either a '#' or 'com#', where "#" is the comport number.

    Returns:
        The device index

    Raises:
        ValueError if the given string is invalid
        TypeError if given an invalid argument type
        FTDIError if ftd2xx is unavailable or there is no device at the given com port.
    """
    if isinstance(comport, str):
        try:
            if "com" in comport.lower():
                comport = int(comport[3:])
            else:
                int(comport)
        except:
            raise ValueError("Invalid string supplied.")
    elif not isinstance(comport, int):
        raise TypeError("COM port must be a str or int.")

    ftdi_idx = -1
    for dev_idx in range(len(list_ftdi_devices())):
        try:
            ftdi_com = get_ftdi_com_port(dev_idx)
        except (FTDIError, ValueError):
            continue
        except NotImplementedError:
            break
        if ftdi_com == comport:
            ftdi_idx = dev_idx
            break
    if ftdi_idx == -1:
        raise FTDIError(f"No device at the given COM port: {comport}")
    return ftdi_idx


@requires_ftd2xx
def get_ftdi_com_port(device: "int | str") -> int:
    """Gets the COM port associated with an FTDI device

    Args:
        device (int, str): the device index or serial number

    Returns:
        The COM port as an int.

    Raises:
        TypeError if `device` is not an int or str.
        ValueError if there is no such device with the given serial number.
        FTDIError if there was a problem locating the device or opening it.
        NotImplementedError if the function isn't available for the system
    """
    if isinstance(device, int):
        index = device
    elif isinstance(device, str):
        try:
            index = index_from_serial(device)
        except (ValueError, FTDIError):
            raise
    else:
        raise TypeError("Device must be index (int) or serial number (str)")

    # ftd2xx exceptions are non-descriptive, need to split try-except blocks
    try:
        ser = ftd.open(index)  # not a context manager
    except ftd.DeviceError:
        raise FTDIError("Could not open the device at the given index.")

    try:
        comport = ser.getComPortNumber()
        if comport < 0:
            raise ValueError()
    except (ftd.DeviceError, ValueError):
        raise FTDIError("No COM port associated with index")
    except AttributeError:
        raise NotImplementedError("FT_GetComPortNumber is only available on windows")
    finally:
        ser.close()
    return comport


@requires_ftd2xx
def available_comports() -> list:
    """List available comports using the FTDI driver.

    Currently windows only.

    COM ports not using the FTDI driver will not show up.

    Returns:
        A list of comports

    Raises:
        FTDIError: if ftd2xx is unavailable
    """
    avail_ports = []
    # List available devices
    devices = ftd.listDevices() or {}
    for i, dev in enumerate(devices):
        # Open device
        try:
            ser = ftd.open(i)
        except ftd.DeviceError:
            pass
        else:
            # Read port num
            comnum = ser.getComPortNumber()

            comnum = f"{i}: COM{comnum}, {ser.getDeviceInfo()}"
            avail_ports.append(comnum)

            ser.close()

    return avail_ports
