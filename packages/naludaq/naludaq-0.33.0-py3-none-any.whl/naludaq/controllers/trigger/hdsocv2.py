"""
"""
from logging import getLogger
from naludaq.controllers.trigger.hdsoc import TriggerControllerHdsoc
from naludaq.helpers.helper_functions import type_name
from enum import Enum

logger = getLogger("naludaq.trigger_controller_hdsoc")

# {TIA_en, TIA_DC_adj[0:6], tsel, ch_en, scv_legacy, tsgn}
TSEL_BIT = 3
TSGN_BIT = 0


class TriggerGroup(Enum):
    """Used to select grouped channels for setting trigger thresholds and references."""

    CH0_15 = 0
    CH16_31 = 1
    CH32_47 = 2
    CH48_63 = 3


class TriggerControllerHdsocv2(TriggerControllerHdsoc):
    def __init__(self, board):
        super().__init__(board)

    @property
    def references(self) -> "dict[str, tuple[int, int]]":
        """Get/Set the current low/high references for the left and right side

        - nb, left: 16_31
        - nb, right: 48_63
        - sb, left: 0_15
        - sb, right: 32_47

        Returns:
            dict[str, tuple[int, int]]: A dictionary where the keys are the side
                                        and the values are tuples of low and high references.
        """

        ref0_15_low = self._get_analog_register("sub_ref_neg_0_15_trigger")
        ref0_15_high = self._get_analog_register("sub_ref_pos_0_15_trigger")
        ref16_31_low = self._get_analog_register("sub_ref_neg_16_31_trigger")
        ref16_31_high = self._get_analog_register("sub_ref_pos_16_31_trigger")
        ref32_47_low = self._get_analog_register("sub_ref_neg_32_47_trigger")
        ref32_47_high = self._get_analog_register("sub_ref_pos_32_47_trigger")
        ref48_63_low = self._get_analog_register("sub_ref_neg_48_63_trigger")
        ref48_63_high = self._get_analog_register("sub_ref_pos_48_63_trigger")

        ref = {
            "0_15": (ref0_15_low, ref0_15_high),
            "16_31": (ref16_31_low, ref16_31_high),
            "32_47": (ref32_47_low, ref32_47_high),
            "48_63": (ref48_63_low, ref48_63_high),
        }
        return ref

    @references.setter
    def references(self, values: "dict[str, tuple[int, int]]"):
        """Set the low/high references for the left and right side"""
        self._set_references(values)

    @property
    def low_references(self) -> dict[str, int]:
        """Get the current low references for the left and right side"""
        ref0_15_low = self._get_analog_register("sub_ref_neg_0_15_trigger")
        ref16_31_low = self._get_analog_register("sub_ref_neg_16_31_trigger")
        ref32_47_low = self._get_analog_register("sub_ref_neg_32_47_trigger")
        ref48_63_low = self._get_analog_register("sub_ref_neg_48_63_trigger")
        refs = {
            "0_15": ref0_15_low,
            "16_31": ref16_31_low,
            "32_47": ref32_47_low,
            "48_63": ref48_63_low,
        }
        return refs

    @low_references.setter
    def low_references(self, values: "dict[str | str, int]"):
        """Set the low references for the left and right side"""
        if not isinstance(values, dict):
            raise TypeError(f"Values must be a dict, not {type_name(values)}")
        for side, value in values.items():
            if side in [0, "0_15", TriggerGroup.CH0_15]:
                regname = "sub_ref_neg_0_15_trigger"
            elif side in [1, "16_31", TriggerGroup.CH16_31]:
                regname = "sub_ref_neg_16_31_trigger"
            elif side in [2, "32_47", TriggerGroup.CH32_47]:
                regname = "sub_ref_neg_32_47_trigger"
            elif side in [3, "48_63", TriggerGroup.CH48_63]:
                regname = "sub_ref_neg_48_63_trigger"
            else:
                raise ValueError(f"Invalid side: {side}")
            self._write_analog_register(regname, value)

    @property
    def high_references(self) -> dict[str, int]:
        """Get the current high references for the channel groups"""
        ref0_15_high = self._get_analog_register("sub_ref_pos_0_15_trigger")
        ref16_31_high = self._get_analog_register("sub_ref_pos_16_31_trigger")
        ref32_47_high = self._get_analog_register("sub_ref_pos_32_47_trigger")
        ref48_63_high = self._get_analog_register("sub_ref_pos_48_63_trigger")
        refs = {
            "0_15": ref0_15_high,
            "16_31": ref16_31_high,
            "32_47": ref32_47_high,
            "48_63": ref48_63_high,
        }
        return refs

    @high_references.setter
    def high_references(self, values: "dict[int | str, int]"):
        """Set the high references for the left and right side"""
        if not isinstance(values, dict):
            raise TypeError(f"Values must be a dict, not {type_name(values)}")
        for side, value in values.items():
            if side in [0, "0_15", TriggerGroup.CH0_15]:
                regname = "sub_ref_pos_0_15_trigger"
            elif side in [1, "16_31", TriggerGroup.CH16_31]:
                regname = "sub_ref_pos_16_31_trigger"
            elif side in [2, "32_47", TriggerGroup.CH32_47]:
                regname = "sub_ref_pos_32_47_trigger"
            elif side in [3, "48_63", TriggerGroup.CH48_63]:
                regname = "sub_ref_pos_48_63_trigger"
            else:
                raise ValueError(f"Invalid side: {side}")
            self._write_analog_register(regname, value)

    @property
    def edge(self) -> bool:
        """Get the trigger edge for all channels on the board."""
        raise NotImplementedError("Single edge is not implemented for HDSOCv2")

    @edge.setter
    def edge(self, value: bool):
        """Set the trigger edge for all channels on the board."""
        if not isinstance(value, bool):
            raise TypeError("edge must be a bool")
        self.edges = value

    @property
    def edges(self) -> "dict[int | str | TriggerGroup, bool]":
        """Get the trigger edge for all channels on the board."""
        edges = {}
        for ch in range(self.board.channels):
            reg = self._get_fwd_reg_name(ch)
            edges[ch] = bool(
                self.board.registers["analog_registers"][reg]["value"][0] & TSGN_BIT
            )
        return edges

    @edges.setter
    def edges(self, value: "dict[int | str | TriggerGroup, bool] | bool"):
        """Set the trigger edge for all channels on the board."""
        if isinstance(value, bool):
            edges = {ch: value for ch in range(self.board.channels)}
        elif isinstance(value, dict):
            edges = value
        else:
            raise TypeError("edges must be a dict or bool")
        self._set_trigger_edges(edges)

    @property
    def tsel(self) -> dict[int, bool]:
        """Get the trigger select for all channels on the board."""
        tsel = {}
        for ch in range(self.board.channels):
            reg = self._get_fwd_reg_name(ch)
            tsel[ch] = bool(
                self.board.registers["analog_registers"][reg]["value"][0] & TSEL_BIT
            )
        return tsel

    @tsel.setter
    def tsel(self, value: "bool | dict[int, bool]"):
        """Set the trigger select for all channels on the board."""
        if isinstance(value, bool):
            tsel = {ch: value for ch in range(self.board.channels)}
        elif isinstance(value, dict):
            tsel = value
        else:
            raise TypeError("channels must be a dict")

        self._update_fwd_regs(tsel, TSEL_BIT)

    def _set_references(self, values: dict[str, tuple[int, int]]):
        """Set the low/high references for the left and right side
        Args:
            values (dict[str, tuple[int, int]]): A dictionary where the keys are the side
                                                and the values are tuples of low and high references.
        Raises:
            TypeError: If the values argument is not a dictionary.
            TypeError: If the low or high reference is not an integer.
            ValueError: If the side is not valid.
        """
        if not isinstance(values, dict):
            raise TypeError("values must be a dict")
        for side, (low, high) in values.items():
            if not isinstance(low, int) or not isinstance(high, int):
                raise TypeError("Low and high references must be integers")
            if side == "0_15":
                self._write_analog_register("sub_ref_neg_0_15_trigger", low)
                self._write_analog_register("sub_ref_pos_0_15_trigger", high)
            elif side == "16_31":
                self._write_analog_register("sub_ref_neg_16_31_trigger", low)
                self._write_analog_register("sub_ref_pos_16_31_trigger", high)
            elif side == "32_47":
                self._write_analog_register("sub_ref_neg_32_47_trigger", low)
                self._write_analog_register("sub_ref_pos_32_47_trigger", high)
            elif side == "48_63":
                self._write_analog_register("sub_ref_neg_48_63_trigger", low)
                self._write_analog_register("sub_ref_pos_48_63_trigger", high)
            else:
                raise ValueError(f"Invalid side: {side}")

    def _set_tsel_enabled(self):
        """Enables TSEL (Trigger Select) for all channels on the board.

        This method creates a dictionary where each channel on the board is set to True,
        indicating that TSEL is enabled for that channel. It then calls the `enable_tsel`
        method with this dictionary to apply the settings.
        """
        channels = {i: True for i in range(self.board.channels)}
        self.tsel = channels

    def _set_trigger_edges(self, channels: dict[int, bool]):
        """Set trigger edge per channel, either rising=True, or rising=False

        Args:
            channels (dict[int, bool]): keys are channel numbers,
                                        value are True (rising)
                                        or false (falling).

        Raises:
            TypeError if channels is not a dict.
        """
        if not isinstance(channels, dict):
            raise TypeError("channels must be a dict")

        self._update_fwd_regs(channels, TSGN_BIT)

    def _set_trigger_thresholds(self, values: dict[int, int]):
        """Set the trigger values for the individual channels using the values
        stored in the board object.
        """
        values = values or self.values
        self._validate_thresholds_or_raise(values)
        self._set_tsel_enabled()
        for channel, threshold_value in values.items():
            register_name = self._trig_thresh_regname.format(channel)
            if (
                self.board.registers["analog_registers"][register_name]["value"][0]
                != threshold_value
            ):
                self._write_analog_register(register_name, threshold_value)

    def _update_fwd_regs(self, channels: dict[int, bool], bitpos: int):
        """Updates the forward registers for the specified channels.

        This method iterates over the provided channels dictionary, retrieves the
        corresponding register name for each channel, and sets a single bit at the
        specified bit position in the register based on the boolean value.

        Args:
            channels (dict[int, bool]): A dictionary where the keys are channel
                                        numbers and the values are
                                        booleans indicating the state.
            bitpos (int): The bit position to update in the register.
        """
        for ch, val in channels.items():
            reg = self._get_fwd_reg_name(ch)
            self._set_addr_single_bit(reg, bitpos, val)

    def _get_fwd_reg_name(self, ch: int) -> int:
        """Generate the forward register name for a given channel.

        Args:
            ch (int): The channel number.

        Returns:
            int: The formatted forward register name as a string.
        """
        regname = "ch_fwd_{}"
        reg = regname.format(ch)
        return reg

    def _set_addr_single_bit(self, reg: str, bitpos: int, bitval: bool):
        """Sets a single bit in a specified analog register.

        Will only send the write command if the bit value is different from the current value.

        Args:
            reg (str): The name of the register to modify.
            bitpos (int): The position of the bit to set.
            bitval (bool): The value to set the bit to (True for 1, False for 0).

        Returns:
            None
        """
        regval = self.board.registers["analog_registers"][reg]["value"]
        if isinstance(regval, list):
            regval = regval[0]
        rval = bit_replace(regval, bitpos, bitval)
        if rval != regval:
            self._write_analog_register(reg, rval)

    def _set_wbiases(self):
        """Enable the biasing system if it's not already enabled"""
        pass


def bit_replace(num: int, pos: int, val: int) -> int:
    """Replaces the bit at a specified position in an integer with a given value.

    Args:
        num (int): The original integer.
        pos (int): The position of the bit to replace (0-indexed from the right).
        val (int): The new value for the bit (0 or 1).

    Returns:
        int: The modified integer with the bit at the specified position replaced by the given value.
    """
    mask = ~(1 << pos)
    num &= mask
    num |= val << pos
    return num
