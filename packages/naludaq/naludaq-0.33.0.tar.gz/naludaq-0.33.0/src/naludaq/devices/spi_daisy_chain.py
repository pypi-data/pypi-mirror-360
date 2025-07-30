from typing import TypedDict
from collections import defaultdict
import functools

from naludaq.helpers.exceptions import NotInitializedError
from naludaq.devices.spi_bus import SPIBus
from naludaq.devices.spi_device import SPIDevice
from naludaq.backend.managers.io import BoardIoManager

from logging import getLogger

LOGGER = getLogger("naludaq.spichain")


class SPIHeader(TypedDict):
    ncs_hold: bool
    rnw: bool


def initialized(func):
    """Decorator to check if the daisy chain has been initialized before running a method."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._initialized is False:
            raise NotInitializedError("Daisy chain not initialized")
        return func(self, *args, **kwargs)

    return wrapper


class SPIDaisyChain(SPIBus):
    def __init__(self, board, chain_addr: int):
        """Keeps track of the devices in a SPI daisy chain.

        The daist chain manager adds the command structure to the message to use
        with the Nalu firmware. The top 8-bits of the command are the SPI header
        for the Nalu command structure.

        The daisy chain relies on the devices being added in the correct order.
        The ordering must match the ordering of the devices on the hardware.

        Information will be pushed through the chain until it reaches the desired devices,
        since it's a chain data needs to be send to fill the chain.

        Args:
            chain_addr: The number of the daisy chain. Used by the firmware to select the correct chain.

        """
        self.board = board
        self._chain_address: int = chain_addr

        self._initialized: bool = False

        _data_width = 24  # bit, or 3-byte # TODO: This is generally set by the device.
        self._devices: defaultdict = defaultdict(None)
        self._messages: defaultdict = defaultdict(None)

    def init(self):
        """Initialize the daisy chain.

        This will set the daisy chain enable bit for each device in the chain.
        """

        for i, dev in enumerate(self._devices.values()):
            cmd = dev.init_cmd
            self._messages[i] = cmd

        messages = []
        for i, msg in enumerate(self._messages.values()):
            header = {
                "ncs_hold": False,
                "rnw": False,
            }
            spi_header = self.generate_spi_header(**header)
            spi_message = f"{spi_header}{msg}"

            messages.append(spi_message.upper())

        for message in messages:
            self._send_message(message.upper())

        self._reset_msg_buffer()

        self._initialized = True
        # for i, dev in enumerate(self._devices.values()):
        #     cmd = dev.init_cmd
        #     self._messages[i] = cmd

        # self.push_messages()

    def remove(self, device: SPIDevice):
        """Remove device at a specific address."""
        if device in self._devices.values():
            self._devices.remove(device)
            self._reset_msg_buffer()
        else:
            raise AttributeError("Device not in chain")
        self._initialized = False

    def add_message(self, message: str, device_id: int):
        """Add a message to the message queue."""

        self._messages[device_id] = message

    @initialized
    def push_messages(self):
        """Push the messages to the board.

        This will send the messages in the message queue to the board in reverse order.
        If there is no message for a device, a no-op command will be sent.

        The nCS_HOLD bit will be set to True for all devices except the last one.
        """
        if self._initialized is False:
            raise NotInitializedError("Daisy chain not initialized")

        messages = []
        for i, msg in enumerate(self._messages.values()):
            messages.append(self.generate_message(msg, i))

        for message in messages:
            self._send_message(message.upper())

        self._reset_msg_buffer()

    def generate_message(self, message: "str|None", device_id: int) -> str:
        """Generate the message to send to the board.

        Args:
            message: The message to send.
            device_id: The device id.

        Returns:
            The message to send to the board.
        """
        num_devices = len(self._messages)
        header = {
            "ncs_hold": True,
            "rnw": False,
        }
        if message is None:
            message = self[device_id].no_op()
            header["ncs_hold"] = True
        if device_id == num_devices - 1:
            header["ncs_hold"] = False
        spi_header = self.generate_spi_header(**header)
        spi_message = f"{spi_header}{message}"

        return spi_message.upper()

    def _reset_msg_buffer(self):
        """Empties the message buffer."""
        msg = defaultdict(None)
        for k in self._messages.keys():
            msg[k] = None
        self._messages = msg

    def generate_spi_header(self, ncs_hold: bool, rnw: bool) -> str:
        """Generate the SPI header for the Nalu command structure.

        The RnW bit is set to 0 for write operations, 1 for read operations.

        Args:
            ncs_hold: nCS_HOLD bit
            rnw: RnW bit

        Returns:
            SPI header for the Nalu command structure, top 8-bits of command.
        """
        sel = self._chain_address
        SPI_CMD = 0x5
        lb = (ncs_hold << 3) + (rnw << 2) + sel
        cmd = f"{SPI_CMD:1X}{lb:1X}"
        return cmd.upper()

    def _send_message(self, message: str):
        """Send a message to the board.

        Args:
            message: The message to send.
        """
        # LOGGER.debug("SPICHAIN %s is sending message: %s", self._chain_address, message)
        if self.board.using_new_backend:
            BoardIoManager(self.board).write(message)
        else:
            self.board.connection.send(message)

    def __getitem__(self, index) -> SPIDevice:
        return self._devices[index]

    def __setitem__(self, index: int, value: SPIDevice):
        self._devices[index] = value
        self._messages[index] = None
        self._initialized = False

    def __len__(self):
        return len(self._devices)

    def __iter__(self):
        for dev in self._devices.values():
            yield dev
