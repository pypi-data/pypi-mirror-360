"""Base class for the DAC controller, all external DAC controllers should derive from this.

The DAC controller controls the DACs external to the ASICs, different boards are equiped with
one or more DAC chips to set the input Bias on each channel.

The input bias is a DC voltage used to set the base signal at a value above 0, thus making sure
signals with negative values are still positive voltages. Think sinewave, half of the wave is under 0 which
would damage the chip.

Example:
--------

.. code-block:
    dacctrl = get_dac_controller(board)

    # set a sigle channels DAC value:
    dacctrl.set_single_dac(channel, value)

    # Set multiple channels DAC values:
    dacctrl.set_dacs(value, channels,set_mv)

"""
import abc
import logging
from typing import List

from naludaq.controllers.controller import Controller
from naludaq.helpers.exceptions import RegisterFileError

LOGGER = logging.getLogger("naludaq.ext_dac.base")
_REQUIRED_FIELDS = {  # These must be present in the register file.
    "max_mv": int,
    "max_counts": int,
    "channels": dict,
}


class BaseDACController(Controller):
    """Interface for the external/pedestals DAC.

    For the DAC interface to work the board parameters need to be loaded with
    the corresponding DAC parameters, max mV, max counts value set per channel.

    This class needs one channel value per channel in the parameter file or it
    will raise an Error.

    Attributes:
        board (naludaq.board.Board): board object with the corresponding DAC chip params.

    Functions:
        set_single_dac(channel:int, value: int) set the value for a single channel
        set_dacs(value: int, channels: list) sets the same value to multiple channels.

    Raises:
        InvalidRegisterFile is these params are not available in the board.
    """

    def __init__(self, board) -> None:
        """Base class for all DAC controllers.

        Args:
            board (Board): the board object.

        RegisterFileError if the board parameters are missing
                an `ext_dac` field or it is invalid.
        """
        super().__init__(board)
        self.board = board

    @property
    def board(self):
        """Get/Set set board to update DAC chip params.

        Raises:
            RegisterFileError if the board parameters are missing
                an `ext_dac` field or it is invalid.
        """
        return self._board

    @board.setter
    def board(self, board):
        self._validate_ext_dac_params(board.params)
        self.dac_params = board.params["ext_dac"]
        self._board = board

    def set_single_dac(self, channel: int, value: int, set_mv: bool = False):
        """Set the value of a single DAC.

        Args:
            channel(int): channel nummber to set.
            value(int): Value to set DAC to.

        Raises:
            TypeError if channel is not an int
            TypeError if value is not an int
            ValueError if either channel or value is out of bounds.
        """
        try:
            self.set_dacs(value, [channel], set_mv)
        except (TypeError, ValueError):
            raise

    def set_dacs(
        self,
        value: "int | None" = None,
        channels: "list[int] | None" = None,
        set_mv: bool = False,
    ):
        """Sets the values of the external DAC.

        If `channel` is `None`, it'll update all channels with the value given.
        If `value` is `None` it'll use whatever is stored in the board parameters for each channel.

        When changing a DAC, only the specific channels value will change,
        the other channels remain the same (unless stated otherwise).

        To turn a channel off, give it value 0.

        Args:
            value (int): value to set the DAC to. If `None`, values from
                the board object are used instead.
            channels (list): list of channels to set to this value.
            set_mv (bool): whether the value given is in mV.

        Raises:
            TypeError if channels is not a list of integer
            ValueError if channels is not within 0 <= x < < board.channels
            TypeError if the value is not an int.
            ValueError if the value is outside the range 0<=value<max_count
        """
        try:
            if channels is not None:
                self._validate_channels(channels)
            if value is not None:
                self._validate_value(value, set_mv)
        except (TypeError, ValueError):
            raise

        if set_mv:
            value = self._convert_mv2cnt(value)
        if channels is None:
            channels = list(self.board.dac_values.keys())

        original_values = self.board.params["ext_dac"][
            "channels"
        ]  # copy not always needed
        if value is not None:
            original_values = original_values.copy()
            self._set_internal_dac_values(value, channels)

        # An extra check needed in case the user modified the
        # DAC dict directly. ALL DAC values validated out of
        # an abundance of caution.
        try:
            self._validate_internal_dac_values()
            self._write_dacs(channels)
        except Exception as e:
            self.board.params["ext_dac"]["channels"] = original_values
            LOGGER.error(f"Original DAC values restored due to error: {e}")
            raise e

    def set_default_values(self):
        """Sets the dac values for all channels to default values

        Default values are pulled from board.default_params defined
        from the yml
        """
        original_values = self.board.default_params["ext_dac"]["channels"]
        self.board.params["ext_dac"]["channels"] = original_values
        self.set_dacs()

    @abc.abstractmethod
    def _write_dacs(self, channels: List[int]):
        """Implemented by the subclass to handle communication with the
        hardware needed to physically set the DACs.

        Args:
            value (int): the value to set the DACs for the specified channels to.
                If `None`, the DACs are taken from the board object.
            channels (List[int]): the channels to set the DACs for.
        """

    def _validate_ext_dac_params(self, params: dict):
        """Validates the "ext_dac" field on the board params.

        Args:
            params (dict): the params object of the board

        Raises:
            TypeError if the given `params` is not a `dict`.
            RegisterFileError if the external DAC params defined in the
                board configuration are invalid
        """
        if not isinstance(params, dict):
            raise TypeError("Params must be a dict")

        dac_params = params.get("ext_dac", None)
        if dac_params is None:
            raise RegisterFileError("Board does not have an external DAC defined")
        if not isinstance(dac_params, dict):
            raise RegisterFileError("External DAC parameters must be a dict")

        for key, value_type in _REQUIRED_FIELDS.items():
            if key not in dac_params:
                raise RegisterFileError(
                    f'Required field "{key}" is missing from external DAC parameters'
                )
            if not isinstance(dac_params[key], value_type):
                raise RegisterFileError(
                    f'Field "{key}" must be a {value_type.__name__}'
                )

        if not all(isinstance(x, int) for x in dac_params["channels"]):
            raise RegisterFileError("One or more external DAC values is not an int")

    def _validate_value(self, value: int, set_mv: bool = False):
        """Validates the value is within the valid range of counts.

        Args:
            value (int, float): integer value to validate.
                Must be an int if `set_mv` is `False`.
            set_mv (bool): whether to the value given is in mV.

        Raises:
            TypeError if the value is not an int.
            ValueError if th value is outside of the range 0<=value<max_count (12 or 16 bits)
        """
        if not isinstance(set_mv, bool):
            raise TypeError("set_mv must be a bool")
        if not set_mv and not isinstance(value, int):
            raise TypeError("Value in counts must be an int")
        if set_mv and not isinstance(value, (int, float)):
            raise TypeError("Value in mV must be numeric")

        max_value = self.dac_params["max_counts"]
        min_value = self.dac_params.get("min_counts", 0)
        if set_mv:
            max_value = self.dac_params["max_mv"]
            min_value = self.dac_params.get("min_mv", 0)

        if not (min_value <= value <= max_value):
            raise ValueError(
                f"Value is outside range. {min_value} <= value <= {max_value}"
            )

    def _set_internal_dac_values(self, value: int, channels: List[int]):
        """Update the board.dac_values for the selected channels

        Args:
            value (int): the value to set the DACs to
            channels (List[int]): the channels to set the DAC value for.

        Raises:
            TypeError if the arguments are an invalid type.
            ValueError if the value or any channel is out of bounds.
        """
        try:
            self._validate_channels(channels)
            self._validate_value(value)
        except (TypeError, ValueError):
            raise
        for chan in channels:
            self.board.dac_values[chan] = value

    def _validate_internal_dac_values(self):
        """Ensures that all DAC values held in the board object
        are valid. This is important because the user is free
        to modify those values at will, even setting them to
        potentially dangerous values.

        Raises:
            ValueError if _any_ of the DAC values held in the board
                object are out of bounds.
        """
        max_value = self.dac_params["max_counts"]
        for channel, dac_value in self.board.params["ext_dac"]["channels"].items():
            if not 0 <= dac_value <= max_value:
                raise ValueError(
                    f"Cannot set DAC value. Value {dac_value} "
                    f"for channel {channel} exceeds the maximum value"
                )

    def _validate_channels(self, channels: "list[int]"):
        """Make sure the channels are only repeated once and are within range.

        Args:
            channels(list): list of channels to validate

        Raises:
            TypeError if channels is not a list of integers
            ValueError if channels is not within 0 <= x < board.channels
        """
        if not isinstance(channels, list):
            raise TypeError("Channels must be a list of int.")
        if not all(isinstance(chan, int) for chan in channels):
            raise TypeError("Channels must be a list of int.")
        if not all(c in self.board.dac_values.keys() for c in channels):
            raise ValueError("Selected channel numbers are invalid for this board")
        if len(channels) != len(set(channels)):
            raise ValueError("Duplicate channels not allowed")

    def _convert_mv2cnt(self, value):
        """Takes a value in mV and converts it to digital counts based on board model."""
        cnt_hi = self.dac_params["max_counts"]
        cnt_lo = self.dac_params.get("min_counts", 0)
        vref_hi = self.dac_params["max_mv"]
        vref_lo = self.dac_params.get("min_mv", 0)

        cnt = round(value * (cnt_hi - cnt_lo) / (vref_hi - vref_lo))

        return cnt
