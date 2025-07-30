import gzip
import os
import pickle

from naludaq.helpers.exceptions import PedestalsIOError
from naludaq.tools.pedestals.generators import (
    get_pedestals_generator as get_pedestals_controller,
)
from naludaq.tools.pedestals.pedestals_correcter import PedestalsCorrecter


def get_pedestals_from_file(filename):
    """Load the pedestal gzipped and pickled.
    The pedestals object is returned.
    Args:
        filename: valid filename
    Returns:
        Pedestals data.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"No file found: {filename}")

    try:
        sfile = gzip.GzipFile(filename, "r")
        outped = pickle.load(sfile)
    except EOFError:
        raise PedestalsIOError("Unexpected end of file")
    except IOError as e:
        raise PedestalsIOError(f"File could not be loaded: {e}")
    except pickle.UnpicklingError as e:
        raise PedestalsIOError(f"Not a valid pickle file: {e}")
    else:
        if not isinstance(outped, dict):
            raise TypeError(f"Not a valid Pedestals file: {filename}")

        return outped


def save_pedestals(pedestals, filename):
    """Save the pedestal in binary format for backwards compatibility."""
    if not isinstance(pedestals, dict):
        raise TypeError(f"pedestals must be a dict, got {type(pedestals)}")
    if filename is None:
        raise TypeError("Supplied pathname is NoneType.")
    path, _ = os.path.split(filename)
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a valid directory: {path}")

    try:
        sfile = gzip.GzipFile(filename, "w", compresslevel=4)
        pickle.dump(pedestals, sfile, protocol=pickle.HIGHEST_PROTOCOL)
    except IOError as e:
        raise PedestalsIOError(f"File could not be written: {e}")
    except pickle.PicklingError as e:
        raise PedestalsIOError(f"Object cannot be serialized: {e}")
