import time
from http import HTTPStatus

from naludaq.backend.client import HttpClient
from naludaq.backend.exceptions import DeviceError, HttpError
from naludaq.backend.managers.base import Manager
from naludaq.backend.models.device import (
    AvailableD2xxDevice,
    AvailableD3xxDevice,
    AvailableSerialDevice,
    D2xxDevice,
    D3xxDevice,
    Device,
    DeviceType,
    SerialDevice,
    UdpDevice,
)


class ConnectionManager(Manager):
    def __init__(self, board):
        """Utility for controlling the board connection on the backend.

        Args:
            context (Context): context used to communicate with the backend.
        """
        super().__init__(board)

    @property
    def is_connected(self) -> bool:
        return self.device is not None

    @property
    def is_uart_based(self) -> bool:
        """Check if the connected device is UART-based (serial & D2XX).
        Will return `False` if there is no connection.
        """
        return hasattr(self.device, "baud_rate")

    @property
    def device(self) -> "Device | None":
        """Get a wrapper which can be used to configure the device connected to the backend.
        If no device is connected, `None` is returned.
        """
        try:
            type_name = self.context.client.get_json("/connection/info").get(
                "connection_type", None
            )
        except HttpError as e:
            if e.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                raise DeviceError("Failed to retrieve device information")

        device_type = None
        if type_name is not None:
            device_type = DeviceType.from_string(type_name)
        if device_type == DeviceType.UDP:
            return UdpDevice(self.context)
        if device_type == DeviceType.SERIAL:
            return SerialDevice(self.context)
        if device_type == DeviceType.D2XX:
            return D2xxDevice(self.context)
        if device_type == DeviceType.D3XX:
            return D3xxDevice(self.context)
        return None

    def connect_udp(
        self,
        board_addr: tuple[str, int],
        receiver_addr: tuple[str, int],
        attempts: int = 5,
    ) -> UdpDevice:
        """Connect to the board through the backend using UDP.

        Any existing connections will be dropped prior to attempting to
        establish the new connection.

        Args:
            board_addr (tuple[str, int]): the board socket address
            receiver_addr (tuple[str, int]): the receiver socket address
            attempts (int): number of times to attempt connecting.

        Returns:
            UdpDevice: a handle to the device
        """
        board_addr = ":".join(map(str, board_addr))
        receiver_addr = ":".join(map(str, receiver_addr))
        arguments = {"board": board_addr, "receiver": receiver_addr}
        self._connect_with_attempts("udp", arguments, attempts)
        return UdpDevice(self.context)

    def connect_serial(
        self, port: str, baud_rate: int, attempts: int = 5
    ) -> SerialDevice:
        """Connect to the board through the backend using a serial port.

        Any existing connections will be dropped prior to attempting to
        establish the new connection.

        Args:
            port (str): COM port (Windows) or device file (Linux).
            baud_rate (int): serial connection baud rate.
            attempts (int): number of times to attempt connecting.
                Serial devices can randomly fail to open, so avoid
                setting this value too low.

        Returns:
            SerialDevice: a handle to the device
        """
        arguments = {"port": port, "baud_rate": baud_rate}
        self._connect_with_attempts("serial", arguments, attempts)
        return SerialDevice(self.context)

    def connect_d2xx(
        self, serial_number: str, baud_rate: int, attempts: int = 5
    ) -> D2xxDevice:
        """Connect to the board through the backend using D2XX.

        Any existing connections will be dropped prior to attempting to
        establish the new connection.

        Args:
            serial_number (str): D2XX device serial number.
            baud_rate (int): D2XX connection baud rate.
            attempts (int): number of times to attempt connecting.
                D2XX devices can randomly fail to open, so avoid
                setting this value too low.

        Returns:
            D2xxDevice: a handle to the device
        """
        arguments = {"serial_number": serial_number, "baud_rate": baud_rate}
        self._connect_with_attempts("d2xx", arguments, attempts)
        return D2xxDevice(self.context)

    def connect_d3xx(self, serial_number: str, attempts: int = 5) -> D2xxDevice:
        """Connect to the board through the backend using D3XX.

        Any existing connections will be dropped prior to attempting to
        establish the new connection.

        Args:
            serial_number (str): D3XX device serial number.
            attempts (int): number of times to attempt connecting.
                D3XX devices can randomly fail to open, so avoid
                setting this value too low.

        Returns:
            D3xxDevice: a handle to the device
        """
        arguments = {
            "serial_number": serial_number,
            "read_timeout_ms": 0,
            "write_timeout_ms": 0,
        }
        self._connect_with_attempts("d3xx", arguments, attempts)
        return D3xxDevice(self.context)

    def connect_from_info(self, info: dict) -> Device:
        """Connect to a device using an info dict.

        Args:
            info (dict): the info dict. Must contain "type" field and
                required arguments.

        Returns:
            Device: the connected device

        Raises:
            ValueError: if the info dict is invalid
        """
        type_name = info["type"].lower()
        if type_name == "udp":
            return self.connect_udp(info["board_addr"], info["receiver_addr"])
        if type_name == "serial":
            return self.connect_serial(info["port"], info["baud_rate"])
        if type_name == "d2xx":
            return self.connect_d2xx(info["serial_number"], info["baud_rate"])
        if type_name == "d3xx":
            return self.connect_d3xx(info["serial_number"])
        raise ValueError("Invalid connection info")

    def list_devices(
        self,
    ) -> "list[AvailableSerialDevice | AvailableD2xxDevice | AvailableD3xxDevice]":
        """Get a list of devices which are currently available to the backend.

        Returns:
            list[SerialDevice | D2xxDevice | D3xxDevice]: the list of devices.
        """
        return list_devices(self.context.client.address)

    def disconnect(self):
        """Attempts to drop any board connection the backend currently holds."""
        self.context.client.put("/connection/disconnect")

    def _connect_with_attempts(self, type_name: str, params: dict, attempts: int):
        """Open a device on the backend. Any existing connections will be dropped.

        Runs several attempts. This is mainly important for serial/D2XX, which
        can randomly fail to open for some reason.

        Args:
            type_name (str): connection type name (used for route).
            params (dict): connection arguments
            attempts (int): number of attempts.

        Raises:
            HttpError: if the device could not be opened.
        """
        ROUTE = f"/connection/{type_name}"
        for _ in range(attempts):
            self.disconnect()
            try:
                self.context.client.put(ROUTE, params=params)
            except HttpError:
                pass
            else:
                break
            time.sleep(0.1)
        else:
            raise DeviceError("Failed to connect to board")


def list_devices(
    backend_addr: tuple[str, int]
) -> "list[AvailableSerialDevice | AvailableD2xxDevice]":
    """Get a list of devices which are currently available to the backend.

    Returns:
        list[SerialDevice | D2xxDevice]: the list of devices.
    """
    client = HttpClient(backend_addr)
    response = client.get_json("/connection/list")
    result = []
    for device in response["devices"]:
        # UDP cannot be enumerated, so is not included in the response
        if "Serial" in device:
            result.append(AvailableSerialDevice(device["Serial"]["port"]))
        if "D2xx" in device:
            result.append(
                AvailableD2xxDevice(
                    serial_number=device["D2xx"]["serial_number"],
                    com_port=device["D2xx"].get("com_port", None),
                    index=device["D2xx"]["index"],
                    description=device["D2xx"]["description"],
                )
            )
        if "D3xx" in device:
            result.append(
                AvailableD3xxDevice(
                    serial_number=device["D3xx"]["serial_number"],
                    description=device["D3xx"]["description"],
                )
            )
    return result


def force_disconnect(backend_addr: tuple[str, int]):
    """Force the backend to disconnect any open connections.

    Useful for listing devices when the backend is hogging a board.

    Args:
        backend_addr (tuple[str, int]): address of the backend
    """
    client = HttpClient(backend_addr)
    client.put("/connection/disconnect")
