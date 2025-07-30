"""Gain stage controller for the aodsoc_aods board.
"""

from naludaq.communication import LOGGER
from naludaq.communication.analog_registers import AnalogRegisters

from .aodsv2 import GainStageController as AODSV2GainStageController


class GainStageController(AODSV2GainStageController):
    """Controls the AODS gain stages

    Gain stages are controlled by the following registers:
    - sel_0: ch0 input buffer
    - sel_1: ch1 input buffer
    - sel_2: ch2 input buffer
    - sel_3: ch3 input buffer
    - sel_4: external output
    - sel_5: ch1 BAMP or x8 of ch0 output
    - sel_6: select either BAMP or 8x gain for ch3
    - sel_7: select ch3 input either ch0 output or ch2 output

    There are several functions in the form `ch{X}_{some possible configuration}`
    such as `ch3_external_input()` that serve as presets and a human-readable
    way to configure each stage. Note that the configurations for each channel
    are mutually exclusive; e.g. you cannot have ch1 external input and ch1 8x ch0
    simulatenously.
    """

    def __init__(self, board, chip_number=0):
        """Initialize the controller"""
        super().__init__(board)
        self.chip_num = chip_number

    @property
    def sel_values(self) -> "list[bool]":
        """Get a list of sel values from the internally stored registers"""
        analog_registers = self.board.registers["analog_registers"]
        return [
            analog_registers[f"sel_{i}"]["value"][self.chip_num]
            for i in range(self._num_stages)
        ]

    def _write_reg(self, reg, value):
        """Write a register.

        We need to override the chip mask manually since we don't support
        multichip registers yet.
        """
        LOGGER.debug("Selecting chip %d", self.chip_num)
        AnalogRegisters(self.board, self.chip_num).write(reg, value)
