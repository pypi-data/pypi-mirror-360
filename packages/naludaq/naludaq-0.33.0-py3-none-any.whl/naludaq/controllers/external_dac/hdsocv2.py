from typing import List

from naludaq.devices.ad5674r import AD5674R_SPI
from naludaq.controllers.external_dac.base import BaseDACController
from collections import defaultdict


def require_initialized():
    """Check if the SPI connection is initialized."""

    def wrapped_func(func):
        def wrapper(self, *args, **kvargs):
            self._validate_spi_connection_or_raise()
            func(self, *args, **kvargs)

        return wrapper

    return wrapped_func


class DACControllerHDSoCv2(BaseDACController):
    def __init__(self, board):
        """HDSoCv2 DAC controller.

        HDSoCv2 uses Daisy Chained SPI DAC chips AD5674 in two chains
        Due to this configuration the DAC controller works a bit different.
        However the API should be the same as all other DAC controllers.

        Args:
            board: the board object must contain the SPI daisy chains.
        """
        self.board = board

    @property
    def spi(self):
        return self.board.spi_connection

    def _validate_spi_connection_or_raise(self):
        """Validate the SPI connection for the board.

        The spi connection should have two buses for the DACs.
        Each bus should have two devices.
        The two devices should have the channelmap set to the correct values.

        The spi chain should be initialized and the devices should be initialized.

        If the validation fails, an exception will be raised.

        Raises:
            AttributeError: If the validation fails.
        """
        if self.spi is None:
            raise AttributeError("SPI connection is not set")
        if not len(self.spi) >= 2:
            raise AttributeError(
                f"SPI connection should have two buses for the DACs got {len(self.spi)}"
            )
        if len(self.spi[0b01]) != 2 or len(self.spi[0b10]) != 2:
            raise AttributeError("Each bus should have two devices")
        for bus in self.spi:
            for device in bus:
                if not isinstance(device, AD5674R_SPI):
                    raise AttributeError(
                        f"The devices should be AD5674R_SPI objects, got {device}"
                    )
            if not bus._initialized:
                raise AttributeError(
                    f"The bus should be initialized: {bus._initialized}"
                )
        return True

    def _get_device_num(self, channel):
        """Return (device_id, bus_id) for a channel.

        This function will compute the correct bus and device number.
        The devices are connected on the HDSoCv2 eval board in the following way:
        - 0-15: West DAC1
        - 16-31: West DAC0
        - 32-47: East DAC1
        - 48-63: East DAC0

        Args:
            channel: The channel number.

        Returns:
            Tuple of (device_id, bus_id)

        Raises:
        TypeError: If the channel is not an int.
            ValueError: If the channel is not in the range of 0-63.
        """
        bus_num_to_id = {
            0: 0b01,
            1: 0b10,
        }
        validate_channel_or_raise(self.board, channel)
        device_num, _ = divmod(channel, 16)
        bus, dev = divmod(device_num, 2)
        dev = 1 - dev  # invert the device number
        return (bus_num_to_id[bus], dev)

    @require_initialized()
    def _write_dacs(self, channels: List[int]):
        """Write the values from the internal DAC values to the DACs.

        Args:
            channels: List of channels

        """
        dac_values = self.board.dac_values

        chmap = defaultdict(list)
        valmap = defaultdict(list)
        for channel in channels:
            devnum = self._get_device_num(channel)
            chmap[devnum].append(channel)
            valmap[devnum].append(dac_values[channel])

        for (bus_id, dev_id), chans in chmap.items():
            device = self.spi[bus_id][dev_id]
            vals = valmap[devnum]
            if len(chans) == 16 and len(set(vals)) == 1:  # check for broadcast
                device.broadcast(valmap[devnum][0])
            else:
                for i, channel in enumerate(chans):
                    device.set_channel(channel, vals[i])


def validate_channel_or_raise(board, channel):
    if not isinstance(channel, int):
        raise TypeError("Channel must be an int")
    if not (0 <= channel < board.channels):
        raise ValueError(f"Channels must be between 0 and {board.channels - 1}")
