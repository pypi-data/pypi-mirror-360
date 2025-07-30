from naludaq.devices.spi_daisy_chain import SPIDaisyChain
from enum import Enum, auto


class SPIBUS_t(Enum):
    """SPI bus type enum."""

    DAISY_CHAIN = auto()
    SPI = auto()


class SPIConnection:
    """SPI connection class.

    Used as a baseclass for board specific SPI implementations.

    Hadnles multiple buses and devices.

    Args:
        board (Board): The board object.

    Attributes:
        board (Board): The board object.
        spi_bus (DaisyChain): The SPI bus object.
    """

    def __init__(self, board):
        self.board = board
        # self.spi_bus = board.params.get("spi", {}).get("bus", 0)
        self.spi_bus = {}

    @property
    def initialized(self):
        """Check if the SPI connection is initialized."""
        return all([bus.initialized for bus in self.spi_bus.values()])

    def init(self):
        """Initialize the SPI connection."""
        for bus in self.spi_bus.values():
            bus.init()

    def add_bus(self, bus_id: int, bus_type: SPIBUS_t):
        """Add a bus to the SPI connection.

        A spi bus is either a daisy chain or a normal SPI bus.

        Args:
            bus_id (int): The bus id.
            bus_config (int): The bus configuration.
        """
        if bus_type == SPIBUS_t.DAISY_CHAIN:
            self.spi_bus[bus_id] = SPIDaisyChain(self.board, bus_id)
        else:
            raise NotImplementedError("Only daisy chain is currently supported.")

    def add_device(self, device, bus_id: int, device_id: int):
        """Add a device to the SPI bus.

        Args:
            device (Device): The device object.
            bus_id (int): The bus id to add the device to.
        """
        if bus_id not in self.spi_bus:
            raise AttributeError(f"Bus {bus_id} not in SPI connection")

        self.spi_bus[bus_id][device_id] = device

    def write(self, message, device_id, bus_id: "int | None" = None):
        """Write a message to a device on the SPI bus.

        Args:
            message: The message to write.
            device_id: The device id on the SPI bus.
            bus_id: The bus id to write to. If None, the default bus will be used.
        """
        self.spi_bus[bus_id].add_message(message, device_id)
        self.spi_bus[bus_id].push_messages()

    def _generate_write(self, message, device_id, bus_id):
        """Generate the message for the SPI bus.

        Args:
            message: The message to write.
            device_id: The device id on the SPI bus.
            bus_id: The bus id to write to. If None, the default bus will be used.

        Returns:
            str: The generated message.
        """
        msg = self.spi_bus[bus_id]._generate_message(message, device_id, bus_id)
        return msg

    def __getitem__(self, key: int) -> SPIDaisyChain:
        return self.spi_bus[key]

    def __setitem__(self, key: int, value: SPIDaisyChain):
        self.spi_bus[key] = value

    def __len__(self):
        return len(self.spi_bus)

    def __iter__(self):
        for each in self.spi_bus.values():
            yield each

    # return iter(self.spi_bus)
