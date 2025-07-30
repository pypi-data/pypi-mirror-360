from dataclasses import dataclass

from naludaq.helpers.exceptions import WrongDeviceError
from naludaq.devices.spi_device import SPIDevice
from naludaq.devices.spi_bus import SPIBus
from naludaq.communication.spi import SPIConnection


@dataclass
class AD5674RCommands:
    """ "
    C3 C2 C1 C0 Description
    0 0 0 0 No operation
    0 0 0 1 Write to Input Register n where n = 1 to 8, depending on the DAC selected from the address bits in Table 11 (dependent on LDAC)
    0 0 1 0 Update DAC Register n with contents of Input Register n
    0 0 1 1 Write to and update DAC Channel n
    0 1 0 0 Power down/power up the DAC
    0 1 0 1 Hardware LDAC mask register
    0 1 1 0 Software reset (power-on reset)
    0 1 1 1 Internal reference setup register
    1 0 0 0 Set up the daisy-chain enable (DCEN) register
    1 0 0 1 Set up the readback register (readback enable)
    1 0 1 0 Update all channels of the input register simultaneously with the input data
    1 0 1 1 Update all channels of the DAC register and input register simultaneously with the input data
    1 1 0 0 Reserved
    … … … …
    1 1 1 1 No operation, daisy-chain mod
    """

    no_op = 0x0
    write_reg = 0x1
    update_dac_reg = 0x2
    write_and_update_dac_chan = 0x3
    toggle_power = 0x4
    LDAC_mask = 0x5
    software_rst = 0x6
    internal_reference_setup_reg = 0x7
    daisy_chain_enable = 0x8
    readback_en = 0x9
    upd_all_input_from_value = 0xA
    upd_all_dac_from_value = 0xB
    no_op_daisy_chain = 0xF


class AD5674R_SPI(SPIDevice):
    def __init__(
        self,
        spi_connection,
        bus_id,
        device_id,
        channelmap: dict[int, int],
        daisy_chained: bool = True,
    ):
        self._connection: SPIConnection = spi_connection
        self.bus_id: int = bus_id
        self.device_id: int = device_id
        super().__init__(daisy_chained)

        self.channelmap: dict[int, int] = channelmap
        self._commands = AD5674RCommands()

    @property
    def connection(self) -> SPIBus:
        device = self._connection[self.bus_id]
        return device

    @property
    def channelmap(self) -> dict[int, int]:
        return self._channelmap

    @channelmap.setter
    def channelmap(self, value: dict[int, int]):
        self._channelmap = value

    @property
    def init_cmd(self) -> str:
        """Generate the initialization command for the device."""
        dc_en = self._daisy_chained
        cmd = AD5674RCommands.daisy_chain_enable
        message = f"{cmd:1x}0000{dc_en:1X}"
        return message.upper()

    @property
    def daisy_chain_en(self) -> bool:
        return self._daisy_chained

    @daisy_chain_en.setter
    def daisy_chain_en(self, enabled: bool):
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool.")
        self._daisy_chained = enabled

    def init(self):
        """Initialize the device.

        This will set the daisy chain enable bit for the device.
        """
        message = self.init_cmd()

        self._write(message)

    def no_op(self) -> str:
        """Get a no-op command for the device.

        Will return a no-op command for the device. If the device is daisy chained
        then the no-op command will be a daisy chain no-op command.
        """
        if self._daisy_chained is False:
            cmd = AD5674RCommands.no_op
        else:
            cmd = AD5674RCommands.no_op_daisy_chain
        addr = 0
        value = 0
        msg = f"{cmd:1x}{addr:1x}{value:03x}0"

        return msg.upper()

    def set_channel(self, channel: int, value: int):
        """Set a channel to a specific value.

        Args:
            channel: ASIC channel
            value: 12-bit digital value.

        Raise:

        """
        try:
            addr = self._channelmap[channel]
        except KeyError:
            raise WrongDeviceError(f"This device doesn't map to channel: {channel}")
        cmd = AD5674RCommands.write_and_update_dac_chan

        message = f"{cmd:01x}{addr:01x}{value:03x}0".upper()
        self._write(message)

    def broadcast(self, value: int):
        """Broadcast a value to all channels.

        Args:
            value: 12-bit digital value.
        """
        cmd = AD5674RCommands.upd_all_dac_from_value
        addr = 0x0

        message = f"{cmd:1x}{addr:1x}{value:03x}0".upper()
        self._write(message)

    def _write(self, message: str):
        """Write a message to the device.

        The write is passed to the connection object which will handle the message.

        Args:
            message: The message to write.
        """
        self._connection.write(message, self.device_id, self.bus_id)
