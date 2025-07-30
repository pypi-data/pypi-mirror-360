"""

"""
from logging import getLogger

from naludaq.board import Board
from naludaq.tools.adc2mv.adc_linear_regression import ADCLinearReg
from naludaq.tools.dac_sweep.dac_sweep_controller import DACSweepController

LOGGER = getLogger(__name__)


def generate_convertion_data(
    board: Board,
    dac_steps: int,
    stats: list = [],
    minimum_r2: float = 0.9998,
    minimum_range: int = 10,
):
    """Add calibration data to the board

    Adds calibration data to the board for adc2mV conversion.

    Args:
        board: good old board
        dac_steps (int): amount of steps to divide the sweep in.
        stats: storage for progress messages
        minimum_r2:
        minimum_range:

    Raises:
        Unknown for now.
    """

    dsc = DACSweepController(board)
    adclr = ADCLinearReg(board)
    try:
        dsc.progress = stats
        adclr.progress = stats
    except:
        stats.append((0, "Calibration failed"))
        return
    dac_step = calc_step_size(board, dac_steps)
    LOGGER.debug("Will run calibration with step size: %s", dac_step)
    output2analyze = dsc.dac_sweep(step_size=dac_step)
    LOGGER.debug("Run linear regression on DAC sweep data: %s", len(output2analyze))
    caldata = adclr.linear_regression(output2analyze, minimum_r2, minimum_range)
    LOGGER.debug("Calibration data is: %s", caldata)
    board.caldata = caldata


def calc_step_size(board, steps):
    """Calculate the dac sweep step size based on amount of steps.

    Args:
        board: good ol' board object
        steps: amount of steps
    """

    max_counts = board.params.get("ext_dac", 0).get("max_counts", 0)
    min_counts = 0

    return (max_counts - min_counts) // steps
