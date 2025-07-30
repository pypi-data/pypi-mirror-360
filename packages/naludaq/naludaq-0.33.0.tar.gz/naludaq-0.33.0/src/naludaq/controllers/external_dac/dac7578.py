import logging
import time
from typing import List

import numpy as np

from naludaq.communication import sendI2cCommand
from naludaq.controllers.external_dac.i2c_dac import I2CDACController
from naludaq.helpers.exceptions import InvalidBoardModelError

LOGGER = logging.getLogger("naludaq.ext_dac.dac7578")


class DACControllerDAC7578(I2CDACController):
    """DAC controller for boards using the DAC7578 DAC."""

    def __init__(self, board, send_delay=0.001) -> None:
        """Controller for the DAC7578 DAC.

        Args:
            board (Board): the board object.
            send_delay (float): the time to wait between sequential I2C
                writes in seconds.
        """
        super().__init__(board, send_delay=send_delay)
        self._write_cmd = 0b0011

        if board.params["ext_dac"]["chip"] != "dac7578":
            raise InvalidBoardModelError(
                "The given board cannot be used with this DAC controller"
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

        if (
            set(channels) == set((range(self.board.channels)))
            and len(set(self.board.dac_values)) == 1
        ):
            self._broadcast_to_all_channels()
            return

        self._write_to_channels(channels)

    def _write_to_channels(self, channels: List[int]) -> None:
        """Writes the external dac values per channel in channels"""
        LOGGER.info(
            f"Setting channels {channels} to: {[self.board.dac_values[channel] for channel in channels]}"
        )
        for channel in channels:
            value = self.board.dac_values[channel]
            addr = self._address_mapping[channel]
            words = self._get_write_words(channel, value)
            self._send_command(addr, words)

    def _broadcast_to_all_channels(self):
        """Broadcast  to every channel on EVERY ext. DAC chip."""
        unique_addrs = self._get_unique_addresses()
        for addr in unique_addrs:
            addr = int(addr)
            value = self.board.dac_values[0]
            words = self._get_broadcast_words(value)
            LOGGER.info("Broadcasting DAC value: %s to DAC %s", value, addr)
            self._send_command(addr, words)

    def _send_command(self, addr: int, words: list[str], rw: int = 0) -> None:
        """Send the given words to the DAC at the given address.

        Args:
            addr (int): the address of the DAC to send the words to.
            words (List[str]): the words to send to the DAC.
            rw (int): r/w bit (0 = write, 1 = read)

        Raises:
            ConnectionError if the I2C commands could not be sent
        """
        LOGGER.debug("Sent DAC Command - ADDR: %s, WORDS: %s", (addr << 1) | rw, words)
        if not sendI2cCommand(self.board, (addr << 1) | rw, words):
            raise ConnectionError("Failed to write I2C DAC")
        time.sleep(self._send_delay)

    def _get_write_words(self, channel: int, value: int) -> List[str]:
        """Get words to write to set the DAC value for a channel.

        Args:
            channel (int): the channel to set the DAC value for.
            value (int): the DAC value.

        Returns:
            A list of bytes to send over the I2C bus.
        """
        return [
            f"{self._write_cmd:04b}{self._channel_mapping[channel]:04b}",
            f"{(value >> 4 & 0xFF):08b}",
            f"{(value << 4 & 0xFF):08b}",
        ]

    def _get_broadcast_words(self, value: int) -> list[str]:
        return [
            f"{self._write_cmd:04b}{0b1111:04b}",
            f"{(value >> 4 & 0xFF):08b}",
            f"{(value << 4 & 0xFF):08b}",
        ]

    def _get_unique_addresses(self):
        return list(np.unique(list(self._address_mapping.values())))
