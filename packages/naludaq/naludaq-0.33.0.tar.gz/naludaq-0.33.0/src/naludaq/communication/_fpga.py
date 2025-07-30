from . import _common as helpers
from .registers import ReadRegistersABC, WriteRegistersABC


class FpgaRegisters(WriteRegistersABC, ReadRegistersABC):
    def __init__(self, board, register_type: str):
        """Communication with FPGA registers.

        Args:
            board (Board): the board object.
            register_type (str): the type of registers to use.
        """
        super().__init__(board, register_type)
        self._write_cmd = 0xAF
        self._read_cmd = 0xAD
        self._width_cmd = 2
        self._width_addr = 2  # hex char
        self._width_val = 4  # hex char

    # ---------------------------------------------------------------------
    # Write
    # ---------------------------------------------------------------------
    def generate_write(self, name: str, value: int = None) -> str:
        """Generates a command string for writing to a register.

        This function does not change any hardware or software registers.

        Args:
            name (str): the name of the register
            value (int): the value, or None to use the value held in the software register.

        Returns:
            The command string

        Raises:
            ValueError if the address, value or generated command is invalid
            TypeError if the value is an invalid type
        """
        self._validate_name_or_raise(name)
        name = name.lower()
        addr = self._get_addr_from_name_or_raise(name)
        addr_value = self._get_value_from_addr(addr)
        if value is not None:
            addr_value = helpers.substitute_value(
                addr_value, value, self.registers[name]
            )
        return self.generate_write_addr(addr=addr, value=addr_value)

    def generate_write_addr(self, addr: "int|str", value: int = None) -> str:
        """Generates a command string for writing to a register.

        This function does not change any hardware or software registers.

        Args:
            addr (str): the address of the register
            value (int): the value, or None to use the value held in the software register.

        Returns:
            The command string

        Raises:
            ValueError if the address, value or generated command is invalid
            TypeError if the value is an invalid type
        """
        addr = helpers.normalize_address(addr, self._width_addr)
        if value is None:
            value = self._get_value_from_addr(addr)
        self._validate_value_or_raise(value, bitwidth=self._width_val * 4)
        return self._generate_write_atom(addr, value)

    def _generate_write_atom(self, addr: str, value: int) -> str:
        cmd = f"{self._write_cmd:X}"
        cmd_addr = addr.zfill(self._width_addr)
        val = f"{value:X}".zfill(self._width_val)
        command = f"{cmd}{cmd_addr}{val}"
        return command.upper()

    def set(self, name: str, value: int):
        """Set boardparam digital register, do not change the state of the FPGA

        Args:
            name: Register name.
            value: Register value.
        """
        name = name.lower()
        self._validate_name_or_raise(name)
        self._validate_value_or_raise(value, bitwidth=self.registers[name]["bitwidth"])
        self.registers[name]["value"] = value

    def set_addr(self, addr: str, value: int):
        """Update any registers sharing the addr with their part of the value"""
        self._validate_value_or_raise(value, bitwidth=self._width_val * 4)
        for reg in self.registers_on_address(addr.lower()).values():
            val = value >> reg["bitposition"]
            val &= 2 ** reg["bitwidth"] - 1
            reg["value"] = val

    def _get_value_from_addr(self, addr):
        """Generate the value from the hex address.

        An address can contain multiple registers.
        Generate the value depending on the bit positions of all registers on the address.

        Args:
            addr(str): Hex value of the address, 2 hex char long.

        Returns:
            integer value of the combined registers.

        Raises:
            AttributeError if address is not in the registers.
        """
        regs = self.registers_on_address(addr.lower()).values()
        if len(regs) == 0:
            raise AttributeError("Address not found")

        value = 0
        for reg in regs:
            key_value = reg["value"]
            reg["address"]
            key_pos = reg["bitposition"]
            key_width = reg["bitwidth"]

            value += 2**key_pos * (int(key_value) % (2**key_width))
        return value

    # ---------------------------------------------------------------------
    # Read
    # ---------------------------------------------------------------------
    def generate_read_addr(self, addr: "int | str") -> str:
        return self._generate_read_atom(addr)
