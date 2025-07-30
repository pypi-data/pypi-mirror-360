"""Generates tuning parameters for isel ramp current and cap select.

Uses linear regression by finding the slope of the average channel data
between the highest and lowest value of cap select at different ramp current
values. The slope and y-int is then used to determine what values of ramp
current and cap select will get the channel average to the target value.

The tool will return a dict with the register names as the keys and the values
is a list of values to program per channel.

    Tuning parameters are of the form:
    {
        0 (Channel): {
            isel_ramp_current: (value),
            isel_cap_select: (value),
        }
    }
"""
from naludaq.io.io_manager import load_calibration_data, save_gzip_data

from .udc16 import UDC16ConversionRampOptimizer


def get_conversion_ramp_optimizer(board):
    """Sets the appropriate isel ramp/cap to put the channels in midrange.

    Args:
        board (Board): the board
        channels (list[int]): channels to generate pedestals for. Defaults to all channels.

    Returns:
        An instantiated Conversion ramp optimizer for the given board.

    Raises:
        NotImplementedError if the given board does not support pedestals.
    """

    conversion_ramp_optimizers = {
        "udc16": UDC16ConversionRampOptimizer,
        "upac96": UDC16ConversionRampOptimizer,
    }.get(board.model, None)

    if not conversion_ramp_optimizers or not board.is_feature_enabled(
        "conversion_ramp_optimizer"
    ):
        raise NotImplemented(
            f'Board "{board.model}" does not have support for the conversion ramp optimizer.'
        )
    return conversion_ramp_optimizers(board)


def load_conversion_ramp_file(
    fname: str,
    board,
):
    """Loads conversion ramp tuning parameters from a file, programs
    the parameters to the board, and returns the tuning parameters

    Args:
        fname (str): File name of gzip pickled tuning dictionary
        board (Board): Board to tune conversion ramp
    """
    suggested_vals = load_calibration_data(fname)
    tuner = get_conversion_ramp_optimizer(board)
    tuner._update_isel_for_channels(suggested_vals)
    board.tuning["conversion_ramp"] = suggested_vals
    return suggested_vals


def save_conversion_ramp_file(fname: str, board):
    """Saves conversion ramp tuning parameters from
    board.tuning to a file as a gzip pickle
    Args:
        fname (str): File name to save gzip pickled tuning dictionary
        board (Board): Board to grab conversion ramp tuning parameters
    """
    data = board.tuning.get("conversion_ramp", None)
    if data is None:
        raise KeyError("Board does not have conversion_ramp tuning parameter")
    save_gzip_data(filename=fname, data=data)
