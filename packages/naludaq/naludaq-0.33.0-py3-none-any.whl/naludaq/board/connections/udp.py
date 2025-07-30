import binascii
import logging
import select
import socket
import time
from typing import Optional

import numpy as np

from naludaq.board.connections.base_connection import BaseConnection
from naludaq.parsers.answer_parser import get_answer_parser

logger = logging.getLogger(__name__)

_UDP_READ_BUFFER_SIZE = 1500
_UDP_HEADER_BYTES = 16
_WRITE_MESSAGE_NIBBLES = 8
_DEFAULT_TIMEOUT = 0.005


class UDP(BaseConnection):
    def __init__(self, connection_info: dict):
        """Class for communication over an ethernet connection.

        Args:
            connection_info (dict): the connection configuration
        """
        super().__init__()

        # Store connection info
        self._receiver_addr = connection_info["receiver_addr"]
        self._board_addr = connection_info["board_addr"]

        self._model = connection_info["model"]
        self.stop_word = connection_info["stop_word"]
        self._timeout = _DEFAULT_TIMEOUT
        self.read_addr = "AD"
        self.write_addr = "AF"
        self.response_length = 8
        self.parse_answer = get_answer_parser(True)

        self.tx_pause = 0.01
        self.bundle_mode = True

        self._rx_fifo = bytearray()

        self.socket: socket.socket = None

    @property
    def receiver_addr(self) -> tuple:
        """Get/set the user command address.

        Setting the address will close and reopen the connection
        if the connection is already open

        Args:
            addr (tuple): the address
        """
        return self._receiver_addr

    @receiver_addr.setter
    def receiver_addr(self, addr: tuple):
        self._receiver_addr = addr

        # Reopen the socket
        if self.socket:
            self.close()
            self.open()

    @property
    def board_addr(self) -> tuple:
        """Get/set the board command address.

        Args:
            addr (tuple): the address
        """
        return self._board_addr

    @board_addr.setter
    def board_addr(self, addr: tuple):
        self._board_addr = addr
    
    @property
    def type(self):
        return "udp"
    
    @property
    def board_ip(self):
        """Gets the IP address of the board. 
        Alias of UDP.board_addr[0] to use the same naming convention as backend.
        """
        return self.board_addr[0]
    
    @property
    def board_port(self):
        """Gets the IP port of the board. 
        Alias of UDP.board_addr[1] to use the same naming convention as backend.
        """
        return self.board_addr[1]

    @property
    def is_open(self) -> bool:
        """Indicates whether the connection is open."""
        return self.socket is not None

    def set_answer_parser(self, new_firmware: bool = True):
        """Sets the answer parser.

        Args:
            new_firmware (bool): whether to use the parser for new firmware
        """
        self.parse_answer = get_answer_parser(new_firmware)

    def reset_input_buffer(self):
        """Discards any data currently in the input buffer.

        Closes and re-opens the socket.
        """
        self.close()
        self.open()

    def reset_output_buffer(self):
        """Not implemented for ethernet connection."""
        pass

    def __del__(self):
        self.close()

    def open(self):
        """Opens the connection."""
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(self._receiver_addr)
            # self.socket.setblocking(False)
            self.socket.settimeout(self._timeout)

    def close(self):
        """Closes the connection."""
        try:
            self.socket.close()
            self.socket = None
        except:
            pass

    def send(
        self, data: str, pause: Optional[float] = None, bundle: Optional[bool] = None
    ):
        """Sends a string of hex characters.

        Args:
            data (str): the data string. Only hex characters are allowed!
            pause (float): the time in seconds to wait after sending
        """
        if bundle is None:
            bundle = self.bundle_mode
        if pause is None:
            pause = self.tx_pause
        # Make sure the length of the input is a multiple of 8
        if len(data) % 8 != 0:
            logger.debug(
                "UDP.send(): need multiples of 8 hex chars, you gave me %s", len(data)
            )
            logger.debug("command:%s", data)
            return

        logger.debug("Sending: %s in %s mode", data, "bundle" if bundle else "single")
        if (len(data) > _WRITE_MESSAGE_NIBBLES) and bundle is False:
            for i in range(0, len(data), _WRITE_MESSAGE_NIBBLES):
                self._send(data[i : i + _WRITE_MESSAGE_NIBBLES], pause)
        else:
            self._send(data, pause)

    def _send(self, data: str, pause: float):
        # Convert hex data string to binary
        # data_binary = binascii.unhexlify(self.sync_word + data)
        data_binary = binascii.unhexlify(data)

        # Send the data over the socket
        self.socket.sendto(data_binary, self._board_addr)
        time.sleep(pause)

    @property
    def in_waiting(self) -> bool:
        """Checks data is waiting in the socket buffer."""
        data_in_socket, _, _ = select.select([self.socket], [], [], 0)
        return len(data_in_socket) != 0

    def read(self, amount: int) -> bytes:
        """Reads bytes, discards first 16 bytes (UDP Header)"""
        # With datagrams, the min amount to read is 16 (header) + 8 (data) = 24
        # But we have to set the buffer to the largest datagram we can receive
        buf_size = max(amount, _UDP_READ_BUFFER_SIZE)
        try:
            data = self.socket.recv(buf_size)
        except Exception as e:
            return b""
        if len(data) < _UDP_HEADER_BYTES:
            return b""
        return data[_UDP_HEADER_BYTES:]

    def read_until(self, stopword: bytes):
        """Pulls data from the connection until a set of characters is found.

        Args:
            stopword (bytes): the sequence of characters that indicate
                when to stop reading.

        Returns:
            A bytearray containing the data, including the trailing stop word.
            The buffer is empty or incomplete if timed out
        """
        buff = bytearray()
        lenstop = len(stopword)
        while buff[-lenstop:] != stopword:
            try:
                next = self.read(24)
                buff.extend(next)
            except Exception as e:
                break
            if len(next) == 0:
                logger.debug(
                    "read_until(): did not end with correct stop word (got %s)",
                    buff[-lenstop:],
                )
                break
        if len(buff) == 0:
            logger.debug("Receive timeout, no data returned")
        return buff

    def read_all(self) -> bytes:
        """Read all waiting bytes"""
        fifo = self._rx_fifo
        while True:
            try:
                data = self.read(_UDP_READ_BUFFER_SIZE)
                fifo.extend(data)
            except Exception as e:
                break
            if len(data) == 0:
                break
        self._rx_fifo = bytearray()
        return fifo

    def receive(self, length: int = -1, timeout: int = 100, raw: bool = False):
        """Receives data from the socket.

        Args:
            length (int): the number of bytes to receive
            timeout (int): the number of milliseconds to wait before giving up
            raw (bool): return bytes (True), or return a hex string (False)

        Returns:
            Hex string or bytes, depending on the `raw` flag, or None if
            no data was received in time.
        """
        return self.read_until(self.stop_word)

    def receive_all(self, timeout: int = 100, raw: bool = False):
        """Receives all waiting data from the socket.

        Args:
            timeout (int): the number of milliseconds to wait before giving up
            raw (bool): return bytes (True), or return a hex string (False)

        Returns:
            Hex string or bytes, depending on the `raw` flag, or None if
            no data was received in time.
        """
        return self.receive(length=self.in_waiting, timeout=timeout, raw=raw)

    def writeReg(self, regNum: int, value: int):
        """Sends a command to write a value to a register

        Args:
            regNum (int): the address of the register to write
            value (int): the value to write
        """
        command = self.write_addr + hex(regNum)[2:].zfill(2) + hex(value)[2:].zfill(4)
        self.send(command)

    def readReg(self, regNum: int, timeout: int = 1000) -> int:
        """Reads a register.

        Args:
            regNum (int): the address of the register to read from
            timeout (int): the number of milliseconds to wait before giving up

        Returns:
            The value held in the register, or None if an error occurred
        """
        cmd_id = self._send_readreg_cmd(regNum)

        # Read a single response from the socket
        while not self.in_waiting and timeout > 0:
            timeout -= 1
            time.sleep(0.001)

        if not self.in_waiting:
            logger.error("UDP.readReg(): Timed out, no data received")
            return None

        buff, _ = self.socket.recvfrom(self.response_length)
        buff = bytearray(buff)

        # Handle the data received
        answer = self.parse_answer(buff)
        if answer["cmd_id"] != cmd_id:
            logger.error(
                "UDP.readReg(): received command ID does not match the one sent"
            )
            return None

        return answer["value"]

    def _send_readreg_cmd(self, regNum) -> int:
        """Sends a command to read a register.

        Args:
            regNum (str, int): the register to read

        Returns:
            The command id used in the sent command
        """
        read_addr = int(self.read_addr, 16)
        if isinstance(regNum, str):
            regNum = int(regNum, 16)

        # Generate and send the command string (4 bytes)
        cmd_id = np.random.randint(0, 2**16)
        command = f"{read_addr:x}{regNum:02x}{cmd_id:04x}"

        self.send(command)

        return cmd_id
