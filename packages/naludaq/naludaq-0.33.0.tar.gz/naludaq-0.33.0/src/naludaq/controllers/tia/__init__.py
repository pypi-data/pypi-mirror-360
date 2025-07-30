"""Tia controllers

The TIA circuit on the board is a trans impedence amplifier.
https://en.wikipedia.org/wiki/Transimpedance_amplifier

It's a current to voltage converter and it's purpose is to convert current
to a signal our boards can measure (voltage).

Only a selected few boards have a TIA on-board.
To control the TIA use the get_tia_controller function.

"""
from .hdsoc import HdsocTIAController


def get_tia_controller(board, *args, **kwargs):
    """Get the correct TIA controller based on the board model.

    Currently only HDSoCv1 has a TIA controller.

    Args:
        board (Board): the board object.

    Returns:
        The appropriate TIA for the given board.
    """
    controller = {
        "hdsocv1": HdsocTIAController,
        "hdsocv1_evalr1": HdsocTIAController,
        "hdsocv1_evalr2": HdsocTIAController,
    }.get(board.model, None)
    if controller is None or not board.is_feature_enabled("tia_dac"):
        raise NotImplementedError(f"{board.model} does not support the TIAController")
    return controller(board, *args, **kwargs)
