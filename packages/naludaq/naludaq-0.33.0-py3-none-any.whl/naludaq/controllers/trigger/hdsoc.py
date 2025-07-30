"""Trigger controller for the HDSoC series of eval boards.

The HDSoC trigger circuit operates differently than the typical way
found on other boards. The HDSoC allows the reference voltages to be
set arbitrarily, theoretically giving the user a higher level of
control and precision over where the trigger threshold is set.

That being said, the trigger circuit is also highly non-linear,
making it difficult to set manually.
"""
import logging
from enum import Enum

from naludaq.helpers.helper_functions import type_name

from .default import TriggerController

logger = logging.getLogger("naludaq.trigger_controller_hdsoc")


class TriggerGroup(Enum):
    """Used to select grouped channels for setting trigger thresholds and references."""

    LEFT = 0
    RIGHT = 16
    CH0_15 = 0
    CH16_31 = 16


class TriggerControllerHdsoc(TriggerController):
    """Trigger controller for the HDSoC board

    HDSoC has a different division of the Trigger circuit.
    The trigger is set with an 8-bit value but the upper and lower
    reference voltages for the trigger circuit can be set.
    The upper and lower reference voltages are set for 0-15 and 16-31
    """

    def __init__(self, board):
        super().__init__(board)

        self._trig_thresh_regname = "trigger_threshold_{}"
        self._first_right_channel = 16

    @property
    def max_reference(self) -> int:
        """Maximum trigger reference value"""
        max_ref = 2 ** self.params.get("ref_bits", 4) - 1
        return max_ref

    @property
    def max_threshold(self) -> int:
        """Maximum trigger value"""
        max_val = 2 ** self.params.get("val_bits", 8) - 1
        return max_val

    @property
    def references(self) -> dict[str, tuple[int, int]]:
        """Get the current low/high references for the left and right side

        left side is ch 0_15
        right side is ch 16_31
        """
        return {
            "0_15": self.left_references,
            "16_31": self.right_references,
        }

    @references.setter
    def references(self, values: "dict[int | str | TriggerGroup, tuple[int, int]]"):
        """Set the low/high references for the left and right side"""
        self._validate_reference_dict_or_raise(values)
        self._set_references(values)

    @property
    def low_references(self) -> dict[str, int]:
        """Get the current low references for the left and right side"""
        return {
            "0_15": self._get_analog_register("sub_ref_neg_sb_left_trigger"),
            "16_31": self._get_analog_register("sub_ref_neg_sb_right_trigger"),
        }

    @low_references.setter
    def low_references(self, values: "dict[int | str | TriggerGroup, int]"):
        """Set the low references for the left and right side"""
        if not isinstance(values, dict):
            raise TypeError(f"Values must be a dict, not {type_name(values)}")
        for side, value in values.items():
            if side in [0, "left", "0_15", TriggerGroup.LEFT]:
                regname = "sub_ref_neg_sb_left_trigger"
            elif side in [16, "right", "16_31", TriggerGroup.RIGHT]:
                regname = "sub_ref_neg_sb_right_trigger"
            else:
                raise ValueError(f"Invalid side: {side}")
            self._write_analog_register(regname, value)

    @property
    def high_references(self) -> dict[str, int]:
        """Get the current high references for the left and right side"""
        return {
            "0_15": self._get_analog_register("sub_ref_pos_sb_left_trigger"),
            "16_31": self._get_analog_register("sub_ref_pos_sb_right_trigger"),
        }

    @high_references.setter
    def high_references(self, values: "dict[int | str | TriggerGroup, int]"):
        """Set the high references for the left and right side"""
        if not isinstance(values, dict):
            raise TypeError(f"Values must be a dict, not {type_name(values)}")
        for side, value in values.items():
            if side in [0, "left", "0_15", TriggerGroup.LEFT]:
                regname = "sub_ref_pos_sb_left_trigger"
            elif side in [16, "right", "16_31", TriggerGroup.RIGHT]:
                regname = "sub_ref_pos_sb_right_trigger"
            else:
                raise ValueError(f"Invalid side: {side}")
            self._write_analog_register(regname, value)

    @property
    def left_references(self) -> tuple[int, int]:
        """Get the current low/high references for the left side"""
        return (
            self._get_analog_register("sub_ref_neg_sb_left_trigger"),
            self._get_analog_register("sub_ref_pos_sb_left_trigger"),
        )

    @property
    def right_references(self) -> tuple[int, int]:
        """Get the current low/high references for the right side"""
        return (
            self._get_analog_register("sub_ref_neg_sb_right_trigger"),
            self._get_analog_register("sub_ref_pos_sb_right_trigger"),
        )

    @property
    def edge(self) -> bool:
        """Get the trigger edge for all channels on the board."""
        raise NotImplementedError("Single edge is not implemented for HDSOCv1")

    @edge.setter
    def edge(self, value: bool):
        """Set the trigger edge for all channels on the board."""
        if not isinstance(value, bool):
            raise TypeError("edge must be a bool")
        value = {ch: value for ch in [TriggerGroup.LEFT, TriggerGroup.RIGHT]}
        self.edges = value

    @property
    def edges(self) -> "dict[int, bool]":
        """Get the trigger edge for all channels on the board."""
        edges = {}
        for side in ["left", "right"]:
            reg = f"tsgn_{side}"
            edge = bool(self._get_analog_register(reg))
            if side == "left":
                channels = range(0, 16)
            elif side == "right":
                channels = range(16, 32)
            edges.update({ch: edge for ch in channels})
        return edges

    @edges.setter
    def edges(self, value: "dict[int | str | TriggerGroup, bool]"):
        """Set the trigger edge for all channels on the board."""
        if not isinstance(value, dict):
            raise TypeError("edges must be a dict")
        self._set_trigger_edges(value)

    @property
    def tsel(self) -> dict[str, bool]:
        """Get the current tsel state for the left and right side"""
        return {
            "0_15": bool(self._get_analog_register("tsel_left")),
            "16_31": bool(self._get_analog_register("tsel_right")),
        }

    @tsel.setter
    def tsel(self, values: "dict[int | str | TriggerGroup, bool]"):
        """Set the tsel state for the left and right side"""
        if not isinstance(values, dict):
            raise TypeError(f"Values must be a dict, not {type_name(values)}")
        if any(not isinstance(v, bool) for v in values.values()):
            raise TypeError("Values must all be bool")
        if any(not isinstance(k, str) for k in values.keys()):
            raise TypeError("Keys must all be str")
        for side, value in values.items():
            if side in [0, "left", "0_15", TriggerGroup.LEFT]:
                regname = "tsel_left"
            elif side in [16, "right", "16_31", TriggerGroup.RIGHT]:
                regname = "tsel_right"
            else:
                raise ValueError(f"Invalid side: {side}")
            self._write_analog_register(regname, value)

    def _set_references(
        self, values: "dict[int | str | TriggerGroup, tuple[int, int]]"
    ):
        """Update the reference voltage subrange for one side of the trigger circuit.

        Sets the VSS/VDD reference voltages in order to gain higher precision
        of the trigger thresholds around a region of interest.

        Args:
            side (str): the side of the trigger circuit; left or right.
            lower (int): the lower boundary of the subrange in counts.
            upper (int): the upper boundary of the subrange in counts.
        """
        if not isinstance(values, dict):
            raise TypeError(f"Values must be a dict, not {type_name(values)}")
        for side, (lower, upper) in values.items():
            if side in [0, "0_15", "left", TriggerGroup.CH0_15, TriggerGroup.LEFT]:
                side = "left"
            elif side in [
                16,
                "16_31",
                "right",
                TriggerGroup.CH16_31,
                TriggerGroup.RIGHT,
            ]:
                side = "right"
            else:
                raise ValueError(f"Invalid side: {side}")
            logger.debug(
                "Updating references for %s side: lower=%s, upper=%s",
                side,
                lower,
                upper,
            )
            self._validate_reference_range_or_raise(side, lower, upper)
            self._write_analog_register(f"sub_ref_neg_sb_{side}_trigger", lower)
            self._write_analog_register(f"sub_ref_pos_sb_{side}_trigger", upper)

    def _set_trigger_edges(self, channels: "dict[int | str | TriggerGroup, bool]"):
        """Set trigger edge per side, either rising=True, or rising=False

        Will only write each side once, even if multiple channels are specified.

        Args:
            channels (dict[int | str | TriggerGroup, bool]):
                keys are the sides "left" or "right".
                value can be True (rising) or false (falling).

        Raises:
            TypeError if channels is not a dict.
        """
        right = left = False
        if not isinstance(channels, dict):
            raise TypeError("channels must be a dict")
        if any(not isinstance(k, (int, str, TriggerGroup)) for k in channels.keys()):
            raise TypeError("Keys must be int or str or TriggerGroup")
        for side, rising in channels.items():
            if side in [0, "left", "0_15", TriggerGroup.LEFT] and not left:
                self.set_trigger_edge("left", rising)
                left = True
            elif side in [16, "right", "16_31", TriggerGroup.RIGHT] and not right:
                self.set_trigger_edge("right", rising)
                right = True
            if left and right:
                break

    def set_trigger_edge(self, side: "int | str | TriggerGroup", rising: bool = True):
        """Set which signal edge to trigger on.

        Shift between positive going signals (rising) and negative (falling).

        Args:
            side (int | str | TriggerGroup): The side of the trigger circuit to set.
                Can be "left", "right", 0, 16, "0_15", "16_31", TriggerGroup.LEFT, TriggerGroup.RIGHT.
            rising(bool): If true, trigger on positive going signals, else falling edge.

        Raises:
            TypeError if raises is not a bool.
        """
        self._validate_side_or_raise(side)
        if rising not in [True, False]:
            raise TypeError(f"rising must be a bool, got {rising}")
        logger.debug(
            "Setting %s trigger edge to: %s", side, "rising" if rising else "falling"
        )
        if side in [0, "left", "0_15", TriggerGroup.LEFT]:
            register = "tsgn_left"
        elif side in [16, "right", "16_31", TriggerGroup.RIGHT]:
            register = "tsgn_right"
        else:
            raise ValueError(
                f"side is not a valid value, expected 0, 16, 'left', 'right','0_15', '16_31', TriggerGroup.LEFT, TriggerGroup.RIGHT, got {side}"
            )
        self._write_analog_register(register, rising)

    def _set_trigger_thresholds(self, trigger_values: "dict[int, int] | None" = None):
        """Set the trigger values for the individual channels using the values
        stored in the board object.
        """
        trigger_values = trigger_values or self.values
        self._validate_trigger_thresholds_or_raise(trigger_values)
        self._set_tsel_enabled()
        logger.debug("Setting trigger thresholds: %s", trigger_values)
        for channel, threshold_value in trigger_values.items():
            register_name = self._trig_thresh_regname.format(channel)
            self._write_analog_register(register_name, threshold_value)

    def _set_wbiases(self):
        """Enable the biasing system if it's not already enabled"""
        # power the dacs which set Vdd and Vss
        self._write_analog_register("ref_output_bias_left", 0x3E8)
        self._write_analog_register("ref_output_bias_bias_left", 0x3E8)

        self._write_analog_register("ref_output_bias_right", 0x3E8)
        self._write_analog_register("ref_output_bias_bias_right", 0x3E8)

        self._write_analog_register("channel_wbias_source_left", 0x400)
        self._write_analog_register("channel_wbias_source_right", 0x400)

    def _set_tsel_enabled(self):
        """Set whether tsel_{l/r} is enabled based on the trigger values.

        A side is enabled if at least one trigger value is non-zero for that side.
        """
        trigger_values = self.values
        split_pos = self._first_right_channel
        left_val = [val for key, val in trigger_values.items() if key < split_pos]
        right_val = [val for key, val in trigger_values.items() if key >= split_pos]
        en_left = any(t != 0 for t in left_val)
        en_right = any(t != 0 for t in right_val)
        logger.debug("Setting tsel_left: %s", en_left)
        self.tsel = {
            "0_15": en_left,
            "16_31": en_right,
        }

    def _set_trigger_offsets(self):
        """Trigger offsets not implemented yet."""
        pass

    def _validate_trigger_thresholds_or_raise(self, trigger_values: dict[int, int]):
        """Validate the trigger values are within the range of the trigger circuit."""
        max_threshold_value = self.max_threshold
        if not isinstance(trigger_values, (dict)):
            raise TypeError(
                f"Trigger values must be list, not {type_name(trigger_values)}"
            )
        if any(not isinstance(v, int) for v in trigger_values.values()):
            raise TypeError("Trigger values must all be int")
        if any(not 0 <= x <= max_threshold_value for x in trigger_values.values()):
            raise ValueError(
                f"Trigger value must be between 0 and {max_threshold_value}"
            )

    def _validate_side_or_raise(self, side: str):
        VALID_SIDES = [
            0,
            16,
            "left",
            "right",
            "0_15",
            "16_31",
            TriggerGroup.LEFT,
            TriggerGroup.RIGHT,
        ]
        if not isinstance(side, str):
            raise TypeError(f"Side must be str, not {type_name(side)}")
        if side not in VALID_SIDES:
            raise ValueError(f"Side must be one of: {VALID_SIDES}. Got: {side}")

    def _validate_reference_dict_or_raise(self, values: dict):
        """Validate reference dict or raise an error.

        The dict must have the form:
        ```
        {
            'left': [lower, upper],
            'right': [lower, upper],
        }
        ```
        """
        if not isinstance(values, dict):
            raise TypeError(f"Reference values must be a dict, not {type_name(values)}")
        if any(not isinstance(x, (list, tuple)) for x in values.values()):
            raise TypeError("Reference value ranges must be list or tuple")
        if any(len(x) != 2 for x in values.values()):
            raise ValueError(
                "Reference value ranges must each be length 2 (lower & upper)"
            )
        for side, (lower, upper) in values.items():
            self._validate_reference_range_or_raise(side, lower, upper)

    def _validate_reference_range_or_raise(self, side: str, lower: int, upper: int):
        """Validate reference range arguments.

        Args:
            side (str): must be "left" or "right"
            lower (int): must be within bounds
            upper (int): must be within bounds
        """
        self._validate_side_or_raise(side)
        for x in (lower, upper):
            if not isinstance(x, int):
                raise TypeError(
                    f"Reference boundary must be int, not {type_name(side)}"
                )
            if not 0 <= x <= self.max_reference:
                raise ValueError(
                    f"Reference boundary is out of bounds (0-{self.max_reference}). Got: {x}"
                )

    def _get_analog_register(self, register: str) -> int:
        """Get the value of an analog register"""
        return self.board.registers["analog_registers"][register]["value"][0]
