import time
from typing import List

from naludaq.communication.control_registers import ControlRegisters

from .base import BaseDACController


class DACControllerHiper(BaseDACController):
    COMMAND_POWER_UP_AND_UPDATE = 0b0011
    COMMAND_POWER_DOWN = 0b0100  # 16-bit data field is ignored

    def __init__(self, board) -> None:
        """DAC controller for the TRBHM board, which uses two LTC2620 chips.

        In addition to supporting setting the DACs for channels 0-7, this controller
        can also set the DACs for both calibration channels and can power down DACs
        for individual channels.

        The LTC2620 is controlled over SPI, which the firmware has an abstraction
        for. Although the firmware supports daisy chaining multiple LTC2620 chips,
        it has a separate chain for each DAC chip, meaning that each chip is at index
        zero in their respective chains.
        """
        super().__init__(board)
        self._chip_mapping = self.dac_params["chip_mapping"]
        self._channel_mapping = self.dac_params["channel_mapping"]
        self._side_mapping = self.dac_params["side_mapping"]

    def _write_dacs(self, channels: List[int]):
        """Writes the internal DAC values for the given channels to the external DAC chips.

        This function will turn the DACs on if they are off (see datasheet p.12)

        Args:
            channels (list[int]): List of channels to write DACs for

        Raises:
            ValueError: if any of the DAC values on the board object are invalid.
        """
        try:
            self._validate_internal_dac_values()
        except ValueError:
            raise

        values = self.board.dac_values
        for channel in channels:
            if channel // 4 not in self.board.params["installed_chips"]:
                continue
            side = self._side_mapping[channel]
            dac_chip = self._chip_mapping[channel]
            dac_channel = self._channel_mapping[channel]
            self._send_command_to_dac(
                self.COMMAND_POWER_UP_AND_UPDATE,
                side,
                dac_chip,
                dac_channel,
                values[channel],
            )

    def _send_command_to_dac(
        self, command: int, side: int, dac_chip: int, dac_channel: int, value: int
    ):
        """Writes a single instruction to a particular DAC chip.

        There are two DAC chips, and the firmware uses the same set of registers
        to communicate with both. Which chip gets updated is determined by the
        'idac_update' register.

        Args:
            command (int): 4-bit command field
            side (int): 0 for left, 1 for right
            dac_chip (int): the dac chip to write to, 0 or 1.
            dac_channel (int): the dac channel to write to. This is NOT the
                ASIC channel number.
            value (int): the 12-bit value to write to the DAC.
        """
        s = {
            0: "l",
            1: "r",
        }[side]

        # 0. make sure the update signal is low (just in case)
        self._write_control_register(f"dac_{s}_update", 0)

        # 1. set the instruction
        self._write_control_register(f"dac_{s}_cmd", command)
        self._write_control_register(f"dac_{s}_asic", dac_chip)
        self._write_control_register(f"dac_{s}_addr", dac_channel)
        self._write_control_register(f"dac_{s}_value", value)

        # 2. update the DAC
        self._write_control_register(f"dac_{s}_update", 1)
        self._write_control_register(f"dac_{s}_update", 0)

        # writing too fast could theoretically cause subsequent instructions to not be received
        time.sleep(0.01)

    def _write_control_register(self, name: str, value: int):
        """Writes a control register."""
        ControlRegisters(self.board).write(name, value)
