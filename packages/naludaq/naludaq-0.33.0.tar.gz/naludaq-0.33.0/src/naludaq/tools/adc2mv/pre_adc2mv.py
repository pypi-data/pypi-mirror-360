# Builtin
import gzip
import os
import pickle
from logging import getLogger
from pathlib import Path

# Internal
from naludaq.board import Board
from naludaq.tools.adc2mv.adc_linear_regression import ADCLinearReg
from naludaq.tools.dac_sweep.dac_sweep_controller import DACSweepController

# 3rd Party


LOGGER = getLogger(__name__)


def dac_sweep_and_lin_regression(
    board: Board,
    dac_step: int,
    filename: Path,
    minimum_r2: float = 0.9998,
    minimum_range: int = 10,
) -> dict:
    """
    Performs a dac sweep and calculates the linear region and
    linear regression. Stores the linear region and regression
    values to board.sample_lr and to file, and returns it.

    Args:
        board (naludaq.board): Board object to be used for dac sweep
        dac_step (int): Step size between dac values in dac counts
        filename (path): Location to store linear reg. values
        minimum_r2 (float): The minimum R-squared value for a region
            to be considered linear
        minimum_range (int): The minimum amount of points within a
            linear region
    Raises:
        TypeError if filename is None
        NotADirectoryError if the filename is not a valid path

    """
    if filename is None:
        raise TypeError("Supplied filename is NoneType.")
    path, _ = os.path.split(filename)
    if not os.access(os.path.dirname(filename), os.W_OK):
        raise NotADirectoryError(f"Not a valid file directory: {path}")

    dsc = DACSweepController(board)
    adclr = ADCLinearReg(board)
    output2analyze = dsc.dac_sweep(step_size=dac_step)
    lr_dict = adclr.linear_regression(output2analyze, minimum_r2, minimum_range)
    board.sample_lr = lr_dict

    # Save lr_list

    try:
        sfile = gzip.GzipFile(filename, "w", compresslevel=4)
        pickle.dump(lr_dict, sfile, protocol=pickle.HIGHEST_PROTOCOL)
    except IOError as error_msg:
        LOGGER.error("File could not be created. %s", error_msg)
        raise
    except pickle.PicklingError as error_msg:
        LOGGER.error("Saving lr_list failed: %s", error_msg)
        raise

    return lr_dict


def set_lr_dict(board: Board, filename: Path) -> bool:
    """
    Set the lr_dict for the board, to be used for adc2mv per sample.

    Args:
        board (naludaq.board): The board to load the lr_dict into
        filename (path): The location of the lr_dict file

    Returns:
        loaded (bool): True if file was successfully set, false otherwise.
    """
    loaded = True
    try:
        with gzip.open(filename, "rb") as fp:
            lr_list = pickle.load(fp)
            board.sample_lr = lr_list
    except IOError as error_msg:
        LOGGER.error("File could not be loaded. %s", error_msg)
        loaded = False
    except pickle.UnpicklingError as error_msg:
        LOGGER.error("Unpickling the data failed: %s", error_msg)
        loaded = False

    return loaded
