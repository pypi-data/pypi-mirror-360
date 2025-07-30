"""Module contains the base class for I2C devices.
"""
import logging
import time
import typing

import numpy as np

from naludaq.communication.i2c_registers import I2CRegisters
from naludaq.helpers.exceptions import I2CError

from .device import Device

logger = logging.getLogger("naludaq.i2c_device")
_bytes_like_types = (bytes, bytearray)
_BytesLike = typing.Union[bytes, bytearray]


class I2CDevice(Device):
    def __init__(self, board, addr: int):
        """Base class for software representation of I2C devices.

        Communication with the physical I2C bus is handled through
        register reads/writes with the FPGA.

        The class is not abstract, as it is possible to communicate
        with any I2C device without defining a subclass for it.

        Args:
            board (board): board object
            addr (int): 7-bit address of the device.

        Raises:
            TypeError if the address is an invalid type.
            ValueError if the address is out of bounds.
        """
        self._validate_addr_or_raise(addr)

        super().__init__()
        self._board = board
        self._addr = addr
        self._send_delay = 0.001  # pause AFTER sending

        self._num_command_regs = board.params.get("i2c", {}).get("max_command_words", 4)
        self._num_response_regs = board.params.get("i2c", {}).get(
            "max_response_words", 4
        )
        self._max_response_width = (self._num_response_regs - 1) * 2

    @property
    def board(self):
        """The board object used to communicate with the device."""
        return self._board

    @property
    def address(self) -> int:
        """The device address (7-bit)"""
        return self._addr

    def write_register(self, reg: int, data: _BytesLike, *, check_ack: bool = False):
        """Writes a register on the device.

        Args:
            reg (int): register to write to
            data (bytes-like): data to write into the register
            check_ack (bool): whether to check if the device acknowledged the operation.

        Raises:
            I2CErrror: if `check_ack=True` and the device did not acknowledge the data sent.
        """
        self._validate_reg_or_raise(reg)
        self._validate_data_or_raise(data)
        self.send_write_command(bytes([reg]) + data, check_ack=check_ack)

    def read_register(self, reg: int, *, width: int, check_ack: bool = False) -> bytes:
        """Reads a register on the device.

        Args:
            reg (int): register to read from
            width (int): width in bytes of the register on the device.
            check_ack (bool): whether to check if the device acknowledged the operation.

        Returns:
            The register value as `bytes`.

        Raises:
            I2CErrror: if `check_ack=True` and the device did not acknowledge the data sent.
        """
        self._validate_reg_or_raise(reg)
        self._validate_reg_width_or_raise(width)

        self.send_write_command(bytes([reg]), check_ack=check_ack)
        time.sleep(0.01)
        self.send_read_command(bytes([0xFF]) * width, check_ack=check_ack)

        response = self._read_response_registers()

        # first byte is junk
        result = self._discard_ack_bits(response)[1 : width + 1]
        return result

    def send_write_command(self, data: _BytesLike, check_ack: bool = False):
        """Sends a write command to the device.

        The rw bit of the address byte is set to 0, indicating a write operation.

        Args:
            data (bytes-like): the data to write to the device, not including the address byte.
            check_ack (bool): whether to check if the device acknowledged the operation.

        Raises:
            I2CErrror: if `check_ack=True` and the device did not acknowledge the data sent.
        """
        self._send_command(data, rw_bit=0, check_ack=check_ack)

    def send_read_command(self, data: _BytesLike, check_ack: bool = False) -> bytes:
        """Sends a read command to the device.

        The rw bit of the address byte is set to 1, indicating a read operation.

        Args:
            data (bytes-like): the data to write to the device, not including the address byte.
            check_ack (bool): whether to check if the device acknowledged the operation.

        Raises:
            I2CErrror: if `check_ack=True` and the device did not acknowledge the data sent.
        """
        self._send_command(data, rw_bit=1, check_ack=check_ack)

    def _send_command(self, data: _BytesLike, *, rw_bit: int, check_ack: bool):
        """Writes to an I2C device.

        Args:
            data (bytes-like): the data to write to the device, not including the address bytes
            rw_bit (int): the r/w bit, 0 (False) for a write, or 1 (True) for a read.
            check_ack (bool): whether to check if the device acknowledged the operation.

        Raises:
            I2CError if the command could not be sent, or if
                `check_ack=True` and the device did not acknowledge the operation.
        """
        self._validate_data_or_raise(data)
        self._validate_check_ack_or_raise(check_ack)
        logger.debug(
            "Writing to device 0x%02x (r/w=%s): %s",
            self._addr,
            rw_bit,
            [hex(x) for x in data],
        )

        addr_byte = (self._addr << 1) | rw_bit
        self._update_fpga_registers(addr_byte, data)
        I2CRegisters(self.board).transmit_command()

        if check_ack:
            time.sleep(0.01)
            response = self._read_response_registers()
            self._validate_acks_or_raise(response, len(data) + 1, rw_bit)

    def _update_fpga_registers(self, addr_byte: int, data: _BytesLike):
        """Updates the I2C registers on the FPGA.

        Changes the following registers:
        - i2c_addr: set to the address of the device, including the r/w bit.
        - i2c_words: set to the number of data bytes
        - i2c_data{0-3}: set to the data _words_. If `len(data) < 8`, the data
        array is left-padded with zeros.

        Args:
            addr_byte (int): the full address byte of the device, including
                the r/w bit.
            words (bytes-like): the bytes to store in the data registers.
        """
        self._write_fpga_register(
            "i2c_words", len(data)
        )  # NOTE: i2c_words is the number of bytes
        self._write_fpga_register("i2c_addr", addr_byte)

        # np.frombuffer() needs an even number of bytes
        if len(data) % 2 == 1:
            data = b"\x00" + data

        words = np.frombuffer(data, ">H")
        words = np.pad(words, (self._num_command_regs - len(words), 0))
        registers = {f"i2c_data{i}": int(value) for i, value in enumerate(words)}
        I2CRegisters(self.board).write_many(registers)

    def _read_response_registers(self) -> "list[int]":
        """Reads all the response registers from the FPGA and splits them into a list.

        Returns:
            list[int]: the responses. Each element is 9 bits wide (8 data + 1 ACK).
        """
        registers = [f"response{i}" for i in range(self._num_response_regs)]
        responses = I2CRegisters(self.board).read_many(registers)
        phrase = "".join(f"{response:016b}" for response in responses)
        phrase = phrase[::-1]
        phrases = [
            int(phrase[i * 9 : (i + 1) * 9], 2)
            for i in range(2 * self._num_response_regs - 1)
        ]
        return phrases

    def _write_fpga_register(self, name: str, value: int):
        """Writes to an I2C register on the FPGA."""
        I2CRegisters(self.board).write(name, value)

    def _read_fpga_register(self, name: str) -> int:
        """Reads an I2C register on the FPGA"""
        return I2CRegisters(self.board).read(name)["value"]

    @staticmethod
    def _validate_acks_or_raise(
        response: "list[int]",
        num_bytes_sent: int,
        rw_bit: int,
    ):
        """Checks whether the ACK/NACK bits in a response follow the
        appropriate sequence of ACK/NACK for a read or write sequence.

        ACK bits are represented by 0, and NACK bits are represented by 1.
        All acknowledge bits should be ACK (0) _except_ for the last bit
        in a read operation.

        Args:
            response (list[int]): the response read from the FPGA registers.
            num_bytes_sent (int): the total number of bytes sent to the device
                in the last read/write operation.
            rw_bit (int): the r/w bit, 1 for read, 0 for write.

        Raises:
            I2CError if the command was not acknowledged by the device.
        """
        # ACK = 0, NACK = 1
        # Last ack bit is NACK for read operations and ACK for write operations
        ack_bits = [x & 1 for x in response[:num_bytes_sent]]
        expected_ack_bits = [0] * (num_bytes_sent - 1) + [rw_bit]
        if ack_bits != expected_ack_bits:
            raise I2CError("Device did not acknowledge the data written")

    @staticmethod
    def _discard_ack_bits(response: "list[int]") -> bytes:
        """Discards the least significant bits (ACK/NACK) in a list of
        response phrases, converting it from a list of 9-bit values
        to bytes.

        Args:
            response (list[int]): the response as a list of 9-bit-wide values.

        Returns:
            bytes: The response without ACK/NACK bits.
        """
        return bytes([x >> 1 for x in response])

    def _validate_reg_width_or_raise(self, width: int):
        """Makes sure the register width is between 0 and the maximum
        allowed for the board.

        Args:
            width (int): the width in bytes

        Raises:
            TypeError: if the width is not an int
            ValueError: if the width is out of bounds
        """
        if not isinstance(width, int):
            raise TypeError("Width must be an int")
        if not 0 < width <= self._max_response_width:
            raise ValueError(
                f'Width "{width}" is out of bounds (1-{self._max_response_width})'
            )

    @staticmethod
    def _validate_addr_or_raise(addr: int):
        """Ensure address is an int and is 7 bits max.

        Unfortunately there's no way of telling whether we've been
        given an 8-bit address which can be represented by fewer, so
        e.g. 8-bit 0x02 (7-bit 0x01) won't raise an error.

        Args:
            addr (int): the address

        Raises:
            TypeError: if the address is not an int
            ValueError: if the address is not in the range 1 - 127 inclusive.
        """
        if not isinstance(addr, int):
            raise TypeError(f"Address must be an int, not {type(addr).__name__}")
        if not 0 <= addr <= 127:
            raise ValueError(f"Address {addr} is out of bounds (0-127)")

    @staticmethod
    def _validate_reg_or_raise(reg: int):
        """Ensure a register number has the right type and value.

        Args:
            reg (int): the register number

        Raises:
            TypeError: if the register number is not an int
            ValueError: if the value is not in the range 0-255 inclusive.
        """
        if not isinstance(reg, int):
            raise TypeError(f"Register must be an int, not {type(reg).__name__}")
        if not 0 <= reg <= 255:
            raise ValueError(f"Register {reg} is out of bounds (0-255)")

    @staticmethod
    def _validate_data_or_raise(data: _BytesLike):
        """Ensure a data array is bytes-like (bytes or bytearray)

        Args:
            data (bytes-like): the data array

        Raises:
            TypeError: if the object has the wrong type.
        """
        if not isinstance(data, _bytes_like_types):
            raise TypeError(
                f"Data must be a bytes-like object, not {type(data).__name__}"
            )

    @staticmethod
    def _validate_check_ack_or_raise(check_ack: bool):
        """Validate the `check_ack` flag.

        Args:
            check_ack (bool): the check_ack flag.

        Raises:
            TypeError: If the flag is not a bool
        """
        if not isinstance(check_ack, bool):
            raise TypeError(
                f"`check_ack` flag must be a bool, not {type(check_ack).__name__}"
            )
