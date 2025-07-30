import abc
import logging
import time
from typing import List

from naludaq.communication import sendI2cCommand
from naludaq.helpers.exceptions import RegisterFileError

from .base import BaseDACController

LOGGER = logging.getLogger("naludaq.ext_dac.i2c_dac")


class I2CDACController(BaseDACController):
    def __init__(self, board, send_delay: float) -> None:
        """ABC DAC controller for DAC chips that communicate through the I2C
        protocol.

        Args:
            board (Board): the board object
            send_delay (float): the time to wait between sequential I2C
                writes in seconds.

        Raises:
            TypeError if the send delay is not a numeric type
            ValueError if the send delay is a negative value
        """
        if not isinstance(send_delay, (int, float)):
            raise TypeError("Send delay must be numeric")
        if send_delay < 0:
            raise TypeError("Send delay cannot be negative")

        super().__init__(board)
        self._send_delay = send_delay
        self._address_mapping = self.dac_params["address_mapping"]
        self._channel_mapping = self.dac_params["channel_mapping"]

    def _validate_ext_dac_params(self, params: dict):
        """Validates the `ext_dac` field in the YAML.

        Args:
            params (dict): the board params.

        Raises:
            RegisterFileError if the ext_dac params is missing
                any requirements of the base class, or if it is
                missing `address_mapping` or `channel_mapping`
                or they hold invalid values/types.
        """
        super()._validate_ext_dac_params(params)
        dac_params = params["ext_dac"]
        chip = dac_params.get("chip", None)
        address_mapping = dac_params.get("address_mapping", None)
        channel_mapping = dac_params.get("channel_mapping", None)
        if address_mapping is None:
            raise RegisterFileError("External DAC params missing address mapping")
        if channel_mapping is None:
            raise RegisterFileError("External DAC params missing channel mapping")
        if chip is None:
            raise RegisterFileError("External DAC params missing chip field")
        if not isinstance(address_mapping, dict):
            raise RegisterFileError("Address mapping must be a dict")
        if not isinstance(channel_mapping, dict):
            raise RegisterFileError("Channel mapping must be a dict")
        if not isinstance(chip, str):
            raise RegisterFileError("Chip must be a str")

        if not all(isinstance(x, int) and x > 0 for x in address_mapping.values()):
            raise RegisterFileError(
                "One or more values in address mapping is not a non-negative int"
            )
        if not all(isinstance(x, int) and x > 0 for x in address_mapping.values()):
            raise RegisterFileError(
                "One or more values in channel mapping is not a non-negative int"
            )

    def _write_dacs(self, channels: List[int]):
        """Writes the values to the DAC for each board channel given.

        The values written come from the board object.

        Args:
            channels (List[int]): list of channels to set the
                DACs for.

        Raises:
            TypeError if the given channels are of the wrong type
            ValueError if any of the internal DAC values on the board
                are out of bounds.
            ConnectionError if the I2C commands could not be sent
        """
        try:
            self._validate_channels(channels)
            self._validate_internal_dac_values()
        except (TypeError, ValueError):
            raise

        rw = 0
        for channel in channels:
            value = self.board.dac_values[channel]
            addr = self._address_mapping[channel]
            words = self._get_write_words(channel, value)
            LOGGER.info("Setting bias DAC ch%s to: %s", channel, value)
            LOGGER.debug(f"Sent DAC Command: {words}")
            if not sendI2cCommand(self.board, (addr << 1) | rw, words):
                raise ConnectionError("Failed to write I2C DAC")
            time.sleep(self._send_delay)

    @abc.abstractmethod
    def _get_write_words(self, channel: int, value: int) -> List[str]:
        """Get words to write to set the DAC value for a channel.

        Args:
            channel (int): the channel to set the DAC value for.
            value (int): the DAC value.

        Returns:
            A list of bytes to send over the I2C bus.
        """
