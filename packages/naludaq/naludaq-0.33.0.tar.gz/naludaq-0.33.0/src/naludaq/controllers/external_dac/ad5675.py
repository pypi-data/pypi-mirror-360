import logging
from typing import List

from naludaq.helpers.exceptions import InvalidBoardModelError

from .i2c_dac import I2CDACController

LOGGER = logging.getLogger("naludaq.ext_dac.ad5675")


class DACControllerAD5675(I2CDACController):
    def __init__(self, board, send_delay=0.3) -> None:
        """Controller for the AD5675 DAC.

        Args:
            board (Board): the board object.
            send_delay (float): the time to wait between sequential I2C
                writes in seconds.
        """
        super().__init__(board, send_delay=send_delay)
        self._write_cmd = 0b0011

        if board.params["ext_dac"]["chip"] != "ad5675":
            raise InvalidBoardModelError(
                "The given board cannot be used with this DAC controller"
            )

    def _get_write_words(self, channel: int, value: int) -> List[str]:
        """Get words to write to set the DAC value for a channel.

        Args:
            channel (int): the channel to set the DAC value for.
            value (int): the DAC value.

        Returns:
            A list of bytes to send over the I2C bus.
        """
        value_bits = f"{value:016b}"
        return [
            f"{self._write_cmd:04b}{self._channel_mapping[channel]:04b}",
            value_bits[:8],
            value_bits[8:],
        ]
