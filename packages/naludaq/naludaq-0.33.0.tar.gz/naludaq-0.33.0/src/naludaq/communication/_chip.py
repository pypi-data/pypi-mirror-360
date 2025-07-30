"""Module containing base classes for register spaces which are split into multiple chips
-- analog and digital registers.

Commands generated will be wrapped in chip selection commands which will select the appropriate
chips before sending the command, and restore the previous chip selection afterwards. The general
layout of generated pseudo-commands might look like:

- Select chips
- Write address
- Restore chips

This multichip stuff is a bit tricky. The basic idea is that you can write to multiple chips
at once, and the commands generated will be optimized to minimize the number of commands
sent to the board. A true multichip broadcast (same command sent to all boards) is not always
possible because registers living on the same address may have different values for
different chips. In this case, any differing commands will have their own selection logic.
However, a command which is the same for all chips will be broadcast to all chips at once.
A command which ends up being split into multiple commands will look like this:

- Select some chips
- Write address
- Select other chips
- Write address
...
- Restore chips

Some consequences of this implementation are that doing something like `DigitalRegisters.write_addr(addr)`
might generate a very long command, while `DigitalRegisters.write_addr(addr, value)` will generate
a very short command. This is because the former MAY generate a command for each chip.

Multichip reads are currently not supported because we don't have a parser for them, or
consistent firmware support. For now, reads are only supported from one chip at a time.
"""
import functools
import typing
from collections import defaultdict

from . import _common as helpers
from .chip_selection import wrap_command
from .registers import ReadRegistersABC, WriteRegistersABC


def raise_if_multiple_chips(fn):
    """Raise a NotImplementedError if the number of chips selected is greater than 1."""

    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        if len(self.chips) > 1:
            raise NotImplementedError("Cannot read from multiple chips at once")
        return fn(self, *args, **kwargs)

    return wrapper


class ChipRegisters(WriteRegistersABC, ReadRegistersABC):
    def __init__(
        self, board, register_type: str, chips: "int | list[int] | None" = None
    ):
        super().__init__(board, register_type)
        self.chips = chips

    @property
    def chips(self) -> list[int]:
        """Get/set the currently selected chips.

        Can be set to a single chip number, a list of chip numbers, or None (all chips).
        """
        return self._chips

    @chips.setter
    def chips(self, chips: "int | list[int] | None"):
        if isinstance(chips, int):
            chips = [chips]
        elif isinstance(chips, typing.Iterable):
            chips = list(chips)
        elif chips is None:
            chips = list(range(self.board.available_chips))
        else:
            raise TypeError(
                f"chips must be int, list[int], or None, not {type(chips).__name__}"
            )
        if len(chips) == 0:
            raise ValueError("Need to write to at least one chip")
        if any(not 0 <= chip < self.board.available_chips for chip in chips):
            raise ValueError("Invalid chip index")
        self._chips = chips

    # ---------------------------------------------------------------------
    # Write
    # ---------------------------------------------------------------------
    def generate_write(self, name: str, value: int = None) -> str:
        """Generate a write command for the given register.

        This will generate a sequence of commands on multichip boards.
        Since different chips can have different values on neighboring registers,
        multiple commands may be required to write to a single register on different chips
        to avoid inadvertently overwriting neighboring registers on other chips;
        in other words, true broadcast is not possible in the general case.

        Args:
            name (str): the name of the register
            value (int): the value to write to the register. If None,
                the current value of the register will be written.

        Returns:
            str: the command to write the given value to the given register
        """
        self._validate_name_or_raise(name)
        name = name.lower()
        if value is not None:
            bitwidth = self.registers[name]["bitwidth"]
            self._validate_value_or_raise(value, bitwidth)
        return self._wrap_commands(
            [self._generate_write_name_atom(chip, name, value) for chip in self.chips]
        )

    def generate_write_addr(self, addr: "int | str", value: int = None) -> str:
        """Generate a write command for the given address.

        To avoid inadvertently overwriting neighboring registers on other chips,
        multiple commands may be required to write to a single address on different chips;
        in other words, true broadcast is not possible in the general case.

        Args:
            addr (int | str): the address to write to.
            value (int): the value to write to the address. If None,
                the current value of the register will be written.

        Returns:
            str: the command to write the given value to the given address
        """
        if isinstance(addr, int):
            addr = f"{addr:X}"
        if not isinstance(addr, str):
            raise TypeError("Address should be either a hex string or integer")
        self._validate_addr_or_raise(addr)

        return self._wrap_commands(
            [self._generate_write_addr_atom(chip, addr, value) for chip in self.chips]
        )

    def _generate_write_addr_atom(
        self,
        chip: int,
        addr: "int | str",
        value: int = None,
    ) -> str:
        """Generate a write command "atom" for an address for a single chip.

        Args:
            chip (int): Chip number.
            addr (int | str): Address to write to.
            value (int): Value to write to the address. If None, the value from the
                software register will be used.

        Raises:
            ValueError: if the address is invalid

        Returns:
            str: Write command for the given address and chip.
        """
        addr = addr.zfill(self._width_addr).upper()
        if value is None:
            try:
                value = self._addr_value(addr, chip)
            except AttributeError:
                raise ValueError(f"No value found for address {addr}")
        self._validate_value_or_raise(value, bitwidth=self._width_val * 4)
        return self._generate_write_atom(addr, value)

    def _generate_write_name_atom(self, chip: int, name: str, value: int) -> str:
        """Generate a write command "atom" for a register for a single chip.

        Args:
            chip (int): Chip number.
            name (str): Name of the register to write to.
            value (int): Value to write to the register.

        Returns:
            str: Write command for the given register and chip.
        """
        name = name.lower()
        addr = self._get_addr_from_name_or_raise(name)
        if value is not None:
            addr_val = int(self._addr_value(addr, chip))
            value = helpers.substitute_value(addr_val, value, self.registers[name])
        return self._generate_write_addr_atom(chip, addr, value)

    def _wrap_commands(self, commands: list[str]) -> str:
        """Collapse a list of commands into a single command with chip selection.

        Condenses commands which are identical except for the chip number into a single
        broadcasted write.

        Args:
            commands (list[str]): list of commands to collapse.

        Returns:
            str: the collapsed command
        """
        if len(commands) != len(self.chips):
            raise ValueError(
                f"Expected {len(self.chips)} commands, but got {len(commands)} commands"
            )
        collapsed = defaultdict(list)
        for chip, command in zip(self.chips, commands):
            collapsed[command].append(chip)
        command = "".join(
            wrap_command(
                self.board,
                command,
                chips,
                restore=(i == len(collapsed) - 1),
                wait=bool(len(chips) > 1),
            )
            for i, (command, chips) in enumerate(collapsed.items())
        )
        return command

    def set(self, name: str, value: int):
        values = self.registers[name.lower()]["value"]
        for chip in self.chips:
            values[chip] = value

    def set_addr(self, addr: str, value: int):
        self._validate_value_or_raise(value, bitwidth=self._width_val * 4)
        for name, reg in self.list_registers().items():
            if reg["address"].lower() != addr.lower():
                continue
            val = helpers.full_to_partial_value(value, reg)
            self.set(name, val)

    def _addr_value(self, addr: str, chip: int) -> int:
        """Get the current value of the software register at the given address.

        Args:
            addr (str): the address in hex string format
            chip (int): the chip number

        Returns:
            int: the current value of the register
        """
        regs = self.registers_on_address(addr)
        return functools.reduce(
            lambda value, reg: (
                value | helpers.partial_to_full_value(reg, reg["value"][chip])
            ),
            regs.values(),
            0,
        )

    # ---------------------------------------------------------------------
    # Read
    # ---------------------------------------------------------------------
    def generate_read_addr(self, addr: "int | str") -> str:
        command = self._generate_read_atom(addr)
        command = wrap_command(self.board, command, self.chips)
        return command


_SINGLE_CHIP_FNS = [
    "read",
    "read_all",
    "read_many",
    "generate_read",
    "generate_read_addr",
]
for _name in _SINGLE_CHIP_FNS:
    _fn = getattr(ChipRegisters, _name)
    _fn = raise_if_multiple_chips(_fn)
    setattr(ChipRegisters, _name, _fn)
