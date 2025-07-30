from .default import PedestalsGenerator
from .hdsoc import PedestalsGeneratorHdsoc
from .hiper import PedestalsGeneratorHiper
from .udc16 import PedestalsGeneratorUdc16
from .upac96 import PedestalsGeneratorUpac96


def get_pedestals_generator(
    board,
    num_captures: int = 10,
    num_warmup_events: int = 10,
    channels: "list[int]" = None,
):
    """Gets the appropriate pedestals generator for a board.

    Args:
        board (Board): the board
        num_captures (int): Number of datapoints per sample, used for averaging the values.
        num_warmup_events (int): Number of initial events to discard. Helps the board
            settle and excludes events that may skew the pedestals.
        channels (list[int]): channels to generate pedestals for. Defaults to all channels.

    Returns:
        The pedestals generator

    Raises:
        NotImplementedError if the given board does not support pedestals.
    """
    if not board.is_feature_enabled("pedestals"):
        raise NotImplementedError(
            f'Board "{board.model}" does not have support for pedestals.'
        )
    if board.model in ["upac32", "upaci", "zdigitizer"]:
        raise NotImplementedError("Board is currently unsupported")

    classy = {
        "hdsocv1_evalr2": PedestalsGeneratorHdsoc,
        "hdsocv2_eval": PedestalsGeneratorHdsoc,
        "hdsocv2_evalr2": PedestalsGeneratorHdsoc,
        "udc16": PedestalsGeneratorUdc16,
        "upac96": PedestalsGeneratorUpac96,
        "hiper": PedestalsGeneratorHiper,
    }.get(board.model, PedestalsGenerator)
    return classy(board, num_captures, num_warmup_events, channels)
