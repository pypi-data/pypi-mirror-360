"""
Driver for talking over a FTDI interface

Should be interoperable with the linketh package


Marcus Luck - Nalu Scientific
email: marcus@naluscientific.com
January 2022
"""
import binascii
import logging
import time
from typing import Optional

try:
    import ftd2xx as ftd
    import ftd2xx.defines as ftd_defines
except (FileNotFoundError, OSError):
    raise FileNotFoundError("FTDI driver not installed")
except ImportError:
    raise ImportError("ftd2xx not installed. Please install package.")
import numpy as np

from naludaq.board.connections.base_serial import BaseSerialConnection
from naludaq.helpers import validations
from naludaq.helpers.exceptions import FTDIError
from naludaq.parsers.answer_parser import get_answer_parser
from naludaq.tools.ftdi import index_from_comport, index_from_serial, list_ftdi_devices

logger = logging.getLogger("naludaq.FTDI")

_WRITE_MESSAGE_NIBBLES = 8


class FTDI(BaseSerialConnection):
    """FTDI is a communications class for talking to the boards.

    Uses the ftd2xx Python package, which requires d2xx drivers
    to be properly installed. For information about using d2xx:
    https://ftdichip.com/wp-content/uploads/2020/08/D2XX_Programmers_GuideFT_000071.pdf
    """

    def __init__(self, conn_info: dict):
        """Initializes the FTDI object, but does not open a connection.

        Args:
            conn_info (dict): the connection info dict. Required keys: 'speed', 'model',
                and one of 'serial_number' or 'usb_addr'. 'stop_word' is preferred, and defaults
                to 0xCAFE if not present.

        Raises:
            ConnectionError if the connection info dict is missing the required keys.
        """
        super().__init__()
        self.ser: ftd.FTD2XX = None
        self._read_addr = "AD"
        self._write_addr = "AF"

        self._is_open = False
        self.board_num: int = None
        self._serial_number: str = None
        self._dev_word_len = ftd_defines.BITS_8
        self._dev_stop_bits = ftd_defines.STOP_BITS_1
        self._dev_parity = ftd_defines.PARITY_NONE
        self._rx_timeout = 100  # ms
        self._tx_timeout = 100  # ms
        self._rtscts = False
        self.tx_pause = 0.0
        self.bundle_mode = False

        self._baud = conn_info["speed"]
        self._model = conn_info["model"]
        self.stopword = conn_info.get("stop_word", b"\xca\xfe")  # b'\xfa\xce'
        self.new_firmware = conn_info.get("new_firmware", False)
        self.response_length = 4
        self.parse_answer = get_answer_parser()

        serial_number = conn_info.get("serial_number", None)
        board_num = conn_info.get("board_number", None)
        com_port = conn_info.get("usb_addr", None)

        if serial_number:
            logger.debug("using serial_number %s to connect", serial_number)
            self.serial_number = conn_info["serial_number"]
        elif board_num is not None:
            self.port = conn_info["board_number"]
        elif com_port is not None:
            logger.debug("using usb_addr %s to connect", conn_info["usb_addr"])
            try:
                index = index_from_comport(conn_info["usb_addr"])
            except ConnectionError:
                raise
            self._com_port = com_port
            self.port = index
        else:
            raise ConnectionError("FTDI connection requires the serial num or port num")

    def __del__(self):
        """Closes the connection if one is open."""
        self.close()

    @property
    def baud(self):
        """Get/Set baudrate.

        Must be a positive integer.

        Raises:
            ValueError if set to a value which is not an integer or is non-positive.
        """
        return self._baud

    @baud.setter
    def baud(self, value):
        if isinstance(value, int) and value >= 0:
            self._baud = value
        else:
            raise ValueError("Baudrate must be a positive integer.")
        if self.ser:
            try:
                self.ser.setBaudRate(value)
            except ftd.DeviceError as e:
                logger.error("Failed to set baud rate: {e}")
                raise ConnectionError("Failed to set baud rate")

    @property
    def port(self):
        """Get/set the port. For an FTDI device, the port is the device index).

        Raises:
            TypeError if set to a non-integer type.
            ValueError if set to a device that is not available.
            ConnectionError if set while the connection is open
        """
        return self._port

    @port.setter
    def port(self, value):
        if self._is_open:
            raise ConnectionError("Connection cannot be changed while open.")
        elif not isinstance(value, int):
            raise TypeError("Port number must be a integer.")
        ports = self.get_available_ports()
        logger.debug("available ports:%s", ports)

        if value not in ports:
            raise ValueError(f"{value} is not a valid port.")
        self._port = value

    @property
    def serial_number(self) -> str:
        """Get/set the serial number.

        Sets the device index (port), given part of a serial number.

        Raises:
            TypeError if set to a non-string type.
            ConnectionError if set while the connection is open
        """
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value: str):
        if self._is_open:
            logger.error("did not find port matching SN")
            raise ConnectionError("Connection cannot be changed while open.")
        elif not isinstance(value, str):
            raise TypeError("Serial Number must be a string.")

        try:
            index = index_from_serial(value)
        except FTDIError:
            raise ConnectionError(
                "Could not find a device with a matching serial number."
            )
        logger.debug("found port matching given SN with %s", value)

        self._port = index
        self._serial_number = ftd.getDeviceInfoDetail(index)["serial"].decode()

    @property
    def new_firmware(self):
        """Get/Set if the board uses a new firmware or not.

        If a new firmware is used, the register answers are different.
        """
        return self._new_firmware

    @new_firmware.setter
    def new_firmware(self, value: bool):
        self._new_firmware = value
        self.response_length = 4
        if value is True:
            self.response_length = 8
        self.parse_answer = get_answer_parser(value)

    @property
    def in_waiting(self) -> int:
        """Gets the number of bytes waiting in the input buffer."""
        return self.ser.getQueueStatus()

    def get_available_ports(self):
        """Lists available serial ports.

        Returns:
            A list of available serial ports on the system. Empty if no ports are available.
        """
        return [v["index"] for k, v in list_ftdi_devices().items()]
    
    @property
    def com_port(self):
        """Get/set the COM port. This also sets the index to the appropriate value.

        Raises:
            TypeError if set to a non-integer type.
            ValueError if set to a device that is not available.
            ConnectionError if set while the connection is open
        """
        return self._com_port
    
    @com_port.setter
    def com_port(self, value):
        self._com_port = value
        self.port = index_from_comport(value)
    
    @property
    def type(self):
        return "ftdi"

    @property
    def is_open(self) -> bool:
        """Indicates whether the connection is open."""
        # The `_is_open` attribute is a good start, but is not foolproof (e.g. if device unplugged)
        is_open = self._is_open
        if is_open:
            try:
                _ = self.ser.getQueueStatus()
            except:
                is_open = False
        return is_open

    def open(self):
        """Open connection over the FTDI interface.

        Set board (device) number and baud before opening a connection, use:
            .board_number = value
            .port = value
        """
        serial_connection = self.ser

        board_num = self.port
        try:
            if self.ser:
                if not self._is_open:
                    serial_connection = ftd.open(board_num)
                logger.debug("FTDI.open(): device already open")
            else:
                serial_connection = ftd.open(board_num)
        except ValueError as e_msg:
            logger.error("FTDI.open raise: %s", e_msg)
            serial_connection = None
        except Exception as error_msg:
            logger.debug(error_msg)
            serial_connection = None
        else:
            logger.info("Success!  Connected. %s", board_num)
            try:
                serial_connection.setTimeouts(
                    read=self._rx_timeout, write=self._tx_timeout
                )
                serial_connection.setDataCharacteristics(
                    self._dev_word_len,
                    self._dev_stop_bits,
                    self._dev_parity,
                )
                serial_connection.setBaudRate(self.baud)
                serial_connection.setFlowControl(self._rtscts)
            except ftd.DeviceError as e:
                logger.error(f"Failed to configure connection: {e}")
            self._is_open = True
        self.ser = serial_connection

    def close(self):
        """Close the serial port."""
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception as e:
                logger.debug("Failed to close connection due to: %s", e)
            self.ser = None
        self._is_open = False

    def send(self, data, pause: Optional[float] = None, bundle: Optional[bool] = None):
        """Converts the string to a series of bytes to send in the correct format

        Input:
            data (hex): A hex type string (interface needs 32 bits, so 8 hex chars minimum)
            pause (float): How logn to wait in between send.
        """
        if bundle is None:
            bundle = self.bundle_mode
        if pause is None:
            pause = self.tx_pause

        if len(data) % 8 != 0:
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
            self.ser.write(tosend)
        except AttributeError as error_msg:
            logger.error("Can't send command to board, no connection available.")
        time.sleep(pause)

    def read_until(self, stopword: bytes):
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
                value = self.read(1)
            except Exception as e:
                logger.debug("Receiving data failed due to: %s", e)
            if value == b"":
                logger.debug("Receive timeout, no data returned")
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

    def read(self, amount):
        """Read bytes"""
        try:
            data = self.ser.read(amount)
        except ftd.ftd2xx.DeviceError as e:
            raise FTDIError(f"FTDI.read failed due to: {e}")
        return data

    def read_all(self):
        """Read all waiting bytes"""
        return self.ser.read(self.ser.getQueueStatus())

    def resync(self, sync_int, sync_addr) -> bool:
        """Resync the board if the input buffer is half full.

        Sometimes you go out of sync, and you need to send single chars till it works
        If the baud speed is set different you can end up with the boards input buffer being partially filled.
        Thus it waits for more characters, try send characters until it accepts an 8 char command again.

        Args:
            sync_int(int): value expected when synced.

        Returns:
            True if board is synced, False if syncing failed.
        """
        try:
            sync_regnum = int(sync_addr)
        except TypeError:
            sync_regnum = int(sync_addr, 16)
        self.reset_input_buffer()
        logger.debug("Syncing board...")
        for i in range(0, 8):
            value = b""
            try:
                value = self.readReg(sync_regnum)
                if value == b"":
                    continue
            except:
                logger.debug("FTDI:resync(): sending single character")
                self.ser.write(bytes(b"F"))

            if value == sync_int:
                logger.debug("synced, was off %s chars", i)
                return True
            else:
                continue

        logger.debug("Couldn't sync")
        return False

    def reset_input_buffer(self, iterations: int = 100):
        """Discards any data currently in the boards output buffer.

        This will empty both the computer input buffer and the hardware
        output buffer.

        However, this will only run 100 times at the most which is ~400kb.

        Args:
            iterations (int): maximum number of times to purge the buffer.
                A cap is necessary since the board may be sending data faster
                than it can be purged.
        """
        validations.validate_positive_int_or_raise(iterations)
        for _ in range(iterations):
            if self.in_waiting == 0:
                break
            self.ser.purge(ftd_defines.PURGE_RX)
            time.sleep(0.001)

    def reset_output_buffer(self):
        """Discards any data currently in the output buffer.

        Discarded data will not be received by the board.
        """
        self.ser.purge(ftd_defines.PURGE_TX)

    @property
    def rtscts(self) -> bool:
        """Get/set whether RTS/CTS flow control is enabled."""
        return self._rtscts == ftd_defines.FLOW_RTS_CTS

    @rtscts.setter
    def rtscts(self, value: bool):
        """Enable or disable RTS/CTS.

        Args:
            value (bool): whether to enable.
        """
        if value:
            self._rtscts = ftd_defines.FLOW_RTS_CTS
        else:
            self._rtscts = ftd_defines.FLOW_NONE
        self.ser.setFlowControl(self._rtscts)

    def set_answer_parser(self, old=True):
        """Set's the answer parser"""
        self.parse_answer = get_answer_parser(old)

    def readReg(self, regNum, timeout=10000) -> int:
        """Attempts to read a register from the board.

        Args:
            regNum (int, str): register address
            timeout (int): number of tries

        Returns:
            The register value.

        Raises:
            ValueError if the response is improperly formatted.
        """
        if self._model in ["siread", "upac32", "upaci", "zdigitizer"]:
            return self.readReg_old(regNum=regNum, timeout=timeout)
        else:
            return self.readReg_new(regNum=regNum, timeout=timeout)

    def readReg_old(self, regNum, timeout=10000):
        """readReg implementation for old firmware"""
        command = f"{self._read_addr}{regNum:02x}0000"
        self.send(command)
        # while self.in_waiting < 4:
        #     timeout -= 1
        #     if timeout < 0:
        #         logger.error("No response, timed out")
        #         return -1
        buff = self.receive()
        logger.debug("readReg() Buff: %s, type: %s", buff, type(buff))
        # struct.unpack(): 'H' is for unsigned short,
        # > is because the stat fifo returns things big-endian for who knows why
        value = 0
        if len(buff) == 4:
            try:
                header = int.from_bytes(buff[0:2], byteorder="big", signed=False)
                read_reg = header & 255  # only 8 lsb
                value = int.from_bytes(buff[2:4], byteorder="big", signed=False)
            except Exception:
                logger.error("couldn't unpack output from register: %s", regNum)
                raise ValueError("readReg couldn't unpack the serial response.")

            if read_reg != regNum:
                logger.error(
                    "readReg didn't read expected register, wanted %s and got %s",
                    regNum,
                    read_reg,
                )
                return -1
        else:
            answer = self.parse_answer(buff)
            value = answer["value"]
        try:
            logger.debug("FTDI.readReg(%s) success: %s", read_reg, value)
        except Exception:
            pass

        return value

    def readReg_new(self, regNum, timeout=10000):
        """
        Reads out the register specified by the integer regNum
        Args:
            regNum (int): The registry number to read
            timeout (int): Amount of retries.
        Returns:
            Hex value of the serialread of two bytes.
        """
        self.response_length

        # Send command
        self._send_readreg_cmd(regNum)

        # Wait for response
        buffer = self.receive()  # self._wait_for_readreg_response(response_length)
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

    def _wait_for_readreg_response(self, response_length, timeout: int = 300):
        """Polls the input buffer until there is a valid repsonse.

        Args:
            response_length: number of bytes in response (eg. 4 or 8)
            timeout (int): number of miliseconds before timing out.

        Returns:
            bytes returned.
        """
        buff = b""
        while self.in_waiting < response_length:
            timeout -= 1
            time.sleep(0.001)
            if timeout < 0:
                logger.error("No readReg response, timed out")
                break

        buff = self.read_all()

        return buff


def get_handle(dev_id) -> int:
    """Gets the handle associated with a given device.

    Args:
        dev_id (int): the device index

    Returns:
        The handle as an int
    """
    return ftd.getDeviceInfoDetail(dev_id)["handle"]


def open_device_handle(handle: int):
    """Opens a new FTD2XX object using the given handle

    Args:
        handle (int): the device handle

    Returns:
        The FTD2XX object.
    """
    return ftd.FTD2XX(handle)


def close_all():
    """Closes all FTDI connections opened from this process."""
    for i in range(ftd.createDeviceInfoList()):
        h = get_handle(i)
        try:
            d = open_device_handle(h)
        except ftd.DeviceError:
            pass
        else:
            d.close()
