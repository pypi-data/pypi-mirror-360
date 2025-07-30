"""Set board-level dac values.

The Nalu boards have DACs external to the chip. The DAC need to be set during boot.
Once the dacs have been set, it's easy to change them.

There are different types of dacs depending on the board model and revision.
This is abstracted away from the user by having a single user interface for all different boards.
By using a single interface the DACs can be set without the user needing to know details about
the board and the DAC chip specific implementations.

Note: Some boards do not have an onboard DAC chip.

The DACs in use are have different addressing and value space,
thus they need to be intialized and operated differently.

License: LGPL v3
See LICENSE.txt
"""
from naludaq.helpers.exceptions import InvalidBoardModelError

from .aardvarcv3 import DacControllerAardvarcv3
from .ad5671 import DACControllerAD5671
from .base import BaseDACController as _DACController
from .dac7578 import DACControllerDAC7578
from .hdsoc import DACControllerHDSoC
from .hdsocv2 import DACControllerHDSoCv2
from .hiper import DACControllerHiper
from .trbhm import DACControllerTRBHM
from .upac32 import DacControllerUpac32


def get_dac_controller(board) -> _DACController:
    """Gets the DAC controller appropriate for a given board.

    Args:
        board (Board): the board object.

    Returns:
        The DAC controller

    Raises:
        InvalidBoardModelError if the given board does not have
            a DAC controller
    """
    if not board.is_feature_enabled("ext_dac"):
        raise InvalidBoardModelError("The given board does not support DAC control")

    controller = {
        "aardvarcv3": DacControllerAardvarcv3,
        "aardvarcv4": DacControllerAardvarcv3,
        "aodsv1": DACControllerAD5671,
        "aodsv2_eval": DACControllerAD5671,
        "asocv3": DACControllerAD5671,
        "asocv3s": DACControllerAD5671,
        "hdsocv1": DACControllerHDSoC,
        "hdsocv1_evalr1": DACControllerHDSoC,
        "hdsocv1_evalr2": DACControllerHDSoC,
        "hdsocv2_eval": DACControllerHDSoCv2,
        "hdsocv2_evalr2": DACControllerHDSoCv2,
        "hiper": DACControllerHiper,
        "trbhm": DACControllerTRBHM,
        "dsa-c10-8": DACControllerTRBHM,
        "udc16": DACControllerDAC7578,
        "upac32": DacControllerUpac32,
        "upac96": DACControllerDAC7578,
        "aodsoc_aods": DACControllerDAC7578,
        "aodsoc_asoc": DACControllerDAC7578,
    }.get(board.model, None)
    if controller is None:
        raise InvalidBoardModelError(f"No DAC controller for {board.model}")

    return controller(board)
