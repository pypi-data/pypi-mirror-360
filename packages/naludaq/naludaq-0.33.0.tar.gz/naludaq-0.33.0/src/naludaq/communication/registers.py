"""Base class for registers.
"""
import abc
from abc import ABC
from collections import defaultdict
from functools import wraps
from logging import getLogger
from typing import Iterable, List

from naludaq.backend.exceptions import ConnectionError
from naludaq.backend.managers.connection import ConnectionManager
from naludaq.backend.managers.io import BoardIoManager
from naludaq.helpers.exceptions import InvalidRegisterError

from . import _common as helpers

LOGGER = getLogger(__name__)


def clear_buffer(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """Clears the board buffer before"""
        if self.board.using_new_backend:
            device = ConnectionManager(self.board).device
            if device is None:
                raise ConnectionError("There is no active connection")
            device.clear_buffers()
        else:
            self.board.connection.reset_input_buffer()
        rv = func(self, *args, **kwargs)

        return rv

    return wrapper


class Registers(ABC):
    """Base class for communication with registers.
    This class should not be used directly; use one of the subclasses instead.

    Inheritence tree:

    ```mermaid
    graph TD;
        Registers --> ChipRegisters
        Registers --> FpgaRegisters
        ChipRegisters --> DigitalRegisters
        ChipRegisters --> AnalogRegisters
        FpgaRegisters --> ControlRegisters
        FpgaRegisters --> I2CRegisters
    ```

    Atrributes:
    -----------

        board: The board to update the registers on.
        width_cmd (int): width of the command type in hex chars
        width_addr (int): width of the address in hex chars
        width_val (int): width of the value in hex chars
        width_total (int): total width of the command in hex chars

    """

    def __init__(self, board, register_type: str):
        self.board = board
        self._register_type = register_type
        if not isinstance(getattr(board, "registers", None), dict):
            raise InvalidRegisterError("The board is lacking valid registers")
        if not board.registers.get(register_type, None):
            raise InvalidRegisterError(f"The registers is lacking {register_type}")
        self._width_cmd = 3
        self._width_addr = 2  # hex char
        self._width_val = 3  # hex char
        self._width_total = 8  # common firmware

        self._stopword = None
        self.stopword = self.board.params.get(
            "register_stop_word",
            self.board.params["stop_word"],
        )

    @property
    def stopword(self):
        """Get/Set stopword"""
        return self._stopword

    @stopword.setter
    def stopword(self, value):
        if not isinstance(value, (int, str, bytes)):
            raise TypeError(f"stopword must be str, bytes or hex, got {type(value)}")
        elif isinstance(value, str):
            if len(value) % 2 != 0:
                raise ValueError(
                    "Since stopword converts to bytes, it must be of even length."
                )
            value = bytes.fromhex(value)
        elif isinstance(value, int):
            value = bytes.fromhex(f"{value:X}")
        self._stopword = value

    @property
    def registers(self) -> dict:
        """Shortcut to board registers"""
        return self.board.registers[self._register_type]

    @abc.abstractmethod
    def set(self, name: str, value: int):
        """Set the value of a register without writing to the board.

        Args:
            name (str): Name of the register.
            value (int): Value to set the register to.
        """

    @abc.abstractmethod
    def set_addr(self, addr: "str | int", value: int):
        """Set the value of registers on the given address without
        writing to the board.

        Args:
            addr (str | int): Address of the register.
            value (int): Value to set the register to.
        """

    # VALIDATIONS ############################################################
    #
    ##########################################################################
    def _validate_addr_or_raise(self, addr: str):
        """Validate the address type and make sure it exists.

        Args:
            addr(str): Hex value of address.

        Raises:
            ValueError if addr is not a valid hex or if it doesn't exist in register
            TypeError if addr is not a string or int
        """
        if not isinstance(addr, str):
            raise TypeError("Register number needs to be an integer")
        if addr.zfill(self._width_addr).upper() not in self.list_addresses():
            raise ValueError(f"Address {addr} does not exist in {self._register_type}")

    def _validate_name_or_raise(self, name):
        """Name is a user input, make sure it's valid.

        Args:
            name(str): Name of the analog register.

        Returns:
            True if name is valid, False if it's not.

        Raises:
            TypeError and ValueError
        """
        if not isinstance(name, str):
            raise TypeError(f"Name: {name} is of the wrong type: {type(name)}")
        if name.casefold() not in [k.casefold() for k in self.registers.keys()]:
            raise ValueError(f"Name: {name} is not a valid analog register.")

    def _validate_names_or_raise(self, names: Iterable[str]):
        """Validate list of register names or raise an error."""
        if not isinstance(names, Iterable):
            raise TypeError("Names must be Iterable[str]")
        for name in names:
            self._validate_name_or_raise(name)

    def _validate_value_or_raise(self, value: int, bitwidth: int):
        """Value is a user input, make sure it's valid.

        Args:
            value: Value to set the analog register to.

        Raises:
            TypeError: if the value is of the wrong type.
            ValueError: if the Value is not positive.
        """
        if not isinstance(value, (type(None), int)):
            raise TypeError(f"Value argument is of the wrong type: {type(value)}")
        if isinstance(value, int) and not 0 <= value < 2**bitwidth:
            raise ValueError("Value argument must be  a positive integer.")

    def _validate_value_map_or_raise(self, values: dict[str, int]):
        """Validate the given value map or raise an error"""
        if not isinstance(values, dict):
            raise TypeError("Values must be dict[str, int]")
        for name, value in values.items():
            self._validate_name_or_raise(name)
            bitwidth = self.registers[name]["bitwidth"]
            self._validate_value_or_raise(value, bitwidth)

    # HELPERS ################################################################
    #
    # A set of helper functions used by all registers
    #
    ##########################################################################

    def _get_addr_from_name_or_raise(self, name):
        """Returns the control registers addr from the name.

        Args:
            name(str): Name of the control register

        Returns:
            The number of the control register
        """
        if not isinstance(name, str):
            raise TypeError("Register name must be a strign")

        addr = self.registers.get(name.casefold(), False)
        if addr is False:
            raise InvalidRegisterError(f"{name} is not a valid register.")
        addr = addr["address"]
        if isinstance(addr, int):
            addr = f"{addr:X}"  # pragma: no cover
        addr = addr.zfill(self._width_addr)
        return addr.upper()

    def _validate_command_or_raise(self, command: str):
        """Make sure a generated command is of the right length."""
        if len(command) != self.width_total:
            raise ValueError(
                f"Generated command is invalid. A command must be {self.width_total} char, got {command} or length {len(command)}"
            )  # pragma: no cover

    # COMMON #################################################################
    #
    # A list of convenience tools, common for all registers.
    #
    ##########################################################################
    def list(self) -> list:
        """Lists the name of all available registers.

        Returns:
            A list of all register names
        """
        return list(k.lower() for k in self.registers.keys())

    def list_registers(self) -> dict:
        """Returns all available registers as a dict, organized in the
        same way as the registers file.

        Returns:
            A dict containing all registers
        """
        return self.registers

    def list_addresses(self) -> List[str]:
        """Generate a list of all available addresses.

        This is useful since an address can contain multiple registers.
        The register name can correspond to one or many bits at a specific address.

        Returns:
            List of available addresses in hex (str)
        """
        reg_addr = {
            helpers.normalize_address(value["address"], self._width_addr)
            for value in self.registers.values()
        }
        return sorted(list(reg_addr), key=lambda x: int(x, 16))

    def registers_on_address(self, addr: str) -> dict[str, dict]:
        self._validate_addr_or_raise(addr)
        addr = helpers.normalize_address(addr, self._width_addr)
        return {
            name: value
            for name, value in self.registers.items()
            if helpers.normalize_address(value["address"], self._width_addr) == addr
        }

    def show(self, name: str) -> str:
        """Returns the internal contents of a register.

        Args:
            name (str): The name of the register

        Returns:
            A string representation of the given register.

        Raises:
            TypeError if the name is not a string
            ValueError if the name is not a valid register
        """
        self._validate_name_or_raise(name)

        return self.registers[name]

    def _send_command(self, cmd):
        """Send request to the board"""
        if self.board.using_new_backend:
            BoardIoManager(self.board).write(cmd)
        else:
            self.board.connection.send(cmd)

    def __repr__(self):
        return f"{type(self).__name__}: {self.registers}(board = {self.board})"  # pragma: no cover


class WriteRegistersABC(Registers):
    def write(self, name: str, value: int = None):
        if value is not None:
            self.set(name, value)
        command = self.generate_write(name, value)
        self._send_command(command)

    def write_addr(self, addr: "int | str", value: int = None):
        if value is not None:
            self.set_addr(addr, value)
        command = self.generate_write_addr(addr, value)
        self._send_command(command)

    def write_all(self):
        for addr in self.list_addresses():
            self.write_addr(addr)

    def write_many(self, value_map: dict[str, int]):
        """Write several registers at once.

        Args:
            registers (dict[str, int]): mapping of register values to names
        """
        self._validate_value_map_or_raise(value_map)

        # update all software registers first to prevent generate_write
        # from using potentially old register values in subsequent writes
        for name, value in value_map.items():
            self.set(name, value)

        addresses = {
            self._get_addr_from_name_or_raise(name) for name in value_map.keys()
        }
        commands = [self.generate_write_addr(addr) for addr in addresses]
        command = "".join(commands)
        self._send_command(command)

    @abc.abstractmethod
    def generate_write(self, name: str, value: int = None) -> str:
        pass

    @abc.abstractmethod
    def generate_write_addr(self, addr: str, value: int = None) -> str:
        pass

    def _generate_write_atom(self, addr: str, value: int) -> str:
        cmd = f"{self._write_cmd:X}"
        cmd_addr = addr.zfill(self._width_addr)
        val = f"{value:X}".zfill(self._width_val)
        command = f"{cmd}{cmd_addr}{val}"
        return command.upper()


class ReadRegistersABC(Registers):
    def read(self, name: str) -> dict:
        """Read from a register with a name.

        Args:
            name: Name of the register.

        Raises:
            ValueError if name is not in register.
            TypeError if name is not a str.
        """
        self._validate_name_or_raise(name)
        addr = self.registers[name]["address"]
        return self.read_addr_named(addr)[name]

    def read_addr(self, addr: "int | str") -> int:
        """Read an address and return the value.

        Args:
            addr (str | int): 8-bit address to read as either int or hex.
        """
        command = self.generate_read_addr(addr)
        return self._read_response(command)

    def read_addr_named(self, addr: "int | str") -> dict:
        """Read an address and return the register dicts for all registers
        on that address.

        Args:
            addr (str | int): address to read as either int or hex.

        Returns:
            dict: {name: register_dict}
        """
        addr_value = self.read_addr(addr)
        return {
            name: reg.copy() | {"value": helpers.full_to_partial_value(addr_value, reg)}
            for name, reg in self.registers.items()
            if reg["address"].upper() == addr.upper()
        }

    def read_all(self) -> list:
        """Read all digital registers from the board.

        Reads the values based on the register number rather than the name.

        Args:
            board

        Returns:
            dictionary with {reg_num: values,}
        """
        if self.board.using_new_backend:
            addresses = self.list_addresses()
            commands = [self.generate_read_addr(addr) for addr in addresses]
            values = {}
            answers = BoardIoManager(self.board).read_all(commands)
            for address, answer in zip(addresses, answers):
                parsed_answer = self._parse_response(answer)["value"]
                reg = self._registers_from_addr_value(address, parsed_answer)
                values.update(reg)
        else:
            values = {
                name: register
                for addr in self.list_addresses()
                for name, register in self.read_addr_named(addr).items()
            }
        return values

    def read_many(self, names: list[str]) -> dict:
        """Read several registers at once.

        Do not use this function to read the same register multiple times,
        as older values will be discarded.

        Args:
            names (Iterable[str]): names of registers to read

        Returns:
            list[int]: list of register values in the same order as provided.

        Raises:
            TimeoutError: if one or more registers could not be read in time.
        """
        self._validate_names_or_raise(names)

        # cannot perform concurrent reads without naludaq_rs
        if not self.board.using_new_backend:
            return [self.read(name)["value"] for name in names]

        # sort registers & generate by address to reduce # of commands
        addresses = defaultdict(list)
        for name in names:
            addr = self._get_addr_from_name_or_raise(name)
            addresses[addr].append(name)
        read_cmds = [self.generate_read_addr(addr) for addr in addresses.keys()]

        # response order is guaranteed to be the same as the commands sent
        try:
            responses = BoardIoManager(self.board).read_all(read_cmds)
        except TimeoutError:
            raise

        # parse responses into registers by address
        values = {}
        for (addr, addr_names), response in zip(addresses.items(), responses):
            addr_value = self._parse_response(response)["value"]
            registers = self._registers_from_addr_value(addr, addr_value)
            for name in addr_names:
                values[name] = registers[name]["value"]

        sorted_values = [values[name] for name in names]
        return sorted_values

    def generate_read(self, name: str) -> str:
        """Generate and return the read command as hex"""
        return self.generate_read_addr(self.registers[name]["address"])

    @abc.abstractmethod
    def generate_read_addr(self, addr: "int | str") -> str:
        """Generate and return the read addr command as hex"""
        pass

    def _generate_read_atom(self, addr: "int | str") -> str:
        """Generate a read command for a single address.

        Args:
            addr (int | str): Address to read from.

        Returns:
            str: Command to send to the board.
        """
        if isinstance(addr, int):
            addr = f"{addr:X}"
        cmd = f"{self._read_cmd:X}"
        cmd_addr = addr.zfill(self._width_addr)
        val = "0".zfill(self._width_val)
        command = f"{cmd}{cmd_addr}{val}"
        return command.upper()

    @clear_buffer
    def _read_response(self, command: str) -> int:
        """Send a read command to the board and parse the response.

        Args:
            command (str): command to send to the board.

        Returns:
            int: value read from the board. Value is -1 if the read failed.
        """
        try:
            if self.board.using_new_backend:
                response = BoardIoManager(self.board).read(command)
            else:
                self._send_command(command)
                response = self.board.connection.read_until(self.stopword)
        except TimeoutError:  # pragma: no cover
            return -1  # pragma: no cover
        return self._parse_response(response)["value"]

    def _parse_response(self, buffer: bytes) -> dict:
        """Parses a raw binary answer into a dictionary.

        Args:
            buffer (bytes): Response to parse.

        Returns:
            dict: parsed response containing keys: "header", "read_reg", "value".
        """
        header = int.from_bytes(buffer[0:2], byteorder="big", signed=False)
        value = int.from_bytes(buffer[2:4], byteorder="big", signed=False)
        return {
            "header": header,
            "read_reg": header & 0xFF,
            "value": value,
        }

    def _registers_from_addr_value(self, addr: str, addr_value: int) -> dict:
        _registers = {}
        for name, reg in self.registers.items():
            if reg["address"].upper() == addr.upper():
                _registers[name] = reg.copy()
                _registers[name]["value"] = helpers.full_to_partial_value(
                    addr_value, reg
                )

        return _registers

        return {
            name: {"value": helpers.full_to_partial_value(addr_value, reg)}
            for name, reg in self.registers.items()
            if reg["address"].upper() == addr.upper()
        }


# validation #################################################################
#
##############################################################################
def validate_registermap_or_raise(registers):
    """Validate a regmap, raises error if it's not valid."""

    # invert registers
    inv_register = invert_regmap(registers)

    # find potential conflicts
    try:
        conflicts = find_conflicting_registers(inv_register)
    except Exception as e_msg:
        raise InvalidRegisterError(f"Following register have conflicting bits: {e_msg}")
    # if potential conflicts
    if conflicts:
        raise InvalidRegisterError(
            f"Following register have conflicting bits: {conflicts}"
        )

    return True


def find_conflicting_registers(registers):
    """Takes an inverted regmap and finds all conflicts

    Args:
        registers (dict): register dictionary and find all conflicts.

    Returns:
        dictionary with conflictingaddresses and conflicting names.
    """
    conflict_regs = defaultdict(list)
    inv_regmap = invert_regmap(registers)  # {addr: [(name, reg)]}
    for addr, regs in inv_regmap.items():
        if len(regs) <= 1:
            continue

        regs = sorted(regs, key=lambda i: i[1]["bitposition"])
        for idx, (name1, item1) in enumerate(regs[:-1]):
            item1_end = item1["bitposition"] + item1["bitwidth"] - 1

            for name2, item2 in regs[idx + 1 :]:
                if item2["bitposition"] > item1_end:
                    break
                conflict_regs[addr].append(name1)
                conflict_regs[addr].append(name2)

    conflict_regs = {addr: sorted(set(names)) for addr, names in conflict_regs.items()}
    return conflict_regs


def invert_regmap(registers):
    """Invert a regmap dict to return addr: register instead of name: register

    Args:
        registers (dict): register map {name: registers}

    Returns:
        Dictionary with {address: register}
    """
    all_regs = defaultdict(list)

    for key, val in registers.items():
        addr = val["address"]
        all_regs[addr].append((key, val))

    return all_regs
