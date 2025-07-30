"""Gain stage controller for the aodsv2_eval board.
"""
from logging import getLogger
from typing import List, Tuple

from naludaq.communication.analog_registers import AnalogRegisters
from naludaq.controllers.controller import Controller

LOGGER = getLogger("naludaq.gainstage_controller")


class GainStageController(Controller):
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

    def __init__(self, board):
        """Initialize the controller"""
        super().__init__(board)
        self._num_stages = 8

    @property
    def sel_values(self) -> "list[bool]":
        """Get a list of sel values from the board registers"""
        analog_registers = self.board.registers["analog_registers"]
        return [
            analog_registers[f"sel_{i}"]["value"][0] for i in range(self._num_stages)
        ]

    def set_manual(self, stages: List[bool]) -> List[Tuple[int, int]]:
        """Manually set the gainstages.

        This will set the gainstages to the values of the index in the list
        Each index corresponds to a gainstage and can be either True or False.

        Args:
            stages (List[bool]): List of boolean values.

        Returns:
            List[Tuple[int, int]]: List of tuples with (channel input, total gain)

        Raises:
            ValueError: If the length of the gainstages list is not 7.
        """
        self._validate_manual_input_or_raise(stages)
        for i, stage in enumerate(stages):
            self._write_reg(f"sel_{i}", stage)
        return self.compute_gains()

    def _validate_manual_input_or_raise(self, stages: List[bool]):
        """Validate the manual stages and raise an error if invalid"""
        if not isinstance(stages, list):
            raise TypeError("stages must be a list")
        if not all([s in [0, 1] for s in stages]):
            raise TypeError("Expected a list of boolean values")
        if len(stages) != self._num_stages:
            raise ValueError(f"Expected {self._num_stages} stages, got {len(stages)}")

    def ch0_external_input(self):
        """Disable ch0 input buffer"""
        sel_values = self.sel_values
        sel_values[0] = 0
        return self.set_manual(sel_values)

    def ch0_external_input_buffered(self):
        """Enable ch0 buffered input"""
        sel_values = self.sel_values
        sel_values[0] = 1
        return self.set_manual(sel_values)

    def ch1_external_input(self):
        """Disable ch1 input buffer"""
        sel_values = self.sel_values
        sel_values[1] = 0
        sel_values[5] = 0  # don't care
        return self.set_manual(sel_values)

    def ch1_512x_ch0_input(self):
        """Enable ch1 BAMP of ch0 output"""
        sel_values = self.sel_values
        sel_values[1] = 1
        sel_values[5] = 1
        return self.set_manual(sel_values)

    def ch1_8x_ch0(self):
        """Enable ch1 8x of ch0 output"""
        sel_values = self.sel_values
        sel_values[1] = 1
        sel_values[5] = 0
        return self.set_manual(sel_values)

    def ch2_external_input(self):
        """Enable ch2 external input"""
        sel_values = self.sel_values
        sel_values[2] = 0
        return self.set_manual(sel_values)

    def ch2_8x_ch1(self):
        """Enable ch2 8x input"""
        sel_values = self.sel_values
        sel_values[2] = 1
        return self.set_manual(sel_values)

    def ch3_external_input(self):
        """Enable ch3 external input"""
        sel_values = self.sel_values
        sel_values[3] = 0
        sel_values[6] = 0  # don't care
        sel_values[7] = 0  # don't care
        return self.set_manual(sel_values)

    def ch3_8x_ch0(self):
        """Enable ch3 8x input"""
        sel_values = self.sel_values
        sel_values[3] = 1
        sel_values[6] = 0
        sel_values[7] = 1
        return self.set_manual(sel_values)

    def ch3_512x_ch0(self):
        """Enable ch3 BAMP input"""
        sel_values = self.sel_values
        sel_values[3] = 1
        sel_values[6] = 1
        sel_values[7] = 1
        return self.set_manual(sel_values)

    def ch3_8x_ch2(self):
        """Enable ch3 8x of ch2 output"""
        sel_values = self.sel_values
        sel_values[3] = 1
        sel_values[6] = 0
        sel_values[7] = 0
        return self.set_manual(sel_values)

    def ch3_512x_ch2(self):
        """Enable ch3 BAMP of ch2 output"""
        sel_values = self.sel_values
        sel_values[3] = 1
        sel_values[6] = 1
        sel_values[7] = 0
        return self.set_manual(sel_values)

    def enable_external_output(self):
        """Enable external output"""
        sel_values = self.sel_values
        sel_values[4] = 1
        return self.set_manual(sel_values)

    def disable_external_output(self):
        """Disable external output"""
        sel_values = self.sel_values
        sel_values[4] = 0
        return self.set_manual(sel_values)

    def compute_gains(self, sel: "list[bool]" = None):
        """Compute the gains for the current configuration"""
        if sel is None:
            sel = self.sel_values
        self._validate_manual_input_or_raise(sel)

        prev_ch = []
        prev_ch.append((0, 1))  # ch0
        prev_ch.append(self._compute_ch1(sel))  # ch1
        prev_ch.append(self._compute_ch2(sel, prev_ch))  # ch2
        prev_ch.append(self._compute_ch3(sel, prev_ch))  # ch3
        prev_ch.append(self._compute_ext(sel, prev_ch))  # ext

        return prev_ch

    def _compute_ch1(self, sel) -> Tuple[int, int]:
        """Return a tuple with (channel input, total gain)"""
        ch_input = 1
        gain = 1
        if sel[1]:
            ch_input = 0
            gain = -8
            if sel[5]:
                gain = -512

        return (ch_input, gain)

    def _compute_ch2(
        self, sel, prev_stages: "list[tuple[int, int]]"
    ) -> Tuple[int, int]:
        """Return a tuple with (channel input, total gain)"""
        prev_stage = prev_stages[-1]
        ch_input = 2
        gain = 1
        if sel[2]:
            ch_input = prev_stage[0]
            gain = -8 * prev_stage[1]

        return (ch_input, gain)

    def _compute_ch3(
        self, sel: "list[int]", prev_stages: "list[tuple[int, int]]"
    ) -> Tuple[int, int]:
        """Return a tuple with (channel input, total gain)"""
        prev_stage = (0, 1) if sel[7] else prev_stages[-1]
        prev_gain = prev_stage[1]

        ch_input = 3
        gain = 1
        if sel[3]:
            ch_input = prev_stage[0]
            gain = -8 * prev_gain
            if sel[6]:
                gain = -512 * prev_gain

        return (ch_input, gain)

    def _compute_ext(self, sel, prev_stages) -> Tuple[int, int]:
        """Return a tuple with (channel input, total gain)"""
        ch_input, gain = prev_stages[3]
        if not sel[4]:
            ch_input = prev_stages[3][0]
            gain = 0

        return (ch_input, gain)

    def _write_reg(self, reg, value):
        """Write a register"""
        AnalogRegisters(self.board).write(reg, value)

    def __repr__(self) -> str:
        """Return a string representation of the object"""
        gains = self.compute_gains()
        return "".join(
            [
                f"self.__class__.__name__ - ",
                f"ch0=ch{gains[0][0]}x{gains[0][1]}), ",
                f"ch1=ch{gains[1][0]}x{gains[1][1]}), ",
                f"ch2=ch{gains[2][0]}x{gains[2][1]}), ",
                f"ch3=ch{gains[3][0]}x{gains[3][1]}), ",
                f"ext=ch{gains[4][0]}x{gains[4][1]})",
            ]
        )
