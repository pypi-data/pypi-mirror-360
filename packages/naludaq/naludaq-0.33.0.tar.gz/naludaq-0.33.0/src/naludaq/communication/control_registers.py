"""Control Register
=================

Control registers change functinality of the FPGA.

The control registers are FPGA specific values,
by changing these, the FPGA changes it's operation.

They are stored in two places, in the board object and
in the physical hardware. It's possible to change them independently.

Command structure:
------------------
Updating a digital command uses a format 'CCAAVVVV'

- CC (8-bit): tells the FPGA command parser to expect a control register command.
- AA (8-bit): address
- VVVV (16-bit): value

Will be interpereted by the FPGA as hex. it's 32-bit = 8 hex values.

Examples:
Read the values back from the board
ctrl_reg_vals = read_control_registers(board)

If there is a missmatch the board-objects value can be overwritten:
read_control_registers(board, overwrite=True)

Examples:
----------

.. code-block: python

    dc = DigitalRegisters(board)
    dc.read("regname")
    dc.write("regname", intvalue)

"""
from logging import getLogger

from naludaq.communication import _fpga
from naludaq.helpers.semiton import SemitonABC

LOGGER = getLogger(__name__)


class ControlRegisters(_fpga.FpgaRegisters, SemitonABC):
    """Control Registers

    Attributes:
        board:
    """

    def __init__(self, board):
        super().__init__(board, "control_registers")
