import binascii
import logging
import socket

from .base_ethernet import EthernetBaseConnection

logger = logging.getLogger("naludaq.TCP")
_MAX_BUFF_SIZE = 65536


class TCP(EthernetBaseConnection):
    def __init__(self, ip: str, port: int, stop_word: bytes):
        super().__init__()
        self._timeout = 0.01  # FIXME: hardcoded for TRBHM experiment
        self._stop_word = stop_word
        self._address = (ip, port)
        self._socket: socket.socket = None
        self._rx_fifo = bytearray()

    def __del__(self):
        """Closes the connection if one is open."""
        self.close()

    @property
    def address(self) -> tuple[str, int]:
        return self._address

    @property
    def in_waiting(self) -> int:
        """Gets the number of bytes available to read."""
        self._rx_fifo = self.read_all()
        return len(self._rx_fifo)
    
    @property
    def type(self):
        return "tcp"
    
    @property
    def board_ip(self):
        """Gets the IP address of the board. 
        Alias of TCP.address[0] to use the same naming convention as backend.
        """
        return self.address[0]
    
    @property
    def board_port(self):
        """Gets the IP port of the board. 
        Alias of TCP.address[1] to use the same naming convention as backend.
        """
        return self.address[1]

    @property
    def is_open(self) -> bool:
        """Indicates whether the connection is open."""
        is_open = False
        if self._socket is not None:
            is_open = (
                self._socket.fileno() != -1
            )  # fileno() == -1 if connection dropped
        return is_open

    def open(self):
        if self.is_open:
            logger.debug("TCP.open(): connection already established")
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(True)
        sock.settimeout(self._timeout)
        try:
            sock.connect(self._address)
        except OSError as e:
            sock.close()
            raise ConnectionError("Failed to connect") from e
        self._socket = sock

    def close(self):
        """Close the connection."""
        if self._socket is not None:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None

    def send(self, data):
        """Converts the string to a series of bytes to send in the correct format

        Input:
            data (hex): A hex type string (interface needs 32 bits, so 8 hex chars minimum)
            pause (float): How logn to wait in between send.
        """
        if len(data) % 8 != 0:
            logger.debug(
                "TCP.send(): need multiples of 8 hex chars, you gave me %s", len(data)
            )
            logger.debug("command:%s", data)
            return

        try:
            tosend = binascii.a2b_hex(data)
        except binascii.Error as e:
            raise ValueError("")

        logger.debug("Sending: %s", data)
        try:
            self._socket.send(tosend)
        except Exception as e:
            logger.error("Could not send data to board: %s", e)

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
                next = self.read(1)
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

    def receive(self):
        """Reads out an event or answer. Both end with a stopword.

        This will *NOT* work on boards where data and registers have different stopwords.
        """
        return self.read_until(self._stop_word)

    def read(self, amount: int) -> bytes:
        """Read bytes"""
        fifo = self._rx_fifo
        while len(fifo) < amount:
            try:
                data = self._socket.recv(amount - len(fifo))
                fifo.extend(data)
            except Exception as e:
                break
            if len(data) == 0:
                break
        self._rx_fifo = fifo[amount:]
        return fifo[:amount]

    def read_all(self) -> bytes:
        """Read all waiting bytes"""
        fifo = self._rx_fifo
        while True:
            try:
                data = self._socket.recv(_MAX_BUFF_SIZE)
                fifo.extend(data)
            except Exception as e:
                break
            if len(data) == 0:
                break
        self._rx_fifo = bytearray()
        return fifo

    def reset_input_buffer(self):
        """Discards any data currently in the input buffer."""
        self.read_all()

    def reset_output_buffer(self):
        """Does nothing."""
