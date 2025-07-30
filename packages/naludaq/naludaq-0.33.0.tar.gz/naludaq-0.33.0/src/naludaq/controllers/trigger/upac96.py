"""
"""
import logging
from collections import defaultdict

from naludaq.communication import DigitalRegisters
from naludaq.helpers.exceptions import InvalidTriggerMaskError
from naludaq.helpers.helper_functions import type_name

from .default import TriggerController

LOGGER = logging.getLogger("naludaq.trigger_controller_upac96")


class TriggerControllerUpac96(TriggerController):
    """TriggerController for UPAC96.

    Based on the default Controller

    """

    def __init__(self, board):
        super().__init__(board)
        self._num_channels = board.params.get("channels", 96)
        self._num_chips = board.params.get("num_chips", 6)
        self._channels_per_chip = self._num_channels // self._num_chips

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
            TypeError if not a List[int].
            ValueError if the list is the wrong length
        """
        return self._trigger_values

    @values.setter
    def values(self, trigger_values: "int | list[int] | int") -> None:
        trigger_values = self._convert_trigger_values(trigger_values)
        self.write_triggers(trigger_values=trigger_values)
        self._trigger_values = {c: v for c, v in trigger_values.items()}

    @property
    def enable_trigger_out(self):
        return self.board.registers["control_registers"].get(
            "coincidence_trigger_select", False
        )

    @enable_trigger_out.setter
    def enable_trigger_out(self, value):
        """enable trigger out, enables the trigger output on the board.

        Args:
            value (bool): True for box checked False for box not checked
        Error:
        Raises TypeError if value is not bool
        """
        self._validate_enable_trig_out(value)
        LOGGER.debug("Enable trigger out %s", value)
        self._write_control_register("coincidence_trigger_select", value)

    def get_channel_trigger_mask(self) -> list[int]:
        """Gets the mask for self triggering on individual channels.

        Returns:
            list: a list of enabled channels
        """
        trigger_mask = self.board.params.get("trigger", {}).get("enabled_channels", [])
        return trigger_mask

    def set_channel_trigger_mask(self, channels: list):
        """Sets the mask for self triggering on individual channels.

        The channels which are triggered on will be the ones contained in the list,
        and no other channels will be triggered on.

        Internally this goes chip-by-chip and writes the triggerchannelmask_{lo/hi}
        registers, which control which channels are enabled for self triggering. Any
        chips which have no enabled channels are disabled in the chip trigger mask.

        Args
            channels (list): a list of enabled channels

        Raises:
            TypeError if the given list is not actually a list
            InvalidTriggerMaskError if the list supplied is the wrong length
                or contains invalid elements
        """
        self._validate_channel_list_or_raise(channels)
        for chip in range(self._num_chips):
            chip_channels = self._filter_channels_for_chip(channels, chip)
            trigmask = self._create_trigger_mask(chip_channels)
            self._write_digital_register(
                "triggerchannelmask_lo", trigmask & 0xFF, chips=chip
            )
            self._write_digital_register(
                "triggerchannelmask_hi", trigmask >> 8, chips=chip
            )

        # coincidence trigger on chips without any enabled channels doesn't work
        chip_mask = self._make_chip_mask_from_channel_mask(channels)
        self.set_chip_trigger_mask(chip_mask)
        self.board.params.get("trigger", {})["enabled_channels"] = channels

    def set_single_channel_trigger_mask(self, channel: int):
        """Sets the mask for self triggering on a single channel.

        Args:
            channel (int): the channel to trigger on

        Raises:
            TypeError if the given channel is not an int
            InvalidTriggerMaskError if the channel is out of bounds
        """
        self._validate_channel_list_or_raise([channel])

        self.set_channel_trigger_mask([channel])

    def write_triggers(
        self, trigger_values: "dict[int, int] | int | list[int] | None" = None
    ):
        """Write the trigger values to the hardware.

        This writes the current set triggers to the hardware.
        By setting the offsets or the values
        this function is called automatically and the hardware is updated.

        Reimplemented to disable setting wbias/offsets.
        """
        trigger_val = self._convert_trigger_values(trigger_values)
        self._set_trigger_thresholds(trigger_values=trigger_val)

    def _convert_trigger_values(
        self, trigger_values: "int | dict[int, int] | list[int]"
    ) -> dict[int, int]:
        """Convert trigger values to a dict[int, int].

        Args:
            trigger_values: the trigger values to convert

        Returns:
            dict[int, int]: the converted trigger values
        """
        if isinstance(trigger_values, int):
            trigger_val = {c: trigger_values for c in range(self.board.channels)}
        elif isinstance(trigger_values, dict):
            trigger_val = trigger_values
        elif isinstance(trigger_values, list):
            trigger_val = {c: v for c, v in enumerate(trigger_values)}
        else:
            raise TypeError("Trigger values must be a list of integers.")
        return trigger_val

    def compare_channels(self, channels: list[int], prev_channels: list[int]) -> dict:
        """Compare two sets of channels and return the differences.

        Args:
            channels:
            prev_channels:

        Channels to deactivate: present in old but not in new
        Channels to enable: present in new but not in old
        Channels to not touch: present in both old and new
        """
        new = set(channels)
        old = set(prev_channels)
        deactivate = list(old - new)
        enable = list(new - old)
        not_touch = list(new & old)

        return {"deactivate": deactivate, "enable": enable, "leave": not_touch}

    def compare_values(
        self, channels: dict[int, int], prev_channels: dict[int, int]
    ) -> dict[int, int]:
        """Compares the values and creates a new dict containing the channels, values that needs a change.

        Args:
            channels (int): new set of channels to compare against
            prev_channels (int): previous programmed channels

        Returns:
            dict[int, int] of the channels, values that needs to be changed.
        """
        all_chans = set(channels.keys())
        all_chans.update(set(prev_channels.keys()))
        output = {}
        for key in all_chans:
            newval = channels.get(key, None)
            oldval = prev_channels.get(key, None)
            if newval is None:
                pass
            elif oldval != newval:
                output[key] = newval
        return output

    def _make_chip_mask_from_channel_mask(self, channels: list[int]) -> list[int]:
        """Creates a chip trigger mask from the given channel trigger mask.

        Args:
            channels (list[int]): a list of channels to be triggered on

        Returns:
            list[int]: the corresponding list of channels to trigger on
        """
        chip_mask = []
        for chip in range(self._num_chips):
            chip_channels = self._filter_channels_for_chip(channels, chip)
            if len(chip_channels) != 0:
                chip_mask.append(chip)
        return chip_mask

    def _create_trigger_mask(self, chip_channels: list[int]) -> int:
        """Creates a trigger mask for the given channels (single chip only).

        Args:
            chip_channels (list): a list of chip channels to trigger on

        Returns:
            int: the trigger mask for the given channels
        """
        trigmask = sum(1 << (c % self._channels_per_chip) for c in chip_channels)
        trigmask ^= 0xFFFF  # the mask registers are negative logic
        return trigmask

    def _set_trigger_thresholds(
        self, trigger_values: "dict[int, int] | None" = None
    ) -> None:
        """Sets the trigger thresholds from board.trigger_values for all channels"""
        if trigger_values is None:
            trigger_val = self.values
        else:
            self._validate_trigger_dict_or_raise(trigger_values)
            prev_channels = self.values
            trigger_val = self.compare_values(trigger_values, prev_channels)

        threshold_groups = self._group_by_chips(trigger_val)
        for chip, threshold_pair in threshold_groups.items():
            self._write_threshold_pairs(threshold_pair, chip)
        self._reset_writemask()

    def _write_threshold_pairs(self, threshold_pair: dict[int, list[int]], chip: int):
        """Writes the threshold for the given pairs of threshold values and channels.

        Args:
            threshold_pair (dict[int, list[int]]): a dict mapping channels to threshold values.
        """
        for threshold, channels in threshold_pair.items():
            writemask = sum(
                1 << channel % self._channels_per_chip for channel in channels
            )
            self._write_digital_register("writemask_l", writemask & 0xFF, chips=chip)
            self._write_digital_register("writemask_r", writemask >> 8, chips=chip)
            self._write_analog_register("trgthresh", threshold, chips=chip)

    def get_coincidence_trigger_enabled(self) -> "dict[int, bool] | None":
        """Get whether the coincidence trigger is enabled for each chip.

        Returns:
            dict: a dict with chip num (int) as a key and
                coincidence enable as the value (bool)
        """
        return self.board.params.get("trigger", {}).get(
            "coincidence_enabled", {c: False for c in range(self._num_chips)}
        )

    def set_coincidence_trigger_enabled(self, chips: dict[int, bool]):
        """Sets whether the coincidence trigger is enabled for the given chips.

        The coincidence trigger performs "AND"-like logic between channels,
        only emitting a trigger event if multiple channels are triggered at once.
        The period of time for which trigger events are accepted appears to be
        controlled by the wbias register (not set by this function).

        If the coincidence trigger is disabled for any chip, the default "OR"-like
        behavior is performed by the ASIC instead.

        Args:
            chips: a dict with chips (int) as keys, and enabled (bool) for the value
        """
        self._validate_coincidence_trigger_chips_or_raise(chips)
        self.board.trigger.params["coincidence_enabled"] = chips
        for chip, enabled in chips.items():
            # lowest bit of misc reg enables/disables the coincidence trigger
            # for the entire ASIC
            miscreg = self._digital_read("miscreg", chip)
            miscreg = (miscreg & 0b10) | enabled
            self._write_digital_register("miscreg", miscreg, chips=chip)

    def set_chip_trigger_mask(self, chips: list[int]):
        """Sets the chip trigger mask.

        Args:
            chips (list): a list of chips to trigger on

        Raises:
            TypeError if the given list is not actually a list
            InvalidTriggerMaskError if the list supplied is the wrong length
                or contains invalid elements
        """
        LOGGER.debug("Setting chip trigger mask: %s", chips)
        chipmask = sum(1 << chip for chip in chips)
        self._write_control_register("udc_trigger_mask", chipmask)

    def set_trigger_edge(self, channel_edges: dict[int, bool]):
        """Set which signal edge to trigger on per channel.

        Shift between positive going signals (rising) and negative (falling).
        The ASIC will not trigger on the signal until it detects the appropriate
        edge.

        Args:
            channel_edges (list[bool]): list of edge settings for each channel.
                Each value should be True for rising edges, or False for falling edges.
        """
        channel_edges = [channel_edges.get(c, False) for c in range(self._num_channels)]

        self._validate_edge_list_or_raise(channel_edges)
        LOGGER.debug("Setting trigger edges: %s", channel_edges)
        for chip in range(self._num_chips):
            edge_mask = self._extract_edge_mask_for_chip(channel_edges, chip)
            self._set_sgn(chip, edge_mask)
        self._reset_writemask()

    def _set_sgn(self, chip: int, edge_mask: int):
        """Set the sgn register.

        Highest bit is broadcast bit, it's required to be set
        in order to write to each copy of the sgn register individually

        Args:
            edge_mask (int): the edge mask for the given chip
        """
        sgn_l, sgn_r = self._flip_sgn_bytes(edge_mask)
        self._write_digital_register("writemask_l", 0x1FF, chips=chip)
        self._write_digital_register("writemask_r", 0, chips=chip)
        self._write_analog_register("sgn", sgn_l, chips=chip)
        self._write_digital_register("writemask_l", 0, chips=chip)
        self._write_digital_register("writemask_r", 0x1FF, chips=chip)
        self._write_analog_register("sgn", sgn_r, chips=chip)

    def _extract_edge_mask_for_chip(self, channel_edges: list[bool], chip: int) -> int:
        """Extract the edge mask for the given chip from the given list of edges.

        Args:
            channel_edges (list[bool]): list of edge settings for each channel.
                Each value should be True for rising edges, or False for falling edges.
            chip (int): the chip to extract the edge mask for

        Returns:
            int: the edge mask for the given chip
        """
        return sum(
            1 << c
            for c in range(self._channels_per_chip)
            if channel_edges[c + chip * self._channels_per_chip]
        )

    def _flip_sgn_bytes(self, sgn_mask: int) -> tuple[int, int]:
        """Flip the bytes of the sgn register mask.

        Individual bytes need to be flipped because the bits in
        the sgn register are reversed (i.e. bit 0 corresponds to channel 7).

        Args:
            sgn_mask (int): the full sgn mask. MSB corresponds to the right
                side, and lower bytes correspond to the left side.

        Returns:
            tuple[int, int]: sgn for the left side, and sgn for the right side.
        """

        def flip_byte(n):
            return int(f"{n:08b}"[::-1], 2)

        sgn_l = flip_byte(sgn_mask & 0xFF)
        sgn_r = flip_byte(sgn_mask >> 8)
        return sgn_l, sgn_r

    def _group_by_chips(self, pairs: dict[int, int]) -> dict[int, dict[int, list[int]]]:
        """Groups a list into a dict where the key is the chip,
        the value is a dict(list) which maps all unique values
        to the channels that correspond to them.

        Example::

            {
                0: { # chip
                    1000: [0, 1, 2, 3] # threshold: channels
                }
            }
        ```
        """
        groups = defaultdict(lambda: defaultdict(list))
        for channel, val in pairs.items():
            chip = channel // self._channels_per_chip
            groups[chip][val].append(channel)
        return groups

    def _filter_channels_for_chip(self, channels: list[int], chip: int) -> list[int]:
        """Filters out channels in the given list that don't belong to the given chip."""
        return list(filter(lambda c: (c // self._channels_per_chip) == chip, channels))

    def _reset_writemask(self):
        """Reset the write mask register for all chips.

        The writemask register is restored to 0x1FF (broadcast + all channels),
        regardless of what it was set to before. This is important because
        it ensures the other analog registers don't get written improperly
        elsewhere due to the writemask being wrong.
        """
        self._write_digital_register("writemask_l", 0x1FF)
        self._write_digital_register("writemask_r", 0x1FF)

    def _digital_read(self, name: str, chip: int) -> int:
        """Read the value of a digital register"""
        return DigitalRegisters(self.board, chips=chip).read(name)["value"]

    def _validate_channel_list_or_raise(self, channels):
        """Validates a list of channels, and raises an error
        if there's a problem with them.

        Args:
            channels: the object that is supposedly a channels list

        Raises:
            TypeError if the channel list is not a list
            InvalidTriggerMaskError if the list is too long,
                contains elements that are not an int,
                or contains elements that are too large.
        """
        if not isinstance(channels, list):
            raise TypeError(f"Channels needs to be a list, not a {type(channels)}")
        if len(channels) > self._num_channels:
            raise InvalidTriggerMaskError(
                f"Too many channels, max is {self._num_channels}"
            )
        for channel in channels:
            if not isinstance(channel, int):
                raise InvalidTriggerMaskError("Channels can only contain integers")
            if channel >= self._num_channels or channel < 0:
                raise InvalidTriggerMaskError(f"Channel {channel} is out of bounds")

    def _validate_trigger_list_or_raise(self, trigger_list: list):
        """Validates a list of thresholds, and raises an error
        if there's a problem with them.

        Args:
            trigger_list: a list containing thresholds values per channel

        Raises:
            TypeError if the trigger_list is not a list
            ValueError if theres more list values than channels,
                contains elements that are not an int,
                or contains elements that are too large.
        """
        if not isinstance(trigger_list, list):
            raise TypeError(
                f"trigger_list needs to be a list, not a {type_name(trigger_list)}"
            )
        if len(trigger_list) != self._num_channels:
            raise ValueError(
                f"trigger_list length: {len(trigger_list)} needs to match num channels: {self._num_channels}"
            )
        for threshold in trigger_list:
            if not isinstance(threshold, int):
                raise ValueError("Thresholds can only contain integers")
            if threshold > self._max_thresholds or threshold < self._min_thresholds:
                raise ValueError(f"Threshold {threshold} is out of bounds")

    def _validate_trigger_dict_or_raise(self, trigger_dict: dict[int, int]):
        """Validates a dictionary of thresholds, and raises an error
        if there's a problem with them.

        Args:
            trigger_dict: a dict containing thresholds values per channel

        Raises:
            TypeError if the trigger_dict is not a dict
            ValueError if theres more dict values than channels,
                contains elements that are not an int,
                or contains elements that are too large.
        """
        if not isinstance(trigger_dict, dict):
            raise TypeError(
                f"trigger_dict needs to be a dict, not a {type_name(trigger_dict)}"
            )
        if len(trigger_dict) > self._num_channels:
            raise ValueError(
                f"trigger_dict length: {len(trigger_dict)} needs to match num channels: {self._num_channels}"
            )
        for channel, threshold in trigger_dict.items():
            if not isinstance(channel, int):
                raise ValueError(f"Channel {channel} is not an int")
            if not isinstance(threshold, int):
                raise ValueError(f"Threshold {threshold} is not an int")
            if not self._min_thresholds <= threshold <= self._max_thresholds:
                raise ValueError(
                    f"Threshold {threshold} is out of bounds ({self._min_thresholds}:{self._max_thresholds+1})"
                )

    def _validate_edge_list_or_raise(self, edge_list: list):
        """Validates a list of edges of bools, and raises an error
        if there's a problem with them.

        Args:
            edge_list: a list containing thresholds values per channel

        Raises:
            TypeError if the edge_list is not a list
            ValueError if theres more list values than channels,
                contains elements that are not a bool,
                or contains elements that are too large.
        """
        if not isinstance(edge_list, list):
            raise TypeError(
                f"trigger_list needs to be a list, not a {type_name(edge_list)}"
            )
        if len(edge_list) != self._num_channels:
            raise ValueError(
                "edge_list is not the same length as the number of channels"
            )
        if any(not isinstance(edge, bool) for edge in edge_list):
            raise ValueError("edge_list can only contain bools")

    def _validate_coincidence_trigger_chips_or_raise(self, chips: dict):
        """Validate whether the arguments to the coincidence trigger setter are valid

        Args:
            chips (dict): a dict with chip num (int) as a key and
                coincidence enable as the value (bool)

        Raises:
            TypeError: if chips is not a dict
            ValueError: if chips keys contains chips that are out of range of num chips
            TypeError: if chips values contains elements that are not a bool
        """
        if not isinstance(chips, dict):
            raise TypeError(f"chips needs to be a dict, not a {type_name(chips)}")
        for k, v in chips.items():
            if k not in range(self._num_chips):
                raise ValueError(f"chips contains an invalid key: {k}")
            if not isinstance(v, bool):
                raise TypeError(f"chip contains an invalid value: {v}")

    def _validate_enable_trig_out(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"value needs to be a bool, not a {type_name(value)}")
