"""IO module is for saving and loading from disk.

"""
import gzip
import os
import pickle
from collections import deque
from logging import getLogger
from pathlib import Path
from typing import Union

from naludaq.models import acq_converters
from naludaq.models.acquisition import Acquisition

from .io_manager import IOManager

LOGGER = getLogger(__name__)

disk_io = IOManager()


def save_file(filename: str, data):
    """Saves a python object as pickled data.

    This function should be upgraded to a proper factory.
    """
    if filename is None:
        raise TypeError("Supplied pathname is NoneType.")

    path, _ = os.path.split(filename)
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a valid directory: {path}")

    try:
        sfile = gzip.GzipFile(filename, "w", compresslevel=4)
        pickle.dump(data, sfile, protocol=pickle.HIGHEST_PROTOCOL)
    except IOError as error_msg:
        LOGGER.error("File could not be created. %s", error_msg)
    except pickle.PicklingError as error_msg:
        LOGGER.error("Saving acquisition failed: %s", error_msg)


def load_file(filename: str):
    """Loads a python pickled file.

    This function should be upgraded to a factory.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"No file found: {filename}")

    try:
        sfile = gzip.GzipFile(filename, "r")
        output = pickle.load(sfile)
    except EOFError as error_msg:
        LOGGER.error("Reached the end of the file, msg: %s", error_msg)
    except IOError as error_msg:
        LOGGER.error("File could not be loaded. %s", error_msg)
    except pickle.UnpicklingError as error_msg:
        LOGGER.error("Loading pedestals failed: %s", error_msg)
    else:
        return output


def load_pickle_acquisition(path: Union[str, Path]) -> Acquisition:
    """Loads an acquisition from a pickle file.

    Will upgrade files using the old acquisition format
    to the current version.

    Args:
        path (str, Path): the file on disk to load.

    Raises:
        FileNotFoundError if the file does not exist or is not a file.
        EOFError, UnpicklingError if the file is not a valid gzip/pickle file.
        IOError if there was a problem opening the file.

    Returns:
        The loaded acquisition
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No file found: {path}")

    try:
        with gzip.GzipFile(path, "rb") as f:
            output = pickle.load(f)
    except EOFError as error_msg:
        LOGGER.error("Reached the end of the file, msg: %s", error_msg)
        raise error_msg
    except IOError as error_msg:
        LOGGER.error("File could not be loaded. %s", error_msg)
        raise error_msg
    except pickle.UnpicklingError as error_msg:
        LOGGER.error("File could not be loaded. %s", error_msg)
        raise error_msg

    # Upgrade all acquisitions. Converting to the same version is cheap
    return acq_converters.upgrade_old_acquisition(output)


def save_pickle_acquisition(acq: Union[deque, Acquisition], path: Union[str, Path]):
    """Saves an acquisition or deque to a pickle file on the disk.

    Acquisitions are pickled as a dict so they can be opened elsewhere
    without naludaq installed.

    Args:
        acq (deque, Acquisition): the acquisition to save
        path (str, Path): the output file location

    Raises:
        TypeError if the given acquisition is not a deque or `Acquisition`.
        IOError if there was a problem opening the file.
    """
    if not isinstance(acq, (Acquisition, deque)):
        raise TypeError(f"Expected an Acquisition or deque, not {type(acq)}")
    try:
        with gzip.GzipFile(path, "wb", compresslevel=4) as f:
            if isinstance(acq, Acquisition):
                pickle.dump(acq.as_dict(), f, protocol=pickle.HIGHEST_PROTOCOL)
            elif isinstance(acq, deque):
                pickle.dump(acq, f, protocol=pickle.HIGHEST_PROTOCOL)
    except IOError as error_msg:
        LOGGER.error("File could not be loaded. %s", error_msg)
        raise error_msg
    except pickle.PicklingError as error_msg:
        LOGGER.error("File could not be saved. %s", error_msg)
        raise error_msg
