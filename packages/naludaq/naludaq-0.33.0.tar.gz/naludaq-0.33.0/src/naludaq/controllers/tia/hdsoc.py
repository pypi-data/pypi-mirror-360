import logging
from typing import List, Tuple

from naludaq.communication import AnalogRegisters
from naludaq.helpers.exceptions import DACError

from .base import BaseTIAController

LOGGER = logging.getLogger("naludaq.tia_controller_hdsoc")


class HdsocTIAController(BaseTIAController):
    def __init__(self, board, precision: float = 3.0):
        """Controller for the TIA on the HDSoC board.

        Sets the TIA DAC using dynamic precision. Upper/lower reference voltages
        are calculated to maximize the precision of the values set. This means that
        setting the TIA DACs to a wide range of values results in a lower precision,
        hence the minimum "precision" argument. Therefore the best results are obtained
        when the DAC values for all channels are relatively close, or ideally,
        the same value.

        Args:
            board (Board): the board object.
            precision (float): the minimum level of precision allowed. Roughly the
                maximum amount the given DAC values and the actual DAC values may
                differ by.
        """
        super().__init__(board)
        self.precision = precision
        self._valid_sides = ["left", "right"]

        params = self.board.params.get("tia_dac", {})
        self.lower_limit = params.get("min_vref", 0)
        self.upper_limit = params.get("max_vref", 2500)
        self._interval = self.upper_limit - self.lower_limit
        self._steps = 2 ** params.get("val_bits", 8) - 1
        self._num_subranges = 2 ** params.get("ref_bits", 4) - 1
        self._ref_table = {
            i: int((self.upper_limit - self.lower_limit + 1) / self._num_subranges * i)
            for i in range(self._num_subranges + 1)
        }

    @property
    def lower_limit(self) -> int:
        """Get the lower value limit"""
        return self._lower_limit

    @lower_limit.setter
    def lower_limit(self, value: int):
        if not isinstance(value, int):
            raise TypeError("lower_limit must be an int")
        if (
            not self.board.params.get("min_vref", 0)
            <= value
            <= self.board.params.get("max_vref", 2500)
        ):
            raise ValueError("Lower limit must be min_vref < value < max_vref")
        self._lower_limit = value

    @property
    def upper_limit(self) -> int:
        """Get the upper value limit"""
        return self._upper_limit

    @upper_limit.setter
    def upper_limit(self, value: int):
        if not isinstance(value, int):
            raise TypeError("lower_limit must be an int")
        if (
            not self.board.params.get("min_vref", 0)
            <= value
            <= self.board.params.get("max_vref", 2500)
        ):
            raise ValueError("Lower limit must be min_vref < value < max_vref")
        self._upper_limit = value

    @property
    def precision(self) -> float:
        """Get/set the minimum precision.

        Raises:
            TypeError if not set to a numeric value.
            ValueError if the value is not positive.
        """
        return self._precision

    @precision.setter
    def precision(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("Precision must be numeric")
        if value <= 0:
            raise ValueError("Precision must be a positive number")
        self._precision = value

    def set_enabled_sides(self, sides: "str | list[str]"):
        """Sets which TIAs are enabled.

        **Important:** the external DAC must be disabled in order
        to enable either of the TIAs.

        Args:
            sides (str | List[str]): a list of sides to enable, or a str
                for a single side. Sides must be "left" or "right" (case sensitive).

        Raises:
            TypeError if an invalid type is given.
            ValueError if the sides are not "left" or "right"
            DACError if the external DAC is not disabled.
        """
        sides = list(set(sides)) if isinstance(sides, list) else [sides]
        if not all(isinstance(x, str) for x in sides):
            raise TypeError('Sides must be strings "left" or "right"')
        if not all(x in ["left", "right"] for x in sides):
            raise ValueError('Side must be "left" or "right"')
        if len(sides) > 0 and self._is_ext_dac_enabled():
            raise DACError("External DAC must be disabled to use the TIA")

        for side in self._valid_sides:
            enabled = side in sides
            self._write_analog_register(f"ntia_{side}", not enabled)

    def set_dac_values(self, values: list[int]):
        """Sets the TIA DAC values for all channels.

        Writes the DAC values with dynamic precision, meaning that
        what you get isn't necessarily what you requested, up to
        a certain tolerance level. This function maximizes the
        level of precision you get, but the precision quickly drops
        as the dac values become more spread out. See the class
        docstring for more information.

        Args:
            values (List[int]): the TIA DAC values. Bounds: lower limit (in mV) to upper limit (in mV)

        Raises:
            TypeError if `values` is not a list of ints.
            ValueError if one or more values is out of bounds.
        """
        self._validate_values(values)

        min_dac, max_dac = min(values), max(values)
        low_ref, high_ref = self._get_references(min_dac, max_dac)
        low_vref = self._ref_table[low_ref]
        high_vref = self._ref_table[high_ref]
        high_vref = min(high_vref, self._upper_limit)

        actual_precision = self._calculate_precision(low_vref, high_vref)
        if self.precision < actual_precision:
            raise ValueError(
                f"Cannot set TIA DAC values: {min_dac} and {max_dac} are too far apart. "
                f"The precision ({actual_precision} mV) is lower than the minimum allowed "
                f"({self.precision} mV)"
            )

        self._set_references(low_ref, high_ref)
        self._set_tia_dac_values(values, low_vref, high_vref)

    def _get_references(self, lower_limit: int, upper_limit: int) -> Tuple[int, int]:
        """Return the 4-bit reference value for upper and lower trigger reference voltages.

        Args:
            lower_limit(int): Lowest trigger value
            upper_limit(int): Highest trigger value

        Returns:
            A tuple of (low_vref, high_vref)

        Raises:
            TypeError if the lower/upper limits are not an int
            ValueError if one or more values is out of bounds, or the
                minimum exceeds the maximum.
        """
        self._validate_bounds(
            lower_limit, upper_limit, self._lower_limit, self._upper_limit
        )
        low_ref = int(divmod(lower_limit, self._interval / self._num_subranges)[0])
        high_ref = low_ref + 1  # Upper reference above the value

        # Sanity checks. Refs can't be equal, so we need to slide one of them up/down
        # Only equal when hitting the top of the range.
        high_ref = min(high_ref, self._num_subranges)
        if low_ref == high_ref:
            low_ref -= 1
        return low_ref, high_ref

    def _set_references(self, min_vref: int, max_vref: int):
        """Set the Vdd and Vss references for both east and west side.

        Args:
            min_vref(int): the lower value
            max_vref(int): the upper value

        Raises:
            TypeError if the min/max refs are not ints
            ValueError if one or more arguments is out of bounds, or if
                the minimum exceeds the maximum.
        """
        self._validate_bounds(min_vref, max_vref, 0, self._num_subranges)
        if min_vref == max_vref:
            raise ValueError("Minimum and maximum references cannot be the same")
        self._write_analog_register("sub_ref_neg_sb_left_tia", min_vref)
        self._write_analog_register("sub_ref_neg_sb_right_tia", min_vref)
        self._write_analog_register("sub_ref_pos_sb_left_tia", max_vref)
        self._write_analog_register("sub_ref_pos_sb_right_tia", max_vref)

    def _set_tia_dac_values(self, values: List[int], low_vref: int, high_vref: int):
        """Writes the corrected DAC values to the corresponding registers.

        Args:
            values (List[int]): the list of values for each channel.
            low_vref (int): the lower vref.
            high_vref (int): the higher vref.

        Raises:
            TypeError if the values are not a List[int] or the low/high refs
                are not ints.
            ValueError if any values are out of bounds, or if the low reference
                exceeds the high reference.
        """
        self._validate_values(values)
        self._validate_bounds(low_vref, high_vref, self._lower_limit, self._upper_limit)
        step_size = (high_vref - low_vref) / self._steps
        for channel, value in enumerate(values):
            corrected_value = round(max(value - low_vref, 0) / step_size)
            self._write_analog_register(f"tia_dac_{channel}", corrected_value)

    def _is_ext_dac_enabled(self) -> bool:
        """Checks if any of the external DACs are enabled for any channels."""
        return any(x != "hi-z" for x in self.board.dac_values.values())

    def _calculate_precision(self, low_vref: float, high_vref: float):
        """Calculates the highest level of precision we can get
        with the given reference voltages.

        Args:
            low_vref (float): the lower vref
            high_vref (float): the higher vref

        Returns:
            The precision
        """
        return (high_vref - low_vref) / self._steps

    def _validate_values(self, values):
        """Validates a value expected to be a valid list of ints.

        Args:
            values: the values to check

        Raises:
            TypeError if the argument is not a List[int]
            ValueError if the list has the wrong length or
                any values are out of bounds.
        """
        if not isinstance(values, list):
            raise TypeError("Values must be a List[int]")
        if not len(values) == self._board.channels:
            raise ValueError(
                f"Values must be an array of length {self._board.channels}"
            )
        if not all(isinstance(x, int) for x in values):
            raise TypeError("Values must be a List[int]")
        if not all(self._lower_limit <= x <= self._upper_limit for x in values):
            raise ValueError("One or more values is out of bounds.")

    def _validate_bounds(self, given_low, given_high, min, max):
        """Validates the low and high bounds.

        Args:
            given_low (int): the given lower bound
            given_high (int): the given upper bound
            min (int): minimum allowed value
            max (int): maximum allowed value

        Raises:
            TypeError if either argument is not an int
            ValueError if either vref is out of bounds,
                or if the low vref exceeds the high vref.
        """
        if not isinstance(given_low, int):
            raise TypeError("low_vref must be an int")
        elif not isinstance(given_high, int):
            raise TypeError("high_vref must be an int")
        elif not min <= given_low <= max:
            raise ValueError("low_vref is out of bounds")
        elif not min <= given_high <= max:
            raise ValueError("high_vref is out of bounds")

    def _write_analog_register(self, register: str, value: int):
        """wrapper for the Analog register coms module.

        Args:
            register (str): name of the register to update.
            value (int): The register value to set.

        Raises:
            ValueError: if the value cannot be written
            TypeError: if the register/value are of incorrect types.
        """
        AnalogRegisters(self.board).write(register, value)
