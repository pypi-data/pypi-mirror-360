"""Peripherals controller controlls sensors on the board.

"""
from .peripherals_controller import PeripheralsController


def get_peripherals_controller(board) -> PeripheralsController:
    """Gets the appropriate peripherals controller for the given board.

    Since there is only one peripherals controller at the moment,
    the controller returned is always `PeripheralsController`.

    Args:
        board (Board): the board object

    Returns:
        The peripherals controller for the board.
    """
    if board.model in ["aodsoc_asoc", "aodsoc_aods"]:
        from .aodsoc import AodsocPeripheralsController

        return AodsocPeripheralsController(board)
    if board.model in [
        "hdsocv1",
        "hdsocv1_evalr1",
        "hdsocv1_evalr2",
        "hdsocv2_eval",
        "hdsocv2_evalr2",
    ]:
        from .hdsoc import HdsocPeripheralsController

        return HdsocPeripheralsController(board)
    if board.model in ["upac32"]:
        from .upac import UpacPeripheralsController

        return UpacPeripheralsController(board)
    if board.model in ["upac96"]:
        from .upac96 import PeripheralsControllerUpac96

        return PeripheralsControllerUpac96(board)
    if board.model in ["aardvarcv3"]:
        from .aardvarcv3 import Aardvarcv3PeripheralsController

        return Aardvarcv3PeripheralsController(board)

    from .peripherals_controller import PeripheralsController

    return PeripheralsController(board)
