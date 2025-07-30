"""Collection of helper functions used in all modules.

"""
import datetime
import os
import socket
import sys
from collections import defaultdict
from typing import Iterable

import numpy as np
import numpy.typing as npt


def type_name(obj) -> str:
    """Get the name of an object's type.

    Args:
        obj (any): any object (classes are objects too!)

    Returns:
        The name as a string.
    """
    return type(obj).__name__


def swap_dict_key_and_val(to_swap: dict) -> dict:
    """Swap dict.

    Returns:
        {v, k} from {k, v}
    """
    return {v: k for k, v in to_swap.items()}


def hex_to_int(input_hex: str) -> int:
    """Converts hexdecimal string to an integer.

    Args:
        input_hex (str): hexdecimal string

    Returns:
        Integer
    """
    return int(input_hex, 16)


def int_to_bin(value, width=4):
    """Converts an integer to a binary string.

    Args:
        value (int): the value to convert to binary
        width (int): preferred width of the string.
            If the smallest possible binary representation of the
            value has fewer bits, the result is left-padded with
            zeros.

    Returns:
        _type_: _description_
    """
    if not isinstance(value, int):
        raise TypeError("Value must be an int")
    if not isinstance(width, int):
        raise TypeError("Width must be an int")
    if value < 0:
        raise ValueError("Negative values not supported")
    if width < 0:
        raise ValueError("Negative widths not supported")
    return f"{bin(value)[2:].zfill(width)}"


def locked_deque(it, lock):
    """Makes a process safe iterator from a deque.

    The locked deque can be safely used with the
    multiprocess map. This allows threads to write to a deque
    and a process pool to read from the deque to process it.

    Args:
        it (deque): object to iterate
        lock: the multiprocess lock.
    """
    while True:
        try:
            with lock:
                value = it.pop()
        except IndexError:
            return

        yield value


def get_application_path():
    """Application path depending on run mode:
        - frozen .exe
        - commandline
        - interactive mode (eg. notebook)

    Returns:
        Path to root of application.
    """
    if getattr(sys, "frozen", False):
        application_path = os.path.dirname(sys.executable)
    else:
        try:
            app_full_path = sys.modules["__main__"].__file__
            application_path = os.path.dirname(app_full_path)

        except (NameError, AttributeError):
            application_path = os.getcwd()

    return application_path


def create_dir_if_not_exist(directory):
    """Checks if a directory exists, creates it if it doesn't.

    Returns:
        The input directory but with the directory created.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.normpath(directory)


def get_package_versions() -> tuple:
    """Get the current naludaq and naluscope versions safely.

    Will not raise an exception if naluscope is not present.

    Returns:
        A tuple of (x, y) where x = naludaq version str, and
        y = naluscope version str or `None` if not installed.
    """
    try:
        # Ugly! ideally naludaq shouldn't care about naluscope
        import naluscope

        import naludaq

        return (naludaq.__version__, naluscope.__version__)
    except:
        return (naludaq.__version__, None)


def extract_event_creation_times(events: Iterable[dict]) -> npt.NDArray[np.datetime64]:
    """Extract event creation times from a collection of events into a numpy array.
    If creation times are not present, ``np.datetime64('nat')`` (not a time) is stored
    instead.

    Args:
        events (Iterable[dict]): events.

    Returns:
        np.ndarray[np.datetime64]: array of creation times with dtype of ``np.datetime64``.
    """
    try:
        iter(events)  # raises if not iterable
    except TypeError:
        raise

    from_timestamp = datetime.datetime.fromtimestamp
    times = np.full(len(events), np.datetime64("nat"), dtype="datetime64[us]")
    for idx, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(
                f"All events must be dicts. Got {type_name(event)} instead."
            )

        creation_time = event.get("created_at", None)
        if isinstance(creation_time, (int, float)):
            creation_time = from_timestamp(creation_time)
        if not isinstance(creation_time, (np.datetime64, datetime.datetime)):
            continue
        times[idx] = np.datetime64(creation_time)

    return times


def event_transfer_time(
    board,
    windows: int,
    channels: int = None,
    margin: float = 2.0,
    overhead: float = 0,
) -> float:
    """Calculate the approximate time it takes to transfer an event from the board.

    The event size is approximated based on the number of windows and channels,
    and does not account for headers/footers (although this is typically negligible).

    Args:
        board (Board): the board object. Must have valid connection info
        windows (int): number of windows per channel in the event
        channels (int): number of channels returned in the event. Defaults to all channels.
        margin (float): value to scale the transfer time by to adjust for real-world scenarios.
        overhead (float): overhead time in seconds time to add to adjust for real-world scenarios.

    Returns:
        float: the approximate time in seconds it would take to transfer such an event.
    """
    from naludaq.backend.managers import ConnectionManager

    if channels is None:
        channels = board.channels
    speed = board.connection_info.get("speed", 115_200)
    if board.using_new_backend:
        speed = 30_000_000
        cm = ConnectionManager(board)
        if cm.is_uart_based:
            speed = cm.device.baud_rate
    # 2 bytes per sample
    event_size = channels * windows * board.params.get("samples", 64) * 2
    transfer_rate = speed // 8
    transfer_time = event_size / transfer_rate
    adjusted_time = transfer_time * margin + overhead
    return adjusted_time


def get_available_port(host: str = "127.0.0.1") -> int:
    """Get an available port for the server to use.

    Args:
        host (str): the host to bind to. Defaults to localhost.

    Raises:
        ConnectionError: if no port is available.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((host, 0))
            return s.getsockname()[1]
    except:
        raise ConnectionError("Could not find an available port")


def find_missing_channels(expected: list[int], actual: list[int]) -> list[int]:
    """Find the channels that are missing in the given list

    Args:
        expected (list[int]): the expected channels
        event (list[int]): the channels to check

    Returns:
        list[int]: the missing channels
    """
    return list(set(expected) - set(actual))


def group_channels_by_chip(
    channels: list[int], channels_per_chip: int
) -> dict[int, list[int]]:
    """Groups the given channels by chip number.

    No special handling is done for duplicates.

    Args:
        channels (list[int]): the channels to sort
        channels_per_chip (int): the number of channels per chip

    Returns:
        dict[int, list[int]]: the channels grouped as {chip: [channels]}
    """
    sorted_channels = defaultdict(list)
    for chan in channels:
        chip = chan // channels_per_chip
        sorted_channels[chip].append(chan)
    return dict(sorted_channels.items())
