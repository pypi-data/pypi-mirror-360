import time
from typing import List

from naludaq.communication.control_registers import ControlRegisters
from naludaq.helpers.exceptions import InvalidBoardModelError

from .base import BaseDACController


class DACControllerTRBHM(BaseDACController):
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

        if self.dac_params.get("chip", None) != "ltc2620":
            raise InvalidBoardModelError(
                "This board has the wrong DAC chip (expected LTC2620)"
            )

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
            self._send_command_to_dac(
                self.COMMAND_POWER_UP_AND_UPDATE,
                self._chip_mapping[channel],
                self._channel_mapping[channel],
                values[channel],
            )

    def set_calibration_channel_dacs(self, chip: int, value: int):
        """Sets the ext. DAC offset for one of the calibration channels.

        Args:
            chip (int): must be 0 or 1 for chips corresponding to channels
                0-3 or 4-7, respectively.
            value (int): DAC value to set for the calibration channel.

        Raises:
            ValueError: if the chip number is invalid or the value is out of bounds.
        """
        self._validate_chip_number_or_raise(chip)
        self._validate_value(value)

        self._send_command_to_dac(
            self.COMMAND_POWER_UP_AND_UPDATE,
            chip,
            self._channel_mapping[f"cal{chip}"],
            value,
        )

    def power_down_channels(self, channels: "list[int]"):
        """Power down the given channels. The DAC outputs are set to high impedance,
        and passively pulled to ground by 90kOhm resistors.

        Args:
            channels (list[int]): which channels to power down.

        Raises:
            TypeError: if the argument given is not a list[int].
            ValueError: if the channels given are invalid.
        """
        self._validate_channels(channels)

        for channel in channels:
            self._send_command_to_dac(
                self.COMMAND_POWER_DOWN,
                self._chip_mapping[channel],
                self._channel_mapping[channel],
                0,  # value is ignored by the chip for power down command
            )

    def power_down_calibration_channel(self, chip: int):
        """Power down the calibration channel on the given chip."""
        self._validate_chip_number_or_raise(chip)
        self._send_command_to_dac(
            self.COMMAND_POWER_DOWN,
            self._chip_mapping[f"cal{chip}"],
            self._channel_mapping[f"cal{chip}"],
            0,  # value is ignored by the chip for power down command
        )

    def _validate_chip_number_or_raise(self, chip: int):
        """Validate the chip number or raise ValueError"""
        if chip not in [0, 1]:
            raise ValueError("Chip must be 0 or 1")
        if f"cal{chip}" not in self._channel_mapping:
            raise NotImplementedError(
                "This board does not have a calibration channel defined, or it is not supported"
            )

    def _send_command_to_dac(
        self, command: int, dac_chip: int, dac_channel: int, value: int
    ):
        """Writes a single instruction to a particular DAC chip.

        There are two DAC chips, and the firmware uses the same set of registers
        to communicate with both. Which chip gets updated is determined by the
        'idac_update' register.

        Args:
            command (int): 4-bit command field
            dac_chip (int): the dac chip to write to, 0 or 1.
            dac_channel (int): the dac channel to write to. This is NOT the
                ASIC channel number.
            value (int): the 12-bit value to write to the DAC.
        """
        # 0. make sure the update signal is low (just in case)
        self._write_control_register("idac_update", 0)

        # 1. set the instruction
        self._write_control_register("idac_command", command)
        self._write_control_register("idac_address", dac_channel)
        self._write_control_register("idac_value", value)

        # 2. Start writing to the DACs.
        # which chip along a particular chain we want to write to (each chain only has one chip)
        self._write_control_register("idac_chip_number", 0)
        # which chain we want to write to
        self._write_control_register("idac_update", 1 << dac_chip)
        self._write_control_register("idac_update", 0)

        # writing too fast could theoretically cause subsequent instructions to not be received
        time.sleep(0.01)

    def _write_control_register(self, name: str, value: int):
        """Writes a control register."""
        ControlRegisters(self.board).write(name, value)
