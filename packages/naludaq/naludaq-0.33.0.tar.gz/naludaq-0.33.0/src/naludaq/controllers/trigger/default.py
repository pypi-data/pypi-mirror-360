"""Trigger controller.

The trigger controller is an interface to access and operate the
trigger functionality in the Nalu hardware.
The trigger is active when the chip is in the trigger mode,
by setting BoardController(board).start_readout(*args) where trig
is set to "ext" or "imm".

The trigger is operated by two variables, offset and value.
The value is the ADC threshold value of the trigger.
The offset is an offset from the 0, by setting offset it's possible to
fine-tune the trigger since the needed value is now smaller.

Disable the trigger by setting the value to 0.

Example:

    trig_vals = [1000, 0, 1000, 0]
    board.trigger.values = trig_vals

AUTHOR:
Marcus Luck <marcus@naluscientific.com>

"""
import logging
from enum import Enum

from naludaq.communication import AnalogRegisters, ControlRegisters, DigitalRegisters
from naludaq.controllers.controller import Controller
from naludaq.helpers.semiton import SemitonABC

LOGGER = logging.getLogger(__name__)  # pylint ignore=invalid-name


class TriggerEdge(Enum):
    """Enum for the trigger edge.

    The trigger edge can be set to rising or falling.
    """

    RISING = True
    FALLING = False


class BaseTriggerController(Controller, SemitonABC):
    def __init__(self, board):
        super().__init__(board)
        self.num_banks = 1
        triggers_available = self.params.get("triggers_available", self.board.channels)
        self._trigger_offsets: dict[int, int] = {
            ch: 0 for ch in range(triggers_available)
        }
        self._trigger_values: dict[int, int] = {
            ch: 0 for ch in range(triggers_available)
        }
        edges_available: int = self.params.get("edges_available", 1)
        self._edges: dict[int, TriggerEdge] = {
            ch: TriggerEdge.RISING for ch in range(edges_available)
        }
        # init wbias
        if self.params.get("wbias", None) is None:
            self.params["wbias"] = {ch: 0 for ch in range(self._num_trig_chans)}
        elif isinstance(self.params.get("wbias", None), int):
            self.params["wbias"] = {
                ch: self.params["wbias"] for ch in range(self._num_trig_chans)
            }
        elif isinstance(self.params.get("wbias", None), list):
            self.params["wbias"] = {
                ch: self.params["wbias"][ch] or 0 for ch in range(self._num_trig_chans)
            }
        elif isinstance(self.params.get("wbias", None), dict):
            self.params["wbias"] = {
                ch: self.params["wbias"].get(ch, 0)
                for ch in range(self._num_trig_chans)
            }
        else:
            self.params["wbias"] = {ch: 0 for ch in range(self._num_trig_chans)}
        self._wbias_values: dict[int, int] = {ch: 0 for ch in range(triggers_available)}

    @property
    def bank_size(self) -> int:
        return self.board.channels // self.num_banks

    @property
    def params(self):
        return self.board.params.get("trigger", {})

    @property
    def _num_trig_chans(self):
        return self.board.channels

    @property
    def _max_thresholds(self):
        """Get the maximum threshold value for the board.

        Returns:
            Maximum threshold value.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def _min_thresholds(self):
        """Get the minimum threshold value for the board.

        Returns:
            Minimum threshold value.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def references(self) -> "dict[int | str, int]":
        """Get the reference channels for the board.

        Returns:
            Dict of reference channels.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @references.setter
    def references(self, value: "dict[int | str, int]"):
        """Set the reference channels for the board.

        Args:
            value: Dict of reference channels.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def low_references(self) -> "dict[int | str, int]":
        """Get the reference channels for the board.

        Returns:
            Dict of reference channels.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @low_references.setter
    def low_references(self, value: "dict[int | str, int]"):
        """Set the reference channels for the board.

        Args:
            value: Dict of reference channels.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def high_references(self) -> "dict[int | str, int]":
        """Get the reference channels for the board.

        Returns:
            Dict of reference channels.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @high_references.setter
    def high_references(self, value: "dict[int | str, int]"):
        """Set the reference channels for the board.

        Args:
            value: Dict of reference channels.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def wbias(self):
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @wbias.setter
    def wbias(self, value):
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def offsets(self) -> dict[int, int]:
        """Get the trigger offsets for the board.

        Returns:
            List of trigger offsets.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @offsets.setter
    def offsets(self, value: "dict[int, int] | int | list[int] | None"):
        """Set the trigger offsets for the board.

        Args:
            value: List of trigger offsets.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def values(self) -> dict[int, int]:
        """Get the trigger values for the board.

        Returns:
            List of trigger values.
        """
        return self.thresholds()

    @values.setter
    def values(self, value: "dict[int, int] | int | list[int] | None"):
        self.thresholds = value

    @property
    def thresholds(self) -> dict[int, int]:
        """Get the trigger thresholds for the board.

        Returns:
            List of trigger thresholds.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @thresholds.setter
    def thresholds(self, value: "dict[int, int] | int | None"):
        """Set the trigger thresholds for the board.

        Args:
            value: List of trigger thresholds.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def enabled(self) -> dict[int, bool]:
        """Get the trigger enabled per channel.

        Returns:
            List of trigger enabled.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @enabled.setter
    def enabled(self, value: dict[int, bool]):
        """Set the trigger enabled per channel.

        Args:
            value: List of trigger enabled.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def edge(self) -> "bool | TriggerEdge":
        """Get the trigger edge for the board, opnly available for models with one edge control.

        Returns:
            Trigger edge.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @edge.setter
    def edge(self, value: "bool | TriggerEdge"):
        """Set the trigger edge for the board, opnly available for some models.

        Will set all edges to the same value if board supports multiple channels.

        Args:
            value: Trigger edge.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def edges(self) -> "dict[int | str, bool | TriggerEdge]":
        """Get the trigger edges for the board.

        Returns:
            List of trigger edges.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @edges.setter
    def edges(self, value: "dict[int | str, bool | TriggerEdge]"):
        """Set the trigger edges for the board.

        Args:
            value: List of trigger edges.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    def write_triggers(
        self, trigger_values: "dict[int, int] | int | list[int] | None" = None
    ):
        """Write the trigger values to the hardware.

        This writes the current set triggers to the hardware.
        By setting the trigger_offsets or the trigger_values
        this function is called automatically and the hardware is updated.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @property
    def tsel(self) -> bool:
        """Get the trigger select for the board.

        Returns:
            Trigger select.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    @tsel.setter
    def tsel(self, value: dict[int, bool]):
        """Set the trigger select for the board.

        Args:
            value: Trigger select.
        """
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )


class TriggerController(BaseTriggerController):
    """Primary tool to setup the triggers for an aquisition.

    Attributes:
        board: The board to update the triggers on.
        offsets: Offsets as a list, one val per channel.
        values: The trigger values as a list, one val per channel.

    Functions:
        write_triggers: writes all the trigger values to the physical hardware.
    """

    @property
    def _max_thresholds(self):
        """Get the maximum threshold value for the board.

        Returns:
            Maximum threshold value.
        """
        return self.params.get("max_val", 4095)

    @property
    def _min_thresholds(self):
        """Get the minimum threshold value for the board.

        Returns:
            Minimum threshold value.
        """
        return self.params.get("min_val", 0)

    @property
    def wbias(self) -> dict[int, int]:
        """Get the default wbias for the ASIC."""
        return self.params["wbias"]

    @wbias.setter
    def wbias(self, value: "dict[int, int] | list[int] | int"):
        """Set the wbias for the ASIC.

        The wbias controls the width of the trigger pulse.

        Args:
            value: The wbias value to set.
        """
        if isinstance(value, int):
            self.params["wbias"] = {ch: value for ch in range(self._num_trig_chans)}
        elif isinstance(value, list) and len(value) == self._num_trig_chans:
            self.params["wbias"] = {ch: value for ch, value in enumerate(value)}
        elif isinstance(value, dict) and len(value) == self._num_trig_chans:
            self.params["wbias"] = value
        elif isinstance(value, list) and len(value) != self._num_trig_chans:
            raise ValueError("wbias lists must of length %s", self._num_trig_chans)
        else:
            raise TypeError("Voltage offset must be a single number or a list.")

        self._set_wbiases()

    @property
    def edge(self) -> bool:
        """Get set the trigger edge for all channels."""
        return self._edges.get(0, TriggerEdge.RISING).value

    @edge.setter
    def edge(self, rising: "bool | TriggerEdge"):
        if isinstance(rising, bool):
            rval = TriggerEdge(rising)
        elif isinstance(rising, TriggerEdge):
            rval = rising
        else:
            raise TypeError(
                "rising must be a bool or TriggerEdge, got %s", type(rising)
            )
        self.set_trigger_edge(rval)

    @property
    def offsets(self):
        """Set voltage offset for the trigger.

        Set the trigger offset values, can set one value for all channels or
        a specific value for each channel.

        Updates the value on the hardware if connected.

        Args:
            offset(int): voltage offset for all channels.
            offset(list): voltage offset for the individual channels.

        Returns:
            List of current voltage offsets.

        Raises:
            TypeError if voltage is not a list of length num_chans or a single number.
        """
        return self._trigger_offsets

    @offsets.setter
    def offsets(self, value: "dict[int, int] | list[int] | int") -> None:
        if isinstance(value, int):
            self._trigger_offsets = {ch: value for ch in range(self._num_trig_chans)}

        elif isinstance(value, list):
            if len(value) == self._num_trig_chans:
                self._trigger_offsets = {ch: val for ch, val in enumerate(value)}
            else:
                raise ValueError(
                    f"Trigger offsets must be a list of length {self._num_trig_chans}"
                )
        elif isinstance(value, dict):
            for k, v in value.items():
                self._trigger_offsets[k] = v
        else:
            raise TypeError("Voltage offset must be a single number or a list.")

        self.write_triggers()

    @property
    def values(self) -> dict[int, int]:
        """Trigger threshold for the board.

        Set the trigger threshold values, can set one value for all channels or
        a specific value for each channel.

        Updates the value on the hardware if connected.

        Args:
            trigger_val (list or int): Threshold values for triggers per channel.
                Can take an single number for all channels or one value per channel.

        Returns:
            List of current values for the triggers.

        Raises:
            TypeError if value or key isa of the wrong type.
            ValueError if the list is the wrong length
            ValueError if the value is out of bounds.
            ValueError if the key is out of bounds.
        """
        return self._trigger_values

    @values.setter
    def values(self, trigger_val: "int | dict[int, int] | list[int] | None") -> None:
        conv_val = self._convert_to_dict_or_raise(trigger_val)
        self._validate_thresholds_or_raise(conv_val)

        for k, v in conv_val.items():
            self._trigger_values[k] = v

        self.write_triggers()

    def _convert_to_dict_or_raise(self, value) -> "dict[int, int | bool]":
        """Converts int | dict[int, int|bool] | list[int|bool] to dict[int, int|bool] or raises an error."""
        if isinstance(value, bool):
            conv_val = {ch: value for ch in range(self._num_trig_chans)}
        if isinstance(value, int):
            conv_val = {ch: value for ch in range(self._num_trig_chans)}
        elif isinstance(value, list):
            if len(value) != self._num_trig_chans:
                raise ValueError(
                    f"Trigger values must be a list of length {self._num_trig_chans}"
                )
            conv_val = {ch: val for ch, val in enumerate(value)}
        elif isinstance(value, dict):
            conv_val = value
        else:
            raise TypeError(
                "Trigger values must be: int | bool | dict[int, int|bool] | list[int|bool]"
            )
        return conv_val

    def _validate_thresholds_or_raise(self, value: dict[int, int]) -> None:
        """Validate the trigger thresholds or raise an error."""
        for k, v in value.items():
            if not isinstance(k, int):
                raise KeyError("Key must be an integer")
            if not isinstance(v, int):
                raise TypeError("Values must be an integer")
            if not self._min_thresholds <= v <= self._max_thresholds:
                raise ValueError(
                    f"Value {v} is out of bounds for range {self._min_thresholds} - {self._max_thresholds}"
                )
            if k not in range(self._num_trig_chans):
                raise ValueError(
                    f"Channel {k} is not in range 0:{self._num_trig_chans}"
                )

    def write_triggers(
        self, trigger_values: "dict[int, int] | int | list[int] | None" = None
    ):
        """Write the trigger values to the hardware.

        This writes the current set triggers to the hardware.
        By setting the trigger_offsets or the trigger_values
        this function is called automatically and the hardware is updated.
        """
        self._set_trigger_thresholds(trigger_values)
        self._set_wbiases()
        self._set_trigger_offsets()

        return True

    def _set_trigger_thresholds(self, trigger_values: "dict[int, int] | None" = None):
        """Sets the trigger values and send to hardware.

        Take the trigger values from the board
        """

        trigger_values = trigger_values or self.values
        channels = self.board.channels

        reg = "trigger_threshold_{:02}"
        if self.board.model == "siread":
            reg = "thresh_{:02}"

        for chan in range(channels):
            register = reg.format(chan)
            tval = trigger_values.get(chan, 0)
            self._write_analog_register(register, tval)

    def _set_wbiases(self):
        previous_wbias = self._wbias_values.copy()

        for index in range(self.bank_size):
            wbias_val = 0
            if any(
                x > 0
                for k, x in self.values.items()
                if k
                in range(
                    index * self.num_banks, index * self.num_banks + self.num_banks
                )
            ):
                wbias_val = self.wbias[index]

            register = self._get_wbias_reg_name(index)

            if (
                previous_wbias.get(index, -1) != wbias_val
            ):  # only write if the value has changed
                self._wbias_values[index] = wbias_val
                self._write_analog_register(register, self.wbias[index])

    def _get_wbias_reg_name(self, index):
        return f"wbias_{index:02}"

    def _set_trigger_offsets(self):
        vofs = self.offsets

        channels = self.board.channels
        areg = self.board.registers.get("analog_registers", {})
        if areg.get("offset_00", None) is not None:
            for index in range(channels // self.num_banks):
                register = "offset_" + str(index).zfill(2)
                self._write_analog_register(register, int(vofs[index]))

    def set_trigger_edge(self, rising: "bool | TriggerEdge" = True):
        """Set which signal edge to trigger on.

        Shift between positive going signals (rising) and negative (falling).

        Args:
            rising(bool): If true, trigger on positive going signals, else falling edge.

        Raises:
            TypeError if raises is not a bool.
        """
        if isinstance(rising, bool):
            rising = TriggerEdge(rising)
        if not isinstance(rising, TriggerEdge):
            raise TypeError("rising must be a bool, got %s", type(rising))
        self._edges[0] = rising
        self._write_analog_register("sgn", rising.value)

    def set_trigger_edges(self):
        """Set the trigger edges for individual channels."""
        raise NotImplementedError(
            f"This feature is not available for {self.board.model}"
        )

    def _write_analog_register(
        self, register, value, chips: "int | list[int] | None" = None
    ):
        """wrapper for the Analog register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        AnalogRegisters(self.board, chips).write(register, value)

    def _write_control_register(self, register, value):
        """wrapper for the Control register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        ControlRegisters(self.board).write(register, value)

    def _write_digital_register(
        self, register, value, chips: "int | list[int] | None" = None
    ):
        """wrapper for the Digital register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        DigitalRegisters(self.board, chips).write(register, value)
