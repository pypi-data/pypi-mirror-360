"""
Controls how the analog portion of the UDC chip is biased. 
The chip can either use a current mirror to bias the amplifiers (current mode)
or an internal DAC to set the bias voltage (voltage mode).

You can also choose which side to set, so the left can be one mode, and the right could be the other,
if you need to.

Current mode is presumed to be more stable, however the bias value cannot be changed
Voltage mode is presumed to be less stable, but allows for the flexibility of changing the bias voltage

NOT to be confused with External DAC biasing. This biasing affects the stability and performance of the
amplifiers IN the chip. Has nothing to do with external DAC biasing for the input signal.

Kenneth Lauritzen
"""

from naludaq.helpers.exceptions import InvalidBoardModelError


def get_biasing_mode_controller(board):
    """Retrieves the appropriate biasing mode controller.
    Currently, only the UDC16 supports different biasing modes.

    Args:
        board (Board): board to change biasing mode
    """

    if board.model in ["udc16"]:
        from .udc16 import BiasingModeControllerUDC16

        return BiasingModeControllerUDC16(board)

    raise InvalidBoardModelError("Only UDC16 supports biasing mode")
