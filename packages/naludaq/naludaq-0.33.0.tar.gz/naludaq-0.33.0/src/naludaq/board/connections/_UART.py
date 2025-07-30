"""
Driver for talking over a UART interface

Should be interoperable with the linketh package


Ben Rotter - Nalu Scientific
email: ben@naluscientific.com
September 2018
"""
import logging
import time

import numpy as np
import serial
import serial.tools.list_ports

from naludaq.board.connections.base_serial import BaseSerialConnection
from naludaq.helpers import validations
from naludaq.parsers.answer_parser import get_answer_parser

logger = logging.getLogger("naludaq.UART")


class UART(BaseSerialConnection):
    """UART is a communications class for talking to the boards."""

    def __init__(self, conn_info):
        super().__init__()
        self._write_addr = 0xAF
        self._read_addr = 0xAD
        self._baud = conn_info["speed"]
        self._model = conn_info["model"]
        self._rxtx_timeout = 0.1  # s

        self.stopword = conn_info.get("stop_word", b"\xca\xfe")  # b'\xfa\xce'
        self.new_firmware = conn_info.get("new_firmware", False)
        self.response_length = 4
        self.parse_answer = get_answer_parser()

        serial_number = conn_info.get("serial_number", None)
        com_port = conn_info.get("usb_addr", None)

        if serial_number is not None:
            logger.debug("using serial_number %s to connect", serial_number)
            self.serial_number = serial_number
        elif com_port is not None:
            logger.debug("using usb_addr %s to connect", com_port)
            self.port = com_port
        else:
            raise ConnectionError(
                "Need either serial number or COM port to open connection"
            )

        self.stopword = conn_info["stop_word"]  # b'\xfa\xce'
        self.ser = None

    def __del__(self):
        self.close()

    @property
    def baud(self):
        """Get/Set baudrate.

        Must be a positive integer.
        Raises:
            ValueError
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
                self.ser.baudrate = value
            except Exception as e:
                logger.error("Failed to set baud rate: {e}")
                raise ConnectionError("Failed to set baud rate due to error: {e}")

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if not isinstance(value, str):
            raise TypeError("Port name must be a string.")
        ports = self.get_available_ports()
        logger.debug("available ports:%s", ports)

        if value not in ports:
            raise ValueError(f"{value} is not a valid port.")
        self._port = value

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        """
        Set a port given a part of a serial number
        """

        if not isinstance(value, str):
            raise TypeError("Serial Number must be a string.")

        ports = serial.tools.list_ports.comports()
        logger.debug("Connected Devices:")
        for port in ports:
            logger.debug("sn:%s, port:%s", port.serial_number, port.device)
            if port.serial_number is None:
                continue
            if value in port.serial_number:
                self._serial_number = port.serial_number
                self._port = port.device
                logger.debug("found port matching given SN with %s", value)
                return

        logger.error("did not find port matching SN")

    def get_available_ports(self):
        """Lists available serial ports.

        Returns:
            A list of available serial ports on the system. Empty if no ports are available.
        """
        return [comport.device for comport in serial.tools.list_ports.comports()]
    
    @property
    def com_port(self):
        """Get/set the COM port.
        Alias of UART.port to use the same naming convention as the backend.

        Raises:
            TypeError if set to a non-integer type.
            ValueError if set to a device that is not available.
            ConnectionError if set while the connection is open
        """
        return int(self.port.lstrip("COM"))
    
    @com_port.setter
    def com_port(self, value):
        if not isinstance(value, int):
            raise TypeError("COM port must be an integer")
        self.port = "COM{}".format(value)

    @property
    def type(self):
        return "uart"

    @property
    def is_open(self) -> bool:
        """Indicates whether the connection is open."""
        is_open = self.ser.is_open
        try:
            self.ser.in_waiting
        except:
            is_open = False
        return is_open

    def open(self):
        """Open connection over the UART interface.

        Set port and baud before opening a connection, use:
            .port(value)
            .baud(value)

        """
        if self.ser:
            if not self.ser.is_open:
                self.ser.open()

            return self.ser

        serial_connection = None
        try:
            serial_connection = serial.Serial(
                self.port, self._baud, timeout=self._rxtx_timeout
            )

        except ValueError as e_msg:
            logger.error("UART.open raise: %s", e_msg)
            serial_connection = None
        except serial.SerialException as error_msg:
            logger.debug(error_msg)
            serial_connection = None
        else:
            logger.info("Success!  Connected. %s", self.port)
        self.ser = serial_connection

    def close(self):
        """Close the serial port."""
        try:
            self.ser.close()
        except:
            pass

    def send(self, data):
        """Converts the string to a series of bytes to send in the correct format

        Input:
            data (hex): A hex type string (interface needs 32 bits, so 8 hex chars minimum)
            pause (float): How logn to wait in between send.
        """
        # logger.debug("Send(): data: %s", data)
        numchars = len(data)  # number of hex characters
        numcmds = numchars // 8  # 8 hex chars per command
        extra = numchars % 8

        if extra != 0:
            logger.debug(
                "UART.send(): need multiples of 8 hex chars, you gave me %s", numchars
            )
            logger.debug("command:%s", data)
            return

        logger.debug("UART.send(): %s", data)

        tosend = []
        for i in range(0, numchars // 2):
            tosend.append(int(data[i * 2] + data[i * 2 + 1], 16))

        try:
            self.ser.write(bytearray(tosend))
        except AttributeError as error_msg:
            logger.error("Can't send command to board, no connection available.")

    def toggleLoopback(self, state):
        """
        Turns the loopback on or off
        """
        command = "7009BAC" + str(int(state))
        self.send(command)
        try:
            self.ser.read(4)
        except:
            pass

    def read(self, num_bytes) -> bytes:
        return self.ser.read(num_bytes)

    def read_all(self) -> bytes:
        """Read all waiting bytes"""
        return self.ser.read_all()

    def reset_input_buffer(self):
        return self.ser.reset_input_buffer()

    def read_until(self, stopword):
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
            try:
                value = self.ser.read(1)
            except Exception as e:
                logger.debug("Receiving data failed due to: %s", e)
                break

            if value == b"":
                logger.debug("Receive timeout, no data returned")
                break

            buff += value
            if buff[-lenstop:] == stopword:
                break

        logger.debug("Received: %s", buff.hex())

        return buff

    @property
    def in_waiting(self):
        return self.ser.in_waiting

    def receive(self):
        """Reads out a package. Packages end with a stopword."""
        return self.read_until(self.stopword)

    @property
    def rtscts(self) -> bool:
        """Get/set whether RTS/CTS flow control is enabled."""
        return self.ser.rtscts

    @rtscts.setter
    def rtscts(self, value: bool):
        self.ser.rtscts = value

    def set_answer_parser(self, old=True):
        """Set's the answer parser"""
        self.parse_answer = get_answer_parser(old)

    def readReg(self, regNum, timeout=10000):
        if self._model in ["siread", "upac32", "upaci", "zdigitizer"]:
            return self.readReg_old(regNum=regNum, timeout=timeout)
        else:
            return self.readReg_new(regNum=regNum, timeout=timeout)

    def readReg_old(self, regNum, timeout=10000):

        command = f"{self._read_addr:02X}{regNum:02x}0000"
        self.send(command)
        # while self.ser.in_waiting < 4:
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
                raise Exception(
                    "readReg couldn't unpack the serial response."
                )  # TODO Change type

            if read_reg != regNum:
                logger.error(
                    "readReg didn't read expected register, wanted %s and got %s",
                    regNum,
                    read_reg,
                )
                return -1

        try:
            logger.debug("UART.readReg(%s) success: %s", read_reg, value)
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
        # response_length = self.response_length

        # Send command
        self._send_readreg_cmd(regNum)

        # Wait for response
        buffer = self.receive()  # self._wait_for_readreg_response(response_length)
        # Parse response
        answer = self.parse_answer(buffer)
        # Make sure responses are valid

        try:
            logger.debug(
                "UART.readReg(%s) success: %s %s %s",
                answer["read_reg"],
                answer["value"],
                hex(answer["value"]),
                "{0:b}".format(answer["value"]).zfill(16),
            )
        except Exception:
            pass

        return answer["value"]

    def _send_readreg_cmd(self, regNum):
        cmd_id = np.random.randint(0, 2**16)
        if isinstance(regNum, str):
            regNum = int(regNum, 16)

        try:
            command = f"{self._read_addr:02x}{regNum:02x}{cmd_id:04x}"
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
        while self.ser.in_waiting < response_length:
            timeout -= 1
            time.sleep(0.001)
            if timeout < 0:
                logger.error("No readReg response, timed out")
                break

        # Serial reader can cause alignment issues, read all will fix (although first read fails)
        buff = self.ser.read_all()

        # Buffer can be too large if data sent after timeout code above.
        buff = buff[-response_length:]

        return buff

    def writeReg(self, regNum, value):
        """Writes a value to a register (16bits max)

        Args:
            regNum (int): registry number
            value: value to write
        """

        command = self.write_addr + hex(regNum)[2:].zfill(2) + hex(value)[2:].zfill(4)
        logger.debug("WriteReg: %s", command)
        self.send(command)

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
        self.ser.read_all()
        logger.debug("Syncing board...")
        for i in range(0, 8):
            value = b""
            try:
                value = self.readReg(sync_regnum)
                if value == b"":
                    continue
            except:
                logger.debug("UART:resync(): sending single character")
                self.ser.write(bytearray(b"F"))

            # val = binascii.hexlify(value).lstrip(b'0x').lower()
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
            iterations (int): number of times to empty the buffer.
                A cap is necessary since the board may be sending data faster
                than it can be purged.
        """
        validations.validate_positive_int_or_raise(iterations)
        # Buffer can refill with junk after being emptied,
        # need to empty it multiple times
        for _ in range(iterations):
            if self.in_waiting == 0:
                break
            self.ser.reset_input_buffer()

            # Without waiting, buffer refills right after the loop breaks
            time.sleep(0.01)

    def reset_output_buffer(self):
        """Discards any data currently in the output buffer.

        Discarded data will not be received by the board.
        """
        self.ser.reset_output_buffer()
