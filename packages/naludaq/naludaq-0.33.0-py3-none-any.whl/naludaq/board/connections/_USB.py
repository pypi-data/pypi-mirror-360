"""
Driver for talking over a FT60X interface interface

Should be interoperable with the linketh package


Marcus Luck - Nalu Scientific
email: marcus@naluscientific.com
January 2023
"""
import binascii
import ctypes
import logging
import platform
import time
from typing import Optional

from naludaq.helpers import validations

try:
    import ftd3xx as ftd
except (FileNotFoundError, OSError):
    raise FileNotFoundError("D3XX driver not installed")
except ImportError:
    raise ImportError("ftd3xx not installed. Please install package.")

if platform.system() == "Windows":
    import ftd3xx._ftd3xx_win32 as _ft
# elif platform.system() == "Linux":
#     import ftd3xx._ftd3xx_linux as _ft
else:
    raise ImportError(f"Support for USB 3 on {platform.system()} is unavailable")

import numpy as np

from naludaq.board.connections.base_serial import BaseConnection
from naludaq.helpers.exceptions import FTDIError
from naludaq.parsers.answer_parser import get_answer_parser

logger = logging.getLogger("naludaq.D3XX")
_WRITE_MESSAGE_NIBBLES = 8
_DEFAULT_READ_PIPE_ID = 0x82
_DEFAULT_WRITE_PIPE_ID = 0x02
_DEFAULT_CHUNK_SIZE = 4 * 1024  # 786_842


class USB3(BaseConnection):
    """FTDI is a communications class for talking to the boards.

    Uses the ftd2xx Python package, which requires d2xx drivers
    to be properly installed. For information about using d2xx:
    https://ftdichip.com/wp-content/uploads/2020/08/D2XX_Programmers_GuideFT_000071.pdf
    """

    def __init__(self, conn_info: dict):
        """Initializes the FTDI object, but does not open a connection.

        Args:
            conn_info (dict): the connection info dict. Required keys: 'speed', 'model',
                and 'serial_number'. 'stop_word' is preferred, and defaults
                to 0xCAFE if not present.

        Raises:
            ConnectionError if the connection info dict is missing the required keys.
        """
        super().__init__()
        self._conn: ftd.FTD3XX = None
        self._read_addr = "AD"
        self._write_addr = "AF"
        self._is_open = False

        self._chunk_size = _DEFAULT_CHUNK_SIZE
        self._read_pipe_id = _DEFAULT_READ_PIPE_ID
        self._write_pipe_id = _DEFAULT_WRITE_PIPE_ID
        self.tx_pause = 0.02
        self.bundle_mode = False

        self._speed = conn_info["speed"]
        self._model = conn_info["model"]
        self.stopword = conn_info.get("stop_word", b"\xca\xfe")  # b'\xfa\xce'
        self.new_firmware = conn_info.get("new_firmware", False)
        self.response_length = 4
        self.parse_answer = get_answer_parser()

        serial_number = conn_info.get("serial_number", None)
        if serial_number:
            logger.debug("using serial_number %s to connect", serial_number)
            self.serial_number = serial_number
        else:
            raise ConnectionError("FTDI connection requires the serial num or port num")

    def __del__(self):
        """Closes the connection if one is open."""
        self.close()

    @property
    def new_firmware(self):
        """Get/Set if the board uses a new firmware or not.

        If a new firmware is used, the register answers are different.
        """
        return self._new_firmware

    @property
    def in_waiting(self):
        return self._chunk_size

    @new_firmware.setter
    def new_firmware(self, value: bool):
        self._new_firmware = value
        self.response_length = 4
        if value is True:
            self.response_length = 8
        self.parse_answer = get_answer_parser(value)

    @property
    def type(self):
        return "ft60x"

    @property
    def is_open(self) -> bool:
        """Indicates whether the connection is open."""
        is_open = True
        try:
            self._conn.getChipConfiguration()
        except (AttributeError, ftd.DeviceError):
            is_open = False
        return is_open

    def open(self):
        """Open connection over the FTDI interface.

        Set board (device) number and baud before opening a connection, use:
            .serial_number = value
        """
        if self.is_open:
            logger.debug("USB3.open(): device already open")
            return

        serial_number = self.serial_number.encode("ascii")
        usb_connection = ftd.create(serial_number, _ft.FT_OPEN_BY_SERIAL_NUMBER)
        self._conn = usb_connection
        self._is_open = usb_connection is not None

        if usb_connection is None:
            raise ConnectionError("Failed to connect USB3")

    def close(self):
        """Close the serial port."""
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception as e:
                logger.debug("Failed to close connection due to: %s", e)
            self._conn = None
        self._is_open = False

    def send(self, data, pause: Optional[float] = None, bundle: Optional[bool] = None):
        """Converts the string to a series of bytes to send in the correct format

        Input:
            data (hex): A hex type string (interface needs 32 bits, so 8 hex chars minimum)
            pause (float): How logn to wait in between send.
            bundle (bool): If true, will send longer packages in one send, otherwise will send cmd by cmd.
        """
        if bundle is None:
            bundle = self.bundle_mode
        if pause is None:
            pause = self.tx_pause

        if len(data) % _WRITE_MESSAGE_NIBBLES != 0:
            logger.debug(
                "FTDI.send(): need multiples of 8 hex chars, you gave me %s", len(data)
            )
            logger.debug("command:%s", data)
            return

        logger.debug("Sending: %s in %s mode", data, "bundle" if bundle else "single")
        if (len(data) > _WRITE_MESSAGE_NIBBLES) and bundle is False:
            for i in range(0, len(data), _WRITE_MESSAGE_NIBBLES):
                self._send(data[i : i + _WRITE_MESSAGE_NIBBLES], pause)
        else:
            self._send(data, pause)

    def _send(self, data, pause):
        try:
            tosend = binascii.a2b_hex(data)
        except binascii.Error as e:
            logger.error(f"FTDI.send(): could not convert hex data: {e}")
            return
        try:
            bytes_written = self._conn.writePipe(
                self._write_pipe_id, tosend, len(tosend)
            )
        except AttributeError as error_msg:
            logger.error(
                "Can't send command to board, no connection available. %s", error_msg
            )
        if bytes_written == 0:
            raise ConnectionError("Failed to send data, no connection available")
        time.sleep(pause)

    def read_until(self, stopword: bytes) -> bytearray:
        """Pulls data from the connection until a set of characters is found.

        Args:
            stopword (bytes): the sequence of characters that indicate
                when to stop reading.

        Returns:
            A bytearray containing the data, including the trailing stop word.
            The buffer is empty or incomplete if timed out
        """
        lenstop = len(stopword)
        buff = bytearray()
        while True:
            value = None
            try:
                value = self.read(self._chunk_size)
            except Exception as e:
                logger.debug("Receiving data failed due to: %s", e)
            if value is None or len(value) == 0:
                logger.error("Failed to read data")
                break

            buff += value
            if buff[-lenstop:] == stopword:
                break

        logger.debug("Received: %s", buff.hex())

        return buff

    def receive(self):
        """Reads out an event or answer. Both end with a stopword.

        This will *NOT* work on boards where data and registers have different stopwords.
        """
        return self.read_until(self.stopword)

    def read(self, length: int = None) -> bytes:
        """Attempt to read data from the connection.

        Args:
            length (int, optional): maximum number of bytes to read.
                If not provided, the chunk size is assumed.

        Raises:
            FTDIError: If the operation failed.

        Returns:
            bytes: The data received. This may be less than the amount requested.
        """
        if length is None:
            length = self._chunk_size
        try:
            data = ctypes.c_buffer(length)
            rxlength = self._conn.readPipe(self._read_pipe_id, data, length)
            data = data[0:rxlength]
        except ftd.DeviceError as e:
            raise FTDIError(f"USB.read failed due to: {e}")
        if data == b"\xFA\xCE":
            return b""
        return data

    def read_all(self, attempts=10) -> bytearray:
        """Read all waiting bytes"""
        data = bytearray()

        attempt_count = 0
        while attempt_count < attempts:
            resp = self.read(self._chunk_size)
            if len(resp) == 0:
                attempt_count += 1
                continue
            data += resp
        return data

    def reset_input_buffer(self, iterations: int = 100):
        """Discards any data currently in the boards output buffer.

        This will empty both the computer input buffer and the hardware
        output buffer.

        However, this will only run 100 times at the most which is ~400kb.

        Args:
            iterations (int): number of times to read the buffer.
                A cap is necessary since the board may be sending data faster
                than it can be purged.
        """
        validations.validate_positive_int_or_raise(iterations)
        for _ in range(iterations):
            if len(self.read_all()) == 0:
                break
            time.sleep(0.001)

    def reset_output_buffer(self):
        """Not implemented for USB3."""

    def set_answer_parser(self, old=True):
        """Set's the answer parser"""
        self.parse_answer = get_answer_parser(old)

    def readReg(self, regNum, timeout=10000) -> int:
        """
        Reads out the register specified by the integer regNum
        Args:
            regNum (int): The registry number to read
            timeout (int): Amount of retries.
        Returns:
            Hex value of the serialread of two bytes.
        """
        # Send command
        self._send_readreg_cmd(regNum)

        # Wait for response
        buffer = self.receive()
        # Parse response
        answer = self.parse_answer(buffer)
        # Make sure responses are valid

        try:
            logger.debug(
                "FTDI.readReg(%s) success: %s %s %s",
                answer["read_reg"],
                answer["value"],
                hex(answer["value"]),
                "{0:b}".format(answer["value"]).zfill(16),
            )
        except Exception:
            pass

        return answer["value"]

    def _send_readreg_cmd(self, regNum):
        """Generates and sends a command to read a register.

        Args:
            regNum (str, int): address as int or hex str.
        """
        cmd_id = np.random.randint(0, 2**16)
        if isinstance(regNum, str):
            regNum = int(regNum, 16)
        read_addr = int(self._read_addr, 16)

        try:
            command = f"{read_addr:x}{regNum:02x}{cmd_id:04x}"
        except Exception as error_msg:
            logger.exception(f"send_readreg_cmd create cmd failed: {error_msg}")
        else:
            self.send(command)
