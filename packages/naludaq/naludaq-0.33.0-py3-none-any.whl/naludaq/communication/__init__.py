""" Communication module.
=======================

Communicate with the different registries on the board.
Changing registries changes how the board and the chip operates.
This module gives the user low level control on how the board operates
through the 5 primary modules:
- analog registers
- digital registers
- control registers
- i2c
- serial

"""
from logging import getLogger

from .analog_registers import AnalogRegisters
from .chip_selection import select_chips, select_chips_commands, selected_chips
from .control_registers import ControlRegisters
from .digital_registers import DigitalRegisters
from .i2c import *
from .i2c_registers import I2CRegisters

LOGGER = getLogger(__name__)


def debug_mode(board, activate=True):
    """Turn on debug on board.

    Normally the digital side of the ASIC handles the communication with
    the Analog portions but with debug enabled, all Analog commands
    are sent directly to the Analog part of the chip instead of to
    the digital part.

    This bypasses the digital controls entirely.

    Warning!
    Changes a ton of stuff in software and hardware so be careful
    Use at own risk!

    Args:
        active(bool): True enables debug mode, False disables
    """
    ControlRegisters(board).write("debug", activate)


def write_all_registers(board):
    """Updates all available registers to hardware.

    Will grab all the register variables stored in the board.params
    and send them to the hardware board.
    This function effectively sync the hardware with the software.

    Usefull to run on startup when the board is in a blank state or
    after running a program on the hardware that require the board to be
    returned to a known state.

    Args
        board (Board): Good ol' board object.
    """
    reg_types = [
        AnalogRegisters,
        ControlRegisters,
        DigitalRegisters,
        I2CRegisters,
    ]
    for reg in reg_types:
        try:
            reg(board).write_all()
        except (ValueError, TypeError, AttributeError) as error_msg:
            LOGGER.debug("Update registers failed due to : %s", error_msg)
        except KeyError as error_msg:
            LOGGER.debug("Can't update register due to KeyError: %s", error_msg)
        except Exception as error_msg:
            LOGGER.exception(
                "Update registers failed due to unknown error: %s", error_msg
            )
