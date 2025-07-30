"""Class containing all functions to control the boards.

All functions to communicate with the Nalu boards are
collected here. The Facade naludaq is intended to simplify
the interface for general use.
"""
import logging

from .connection_controller import ConnectionController
from .upac import UPACConnectionController
from .upac96 import Upac96ConnectionController

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name


def get_connection_controller(board):
    """Get the correct connection controller based on the board model.

    Args:
        board (Board): the board object.

    Returns:
        The appropriate ConnectionController for the given board.
    """

    return {
        "upac32": UPACConnectionController,
        "upaci": UPACConnectionController,
        "upac96": Upac96ConnectionController,
        "zdigitizer": UPACConnectionController,
    }.get(board.model, ConnectionController)(board)
