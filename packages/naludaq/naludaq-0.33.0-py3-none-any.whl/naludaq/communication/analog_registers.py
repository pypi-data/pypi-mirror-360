"""Analog registers
===================
Registers controlling the analog part of the ASIC.

What are the analog registers?
It's a set of registers on the FPGA matching a set of registers on the chip
By changing these registers it controls the analog portion of the chip.

Command structure:
------------------
Updating the analog command uses a format 'BXMAAVVV'

- B tells the FPGA command parser to expect a analog/digital command.
- M is mode, 0 = write, 1 = read
- AA = address
- VVV = value

Will be interpereted by the FPGA as hex. it's 32-bit = 8 hex values.

Functions:
----------
- write_all
- write
- write2addr


"""
from logging import getLogger

from naludaq.communication._chip import ChipRegisters
from naludaq.communication.digital_registers import DigitalRegisters

LOGGER = getLogger(__name__)


class AnalogRegisters(ChipRegisters):
    def __init__(self, board, chips: "int | list[int]" = None):
        """Registers controlling the analog part of the ASIC(s).

        For a more thorough explanation of the multichip aspect and its implications,
        see the `multichip` module.

        Args:
            board (Board): board object
            chips (int | list[int] | None): chip(s) to write to. If None, all chips are assumed.
        """
        super().__init__(board, "analog_registers", chips)
        self._write_cmd = 0xB00
        self._width_cmd = 3
        self._width_addr = 3  # hex char
        self._width_val = 3  # hex char

        self._fix_timing = self._select_fixtiming_method()

    def _select_fixtiming_method(self):
        """Select the timing fix method depending on the board model.

        Some boards have a different wiring and require a different caluclation.

        Returns:
            timing correction function for the current board.
        """
        if self.board.model in ["hdsocv2_eval", "hdsocv2_evalr2"]:
            return self._fix_timing_even
        return self._fix_timing_odd

    # READ #########################################################

    def _addr_value(self, addr: str, chip: int):
        """Reimplemented to correct strobe values."""
        if self.board.params.get("strobe_values_correction", False):
            result = self._correct_strobes(addr, chip)
        else:
            result = super()._addr_value(addr, chip)
        return result

    def _correct_strobes(self, addr: str, chip: int) -> int:
        """Generate the value from the hex address.

        An address can contain multiple registers.
        Generate the value depending on the bit positions of all registers on the address.

        Args:
            addr (str): Hex value of the address, 2 hex char long.

        Returns:
            int: value of the combined registers.

        Raises:
            AttributeError if the address is not valid.
        """
        addr = addr.upper()
        strobe_correction_keys = self.board.params.get("strobe_correction_keys", [])
        value = 0
        for name, register in self.registers_on_address(addr).items():
            if not isinstance(register["value"], list):
                register["value"] = [register["value"]]
            reg_value = register["value"][chip]
            reg_pos = register["bitposition"]
            reg_width = register["bitwidth"]

            # FIX TIMING REGS, ACCORDING TO BOARD PARAMETER timing_correction
            if name in strobe_correction_keys:
                reg_value = self._fix_timing(reg_value)
            value += 2**reg_pos * (int(reg_value) % (2**reg_width))
        return value

    def _generate_write_atom(self, addr: str, value: int) -> str:
        """Generate the string to send to the board.

        OVERLOAD the standard way of generating the command since the analog command parsing
        sometimes

        Abstracts the model differences away from the main code, AARDVARCv2 got a timing hack.

        Args:
            board(obj)
            name(str): name of the analog register
            value(): Value to set the register to.
        """
        write_addr = f"{self._write_cmd:X}"
        cmd_addr = addr[1:] if len(addr) == 3 else addr
        set_ext = restore_ext = ""
        if len(addr) == 3 and addr[0] == "1":
            set_ext, restore_ext = self._generate_ext_bit_commands()
        if isinstance(value, (int, bool)):
            value = f"{value:X}".zfill(self._width_val)
        command = f"{write_addr}{cmd_addr}{value}"  # First 5 hex chars, address should be 3 hex. B001c
        return f"{set_ext}{command}{restore_ext}"

    def _fix_timing_odd(self, in_value: int, *args, **kwargs):
        """The timing signal data mux is all mixed up for simplicity of routing, so this fixes it

        Don't use unless you know what it does. Contains hardcoded values.
        """
        samples = self.board.params["samples"]

        if in_value < samples:
            fixed = in_value * 2 + 1
        else:
            fixed = 2 * ((2 * samples) - in_value - 1)
        return fixed

    def _fix_timing_even(self, in_value: int, *args, **kwargs):
        """The timing signal data mux is all mixed up for simplicity of routing, so this fixes it

        Don't use unless you know what it does. Contains hardcoded values.
        """
        samples = self.board.params["samples"]

        if in_value < samples:
            fixed = in_value * 2
        else:
            fixed = 2 * ((2 * samples) - in_value - 1) + 1
        return fixed

    def _generate_ext_bit_commands(self) -> tuple[str, str]:
        """Generate commands to set or clear the external bit.

        Args:
            board (Board): the board
            wait (bool): whether to include a wait command
            restore (bool): whether to include a restoration command

        Returns:
            tuple[str, str]: set, clear commands
        """
        dr = DigitalRegisters(self.board)
        set_cmd = dr.generate_write("address_ext", True)
        clear_cmd = dr.generate_write("address_ext", False)
        return set_cmd, clear_cmd
