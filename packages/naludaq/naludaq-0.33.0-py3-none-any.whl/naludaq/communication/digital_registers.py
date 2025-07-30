"""Digital Registers
====================
Registers controlling the digital part of the ASIC.

This is reliant on the digital_registers portion of the .yml file.

These registers control the digital side of the ASICs.
By changing these registers it's possible to
change how and what the ASIC is reading.

Command structure:
------------------
Updating a digital command uses a format 'B01AAVVV'

- B tells the FPGA command parser to expect a analog/digital command.
- M is mode, 0 = write, 1 = read
- AA = address
- VVV = value

Will be interpereted by the FPGA as hex. it's 32-bit = 8 hex values.

Example:
---------

.. code-block: python

    dc = DigitalRegisters(board)
    dc.read("regname")
    dc.write("regname", intvalue)

"""
from logging import getLogger

from naludaq.communication import _chip

LOGGER = getLogger(__name__)


class DigitalRegisters(_chip.ChipRegisters):
    def __init__(self, board, chips: "int | list[int]" = None):
        """Registers controlling the digital part of the ASIC(s).

        For a more thorough explanation of the multichip aspect and its implications,
        see the `multichip` module.

        Args:
            board (Board): board object
            chips (int | list[int] | None): chip(s) to read/write. If None, all chips are assumed.
                Only one chip may be read from at a time!
        """
        super().__init__(board, "digital_registers", chips)
        self._write_cmd = 0xB01
        self._read_cmd = 0xB42
        self._width_cmd = 3
        self._width_addr = 2  # hex char
        self._width_val = 3  # hex char

    @_chip.raise_if_multiple_chips
    def read_all(self):
        """Read all registers.
        Reimplemented to bypass the new backend way of doing this.

        Returns:
            dict: register values structured as {reg_name: reg dict}
        """
        # Digital registers have no command ID, so we need to read them synchronously
        values = {
            name: register
            for addr in self.list_addresses()
            for name, register in self.read_addr_named(addr).items()
        }
        return values

    @_chip.raise_if_multiple_chips
    def read_many(self, names: list[str]) -> list[str]:
        """Read several registers at once.
        Reimplemented to bypass the new backend way of doing this.

        Args:
            names (Iterable[str]): names of registers to read

        Returns:
            list[int]: list of register values in the same order as provided.
        """
        self._validate_names_or_raise(names)

        # Digital registers don't have command IDs so concurrent reads are dangerous
        return [self.read(name)["value"] for name in names]
