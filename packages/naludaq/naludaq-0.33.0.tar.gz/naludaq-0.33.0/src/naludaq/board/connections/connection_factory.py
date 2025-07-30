"""Connection factory.

Creates and returns a connection of the specified type.
"""
from logging import getLogger

from ._MockUART import MockUART
from ._UART import UART
from .tcp import TCP
from .udp import UDP

LOGGER = getLogger(__name__)

# This list gets updated based on whether or not certain
# connection types are actually available
VALID_CONNECTION_TYPES = [
    "ftdi",
    "tcp",
    "udp",
    "uart",
    "ft60x",
    "none",
]
try:
    from ._FTDI import FTDI
except (ImportError, FileNotFoundError) as e:
    VALID_CONNECTION_TYPES.remove("ftdi")
    LOGGER.warning("FTDI import failed: %s", e)
try:
    from ._USB import USB3
except (ImportError, FileNotFoundError) as e:
    VALID_CONNECTION_TYPES.remove("ft60x")
    LOGGER.warning("D3XX import failed: %s", e)

FTDI_AVAILABLE = "ftdi" in VALID_CONNECTION_TYPES
USB3_AVAILABLE = "ft60x" in VALID_CONNECTION_TYPES


def get_connection(conn_info):
    """Setup a connection to the device and raise the connection flag.

    Takes a connection_info dictionary and sets the connection accordingly.

    Input:
        conn_info (dict):
            "type": (str) "none" "eth" "uart"
            "usb_port": (str) port name
            "speed": (int) baud rate or ethernet speed
            "ip_addr": (str) should be in XXX.XXX.XXX.XXX format
            "ip_port": (int) port number

    Raises:
        TypeError if the connection type is unknown.
        ConnectionError if connection can't be created.
    """
    conn_type = _get_connection_type_or_raise(conn_info)
    connection = None
    try:
        if conn_type == "tcp":
            connection = _set_tcp_connection(conn_info)
        elif conn_type == "udp":
            connection = _set_udp_connection(conn_info)
        elif conn_type == "uart":
            connection = _set_uart_connection(conn_info=conn_info)
        elif conn_type == "ftdi":
            connection = _set_ftdi_connection(conn_info=conn_info)
        elif conn_type == "ft60x":
            connection = _set_ft60x_connection(conn_info=conn_info)
    except (ConnectionError, Exception) as error_msg:
        raise ConnectionError(error_msg)

    return connection


def _set_uart_connection(conn_info):
    """Connect to the UART.

    Setup the connection to serial.
    sets self.connection to the UART connection.

    Input:
        serial_port (str): com-port(win) or device address(*nix)
        baud (int): Set communication baud rate.
    """
    baud = conn_info["speed"]
    connection = None
    LOGGER.info("connecting using %s, %s", conn_info, baud)

    try:
        if conn_info.get("mock", False):
            connection = MockUART(conn_info)
        else:
            connection = UART(conn_info)
    except ConnectionError:
        LOGGER.debug("Couldn't open UART.UART(%s, %s)", conn_info, baud)
        raise
    else:
        connection.open()
        connection.toggleLoopback(0)
    return connection


def _set_ftdi_connection(conn_info):
    """Connect using the FTDI driver.

    The FTDI connection uses device number rather than comport.
    Allowing connections to devices not enuemrated.

    """
    if not FTDI_AVAILABLE:
        raise ConnectionError("Can't use FTDI connections if driver is unavailable.")
    baud = conn_info["speed"]
    connection = None
    LOGGER.info("connecting using %s, %s", conn_info, baud)

    try:
        if conn_info.get("mock", False):
            connection = MockUART(conn_info)
        else:
            connection = FTDI(conn_info)
    except ConnectionError:
        LOGGER.debug("Couldn't open FTDI(%s, %s)", conn_info, baud)
        raise
    else:
        connection.open()
    return connection


def _set_ft60x_connection(conn_info):
    """Connect using the FTDI driver.

    The FTDI connection uses device number rather than comport.
    Allowing connections to devices not enuemrated.

    """
    if not USB3_AVAILABLE:
        raise ConnectionError("Can't use USB3 connections if driver is unavailable.")
    connection = None
    LOGGER.info("connecting using %s", conn_info)

    try:
        if conn_info.get("mock", False):
            raise ConnectionError("Mock connection is not available for USB3.")
        connection = USB3(conn_info)
    except ConnectionError:
        LOGGER.debug("Couldn't open USB3(%s)", conn_info)
        raise
    else:
        connection.open()
    return connection


def _set_tcp_connection(conn_info):
    """Connect to the UART.

    Setup the connection to serial.
    sets self.connection to the UART connection.

    Input:
        serial_port (str):
        baud (int): Set communication baud rate.

    """
    try:
        ip = conn_info["ip"]
        port = conn_info["port"]
        stop_word = conn_info.get("stop_word", b"\xFA\xCE")
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")

    connection = None
    try:
        connection = TCP(ip, port, stop_word)
        connection.open()
    except ConnectionError:
        raise
    return connection


def _set_udp_connection(conn_info):
    """Connect to over UDP socket.

    sets self.connection to the UDP connection.

    Args:
        conn_info (dict): containing the connection params for the UDP connection obj.

    Returns:
        An open UDP connection
    """
    try:
        conn_info["stop_word"]
    except KeyError as e:
        raise ValueError(f"Connection is missing required parameter 'stop_word'")

    connection = None
    try:
        connection = UDP(conn_info)
        connection.open()
    except ConnectionError:
        raise
    return connection


def _get_connection_type_or_raise(conn_info: dict):
    conn_type = conn_info.get("type", None)
    if conn_type is None:
        raise AttributeError('Connection info missing "type" key')
    if not isinstance(conn_type, str):
        raise TypeError("Connection type must be a string")
    conn_type = conn_type.lower()
    if conn_type not in VALID_CONNECTION_TYPES:
        raise TypeError(f"{conn_type} is not a recognized connection type.")
    return conn_type
