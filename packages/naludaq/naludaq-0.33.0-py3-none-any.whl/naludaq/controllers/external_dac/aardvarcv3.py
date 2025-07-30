import logging

from naludaq.controllers.external_dac.dac7578 import DACControllerDAC7578

logger = logging.getLogger("naludaq.ext_dac.aardvarcv3")


class DacControllerAardvarcv3(DACControllerDAC7578):
    def __init__(self, board, send_delay=0.001) -> None:
        """External DAC controller for the AARDVARCv3."""
        super().__init__(board, send_delay)
        self._cal_address = self.board.params["ext_dac"]["cal"]["address"]
        self._cal_channel = self.board.params["ext_dac"]["cal"]["channel"]

    @property
    def cal_dac(self) -> int:
        """Get the calibration channel DAC value."""
        return self.board.params.get("ext_dac", {}).get("cal", {}).get("value", 0)

    @cal_dac.setter
    def cal_dac(self, value: int):
        """Set the calibration channel DAC value."""
        self.set_cal_dac(value, set_mv=False)

    def set_cal_dac(self, value: int, set_mv: bool = False):
        self._validate_value(value, set_mv)
        if set_mv:
            value = self._convert_mv2cnt(value)

        logger.debug("Setting calibration channel to %d counts", value)
        words = [
            f"{self._write_cmd:04b}{self._cal_channel:04b}",
            f"{(value >> 4 & 0xFF):08b}",
            f"{(value << 4 & 0xFF):08b}",
        ]
        addr = self._cal_address
        self._send_command(addr, words)

        self.board.params["ext_dac"]["cal"]["value"] = value
