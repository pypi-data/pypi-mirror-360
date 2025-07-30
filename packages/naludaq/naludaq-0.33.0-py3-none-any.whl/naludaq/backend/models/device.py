import abc
from dataclasses import dataclass
from enum import Enum

from naludaq.backend.context import Context
from naludaq.backend.exceptions import DeviceError


class DeviceType(Enum):
    UDP = 0
    SERIAL = 1
    D2XX = 2
    D3XX = 3

    @staticmethod
    def from_string(type_name: str) -> "DeviceType":
        result = {
            "udp": DeviceType.UDP,
            "serial": DeviceType.SERIAL,
            "d2xx": DeviceType.D2XX,
            "d3xx": DeviceType.D3XX,
        }.get(type_name.lower(), None)
        if result is None:
            raise ValueError("Invalid device type")
        return result


class Device(abc.ABC):
    """Abstract wrapper for interacting with a device."""

    def __init__(self, context: Context, device_type: DeviceType):
        self._context = context
        self._type = device_type

    @property
    def context(self) -> Context:
        return self._context

    @property
    def is_open(self) -> bool:
        return self.is_valid

    @property
    def is_valid(self) -> bool:
        """Checks if this handle is usable"""
        return self._type == self._get_remote_type()

    @property
    def is_uart_based(self) -> bool:
        """Check if the connected device is UART-based (serial & D2XX).
        Will return `False` if there is no connection.
        """
        return hasattr(self, "baud_rate")

    @property
    def type(self) -> DeviceType:
        """Get the device type. This method does not check the backend."""
        return self._type

    @property
    def raw_connection_info(self) -> dict:
        """Get the raw connection info dict"""
        try:
            return self.raw_info["connection_info"]
        except KeyError:
            raise DeviceError("Device is not connected")

    @property
    def raw_info(self) -> dict:
        """Get the raw connection information dict"""
        return self._context.client.get_json("/connection/info")

    @property
    @abc.abstractmethod
    def info(self) -> dict:
        """Get connection info dict"""

    def clear_buffers(self):
        """Clear I/O buffers on the device."""
        self._context.client.put(
            "/connection/clear",
        )

    def _get_remote_type(self) -> DeviceType:
        """Get the type of device connected to the remote"""
        try:
            type_name = self.raw_info["connection_type"]
        except KeyError:
            raise DeviceError("Device is not connected")
        return DeviceType.from_string(type_name)

    def __repr__(self) -> str:
        """Generate string representation"""
        info = self.raw_connection_info
        info["valid"] = self.is_valid
        info = ", ".join(f"{k}={repr(v)}" for k, v in info.items())
        return f"{type(self).__name__}<{info}>"


class UdpDevice(Device):
    """Wrapper for working with a UDP device connected to the backend."""

    def __init__(self, context: Context):
        super().__init__(context, DeviceType.UDP)

    @property
    def board_ip(self) -> str:
        """Get the board IP address"""
        return self.raw_connection_info["board_ip"]

    @property
    def board_port(self) -> int:
        """Get the board port number"""
        return self.raw_connection_info["board_port"]

    @property
    def receiver_ip(self) -> str:
        """Get the receiver IP address"""
        return self.raw_connection_info["receiver_ip"]

    @property
    def receiver_port(self) -> int:
        """Get the receiver port number"""
        return self.raw_connection_info["receiver_port"]

    @property
    def info(self) -> dict:
        """Get connection info dict"""
        return {
            "type": "udp",
            "board_addr": (self.board_ip, self.board_port),
            "receiver_addr": (self.receiver_ip, self.receiver_port),
        }


class SerialDevice(Device):
    """Wrapper for working with a serial device connected to the backend."""

    def __init__(self, context: Context):
        super().__init__(context, DeviceType.SERIAL)

    @property
    def port(self) -> str:
        """Get the port the device is connected to"""
        return self.raw_connection_info["port"]

    @property
    def baud_rate(self) -> int:
        """Get/set the port baud rate"""
        return self.raw_connection_info["baud_rate"]

    @baud_rate.setter
    def baud_rate(self, value: int):
        self._context.client.put("/connection/serial", params={"baud_rate": value})
        if self.baud_rate != value:
            raise DeviceError("Failed to set baud rate")

    @property
    def rts_cts(self) -> bool:
        """Get/set whether RTS/CTS flow control is enabled."""
        return self.raw_connection_info["rts_cts"]

    @rts_cts.setter
    def rts_cts(self, enabled: bool):
        self._context.client.put("/connection/serial", params={"rts_cts": int(enabled)})
        if self.rts_cts != enabled:
            raise DeviceError("Failed to set flow control")

    @property
    def info(self) -> dict:
        """Get connection info dict"""
        return {
            "type": "serial",
            "port": self.port,
            "baud_rate": self.baud_rate,
        }


class D2xxDevice(Device):
    """Wrapper for working with a D2XX device connected to the backend."""

    def __init__(self, context: Context):
        super().__init__(context, DeviceType.D2XX)

    @property
    def serial_number(self) -> str:
        """Get the device serial number"""
        return self.raw_connection_info["serial_number"]

    @property
    def com_port(self) -> "str | None":
        """Get the device COM port.
        If there is no corresponding COM port (e.g. Linux), `None` is returned.
        """
        try:
            return self.raw_connection_info["com_port"]
        except KeyError:
            return None

    @property
    def baud_rate(self) -> int:
        """Get/set the device baud rate"""
        return self.raw_connection_info["baud_rate"]

    @baud_rate.setter
    def baud_rate(self, value: int):
        self._context.client.put("/connection/d2xx", params={"baud_rate": value})
        if self.baud_rate != value:
            raise DeviceError("Failed to set baud rate")

    @property
    def rts_cts(self) -> bool:
        """Get/set whether RTS/CTS flow control is enabled."""
        return self.raw_connection_info["rts_cts"]

    @rts_cts.setter
    def rts_cts(self, enabled: bool):
        self._context.client.put("/connection/d2xx", params={"rts_cts": int(enabled)})
        if self.rts_cts != enabled:
            raise DeviceError("Failed to set flow control")

    @property
    def info(self) -> dict:
        """Get connection info dict"""
        return {
            "type": "d2xx",
            "serial_number": self.serial_number,
            "baud_rate": self.baud_rate,
        }


class D3xxDevice(Device):
    """Wrapper for working with a D3XX device connected to the backend."""

    def __init__(self, context: Context):
        super().__init__(context, DeviceType.D3XX)

    @property
    def serial_number(self) -> str:
        """Get the device serial number"""
        return self.raw_connection_info["serial_number"]

    @property
    def description(self) -> str:
        """Get the device description"""
        return self.raw_connection_info["description"]

    @property
    def info(self) -> dict:
        """Get connection info dict"""
        return {
            "type": "d3xx",
            "serial_number": self.serial_number,
            "description": self.description,
        }


@dataclass
class AvailableSerialDevice:
    """Represents a serial device available to the backend"""

    port: str


@dataclass
class AvailableD2xxDevice:
    """Represents a D2XX device available to the backend"""

    serial_number: str
    com_port: "str | None"
    index: int
    description: str


@dataclass
class AvailableD3xxDevice:
    """Represents a D3XX device available to the backend"""

    serial_number: str
    description: str
