from .default import DefaultAutoTrigger


def get_autotrigger(board, interval: float = 1) -> DefaultAutoTrigger:
    """Gets the autotrigger module for the given board.

    Args:
        interval (float): the interval to wait between sending triggers.
    """
    # this weird code is intended for forward-compatibility
    return {}.get(board.model, DefaultAutoTrigger)(board, interval)
