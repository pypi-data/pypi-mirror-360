import logging
import socket
import time

from naludaq.board.connections._UART import UART

logger = logging.getLogger(__name__)

# Import packet size frmo mockboard to standardize packets
try:
    from mockboard.params import MAX_PACKET_SIZE
except:
    MAX_PACKET_SIZE = 1024


class MockUART(UART):
    def __init__(self, conn_info: dict):
        """Class for mocking a UART connection over a UDP socket.

        Args:
            conn_info (dict): the connection configuration
        """
        super(MockUART, self).__init__(conn_info)

        self._user_addr = (conn_info["ip"], conn_info["user_port"])
        self._board_addr = (conn_info["ip"], conn_info["board_port"])

        self.ser: _MockSerial = None

    @property
    def board_addr(self) -> tuple:
        """Address used to communicate with the mock board."""
        return self._board_addr

    @property
    def user_addr(self) -> tuple:
        """Address the naludaq-side socket binds to."""
        return self._user_addr

    def open(self) -> "_MockSerial":
        """Opens the connection."""
        if self.ser:
            if not self.ser.is_open:
                self.ser.open()
            return self.ser

        self.ser = _MockSerial(self._user_addr, self.board_addr)
        return self.ser

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value


class _MockSerial:
    def __init__(self, user_addr, board_addr):
        """Mock serial connection, implements the necessary
        functionality from pyserial but through sockets.

        Args:
            user_addr (tuple): user-side address the socket binds to.
            board_addr (tuple): address of the mock board
        """
        self.user_addr = user_addr
        self.board_addr = board_addr
        self.socket: socket.socket = None

        self.rtscts = False
        self.baudrate = 100_000
        self.input_buffer = bytearray()
        self.timeout = 0.01

        self.open()

    def __del__(self):
        self.close()

    def open(self):
        """Opens the connection."""
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setblocking(False)
            self.socket.bind(self.user_addr)

    def close(self):
        """Closes the connection."""
        try:
            self.socket.close()
        except:
            pass
        self.socket = None

    @property
    def is_open(self) -> bool:
        """Indicates whether the connection is open."""
        return self.socket is not None

    def read(self, size=1):
        """Reads at most the given number of bytes from the socket.
        May read less if the operation times out.

        Args:
            size (int): number of bytes to read.

        Returns:
            A bytearray of the data read.
        """
        start_time = time.perf_counter()
        while (
            len(self.input_buffer) < size
            and time.perf_counter() - start_time < self.timeout
        ):

            try:
                buff, _ = self.socket.recvfrom(MAX_PACKET_SIZE)
                self.input_buffer += buff
            except Exception as e:
                pass
        result = self.input_buffer[:size]
        self.input_buffer = self.input_buffer[size:]
        return result

    def read_all(self):
        """Reads all packets from the socket, until it is empty.

        Returns:
            result (bytearray): The input buffer of MockUART, populated
                with packets read from socket
        """
        while True:
            try:
                buff, _ = self.socket.recvfrom(MAX_PACKET_SIZE)
                self.input_buffer += buff
            except Exception as e:
                break

        result = self.input_buffer
        self.input_buffer = bytearray()
        return result

    def write(self, data: bytes):
        """Sends the data over the socket, to the destination port.

        Args:
            data (bytes): The bytes to send over socket
        """
        try:
            self.socket.sendto(data, self.board_addr)
        except:
            raise IOError("Could not send data over socket.")

    @property
    def in_waiting(self):
        """Reads waiting packets in the socket connection, and
        appends it to the input buffer. Returns the number
        of bytes in wait.

        Returns:
            length (int): Length of the input buffer byte array.
        """
        self.input_buffer = self.read_all()
        return len(self.input_buffer)

    def reset_input_buffer(self):
        """Empties out the packets waiting in socket, as well as
        the input buffer.
        """
        self.read_all()

    def reset_output_buffer(self):
        pass
