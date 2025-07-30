"""Factory for the gainstage controller"""


def get_gainstage_controller(board, *args, **kwargs):
    """Return a gainstage controller for the given board"""
    if board.model == "aodsv2_eval":
        from .aodsv2 import GainStageController

        return GainStageController(board)
    elif board.model == "aodsoc_aods":
        from .oddsock_aods import GainStageController

        return GainStageController(board, *args, **kwargs)
    else:
        raise NotImplementedError(
            "No gainstage implemented for %s" % board
        )  # pragma: no cover
