import logging
from collections import deque
from functools import partial

import numpy as np

from naludaq.board import Board
from naludaq.controllers import get_dac_controller
from naludaq.helpers.exceptions import (
    BadDataError,
    InvalidOptimizationParameters,
    IterationError,
    OperationCanceledError,
    OptimizationError,
)
from naludaq.helpers.helper_functions import (
    find_missing_channels,
    group_channels_by_chip,
)
from naludaq.tools.data_collector import get_data_collector

from .channel_writer import UDC16ChannelWriter

LOGGER = logging.getLogger("naludaq.ConversionRampOptimizer")


class UDC16ConversionRampOptimizer:
    """Generates tuning parameters for isel ramp current and cap select
    Tuning parameters are of the form:
    {
        0 (Channel): {
            isel_ramp_current: (value),
            isel_cap_select: (value),
        }
    }
    """

    def __init__(self, board: Board):
        self.board = board

        self._progress = []
        self._canceled = False
        self._num_channels = board.channels
        self._num_chips = board.available_chips
        self._channels_per_chip = self._num_channels // self._num_chips
        self.target_value = 500

        self.channel_writer = UDC16ChannelWriter(self.board)
        self.channel_writer.reset_mask_after_write = False
        self._last_event_channels = []
        self._bad_channels = []

    @property
    def progress(self):
        """Get/Set the progress message queue.

        This is a hook the read the progress if running threads.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    def run(self, channels: list[int]):
        """Tunes the isel ramp and cap to put the given channels into the midrange.
        Writes the parameters per channel and stores the tuning values to board.tuning.

        Args:
            channels (list[int]): List of channels to tune

        Raises:
            OptimizationError: Something went wrong with running the optimizing script
            TimeoutError: Data capture timedout/couldn't get data
            OperationCanceledError: The operation was canceled by the user
        """
        suggested_parameters = self.generate(channels)
        self.validate_iselrampcap_values(suggested_parameters)
        if suggested_parameters:
            # Status message ###############################
            _update_progress(
                self.progress,
                80,
                f"Calibrating ramp:",
            )

            self._update_isel_for_channels(suggested_parameters)
            self.board.tuning["conversion_ramp"] = suggested_parameters
        else:
            raise OptimizationError(
                "Optimization for Conversion Ramp failed. Unable to create optimization parameters"
            )

        if self._bad_channels:
            raise OptimizationError(self._chan_data_err_str(channels))

    def generate(self, channels: list[int]):
        """Determines the isel ramp and cap to put the average values of the given
        channels to the target value (default=500). Uses linear regression to
        determine what values to set isel ramp current and cap select to put the
        average channel value to the target value.

        Args:
            channels (list[int]): List of channels to tune

        Returns:
            suggested_parameters (dict): Dictionary where it maps the
                register, to a list of values per channel.
            Tuning parameters are of the form:
            {
                0 (Channel): {
                    isel_ramp_current: (value),
                    isel_cap_select: (value),
                }
            }

        Raises:
            OptimizationError: Something went wrong with running the optimizing script
            OperationCanceledError: The operation was canceled by the user
        """
        self._validate_channel_list_or_raise(channels)

        suggested_parameters = []
        self._canceled = False
        self._last_event_channels = []
        self._bad_channels = []
        _update_progress(self.progress, 0, "Starting optimizer")
        try:
            self._backup_settings()
            self._set_default_dac_values()
            suggested_parameters = self._get_calibration_isel_for_channels(channels)
        except (OperationCanceledError, KeyboardInterrupt) as e:
            self.cancel()
            raise OperationCanceledError("Conversion Ramp tuning canceled") from e
        except Exception as e:
            self.cancel()
            raise OptimizationError("Optimization failed") from e
        finally:
            self._restore_settings()
            self._restore_tuning()

        return suggested_parameters

    def cancel(self):
        self._canceled = True

    def _reset_write_mask(self):
        self.channel_writer.reset_writemask()

    def _restore_tuning(self):
        """Restores isel ramp and cap to board.tuning values.

        If board.tuning doesn't contain tuning values, ramp
        and cap will be set to the default settings
        """
        conversion_ramp = self.board.tuning.get("conversion_ramp", None)
        if conversion_ramp:
            self.validate_iselrampcap_values(conversion_ramp)
            self._update_isel_for_channels(conversion_ramp)
        else:
            self._reset_tuning()

    def _reset_tuning(self):
        """Resets isel ramp and cap tuning parameters to defaults,
        ramp: 0x03, cap: 0x00.
        """
        self.channel_writer.write_analog_register("isel_cap_select", 0x00)
        self.channel_writer.write_analog_register("isel_ramp_current", 0x03)
        self.board.tuning["conversion_ramp"] = None
        self._reset_write_mask()

    def _backup_settings(self):
        self._backup_dac = self.board.dac_values.copy()

    def _restore_settings(self):
        for chan, value in self._backup_dac.items():
            get_dac_controller(self.board).set_single_dac(chan, value)

    def _set_default_dac_values(self):
        get_dac_controller(self.board).set_default_values()

    def _get_data(
        self, channels: list[int], num_events: int = 1, num_attempts: int = 5
    ):
        data_collector = get_data_collector(self.board)
        filter = partial(self._filter_data_for_channels, channels=channels)
        try:
            data = (
                data_collector.iter(num_events, num_attempts)
                .filter(filter, exclusion_limit=5)
                .collect()
            )
        except IterationError:
            raise BadDataError(self._iter_err_str(channels))

        return data

    def _filter_data_for_channels(self, evt, channels: list) -> bool:
        """Filter function to determine if an event has data for all the given channels"""
        self._last_event_channels = [c for c in channels if len(evt["data"][c]) != 0]
        no_data_channels = [c for c in channels if len(evt["data"][c]) == 0]
        if no_data_channels:
            LOGGER.warning("Could not capture data for channels: %s", no_data_channels)
        return True

    def _change_isel_reg_of_channel(self, channels: list, reg: str, val: int):
        """Wrapper function for writing the proper ISEL configuration to just the channels specified.

        Args:
            channels (list): Channels, relative to the chip, to write ISEL values to
            reg (str): Which ISEL parameter to change ("isel_cap_select" or "isel_ramp_current")
            val (int): Value to write (up to 3 for ramp, up to 15 for cap)
        """
        self.channel_writer.write_analog_register(reg, val, channels)

    def _get_calibration_isel_for_channels(self, channels: list[int]) -> dict:
        """
        Writes the proper ISEL ramp current and cap settings that result in an average event baseline
        value of target_value (default=500), for the chip specified.

        Args:
            chip (int): chip number to calibrate ISEL for

        Returns:
            suggested_vals (dict): the suggested parameters for isel ramp current and cap select.
            The key corresponds to the register to write, and value is a list of values per channel.
        """
        suggested_vals = {}

        suggested_vals_chip = self._get_suggested_value_for_channels(channels)

        for chan, val in zip(channels, suggested_vals_chip):
            if np.isnan(val).any():
                self._bad_channels.append(chan)
                continue

            suggested_vals[chan] = {
                "isel_cap_select": val[1],
                "isel_ramp_current": val[0],
            }
        if self._bad_channels:
            LOGGER.warning(self._chan_data_err_str(channels))

        return suggested_vals

    def _update_isel_for_channels(self, suggested_vals: dict):
        self.validate_iselrampcap_values(suggested_vals)
        for chan, suggestions in suggested_vals.items():
            for register, value in suggestions.items():
                self._change_isel_reg_of_channel([chan], register, value)
        self._reset_write_mask()

    def _get_suggested_value_for_channels(self, channels: list = range(16)) -> list:
        """
        Finds the linear parameters for each of the 3 ISEL ramp speeds by taking two points
        (all caps off and all caps on), finds the ramp speed that can result in an event average of 500,
        then finds the cap configuration within that ramp speed to ensure an event average of 500.

        Args:
            self.board (self.board): Upac96 self.board object with an active connection
            channels (list, optional): Chip-specific channels to configure. Defaults to range(16).

        Returns:
            list: the values written, 1 tuple (x) for each channel; x[0] is current, x[1] is ramp cap
        """

        channel_recs = []

        # find linear parameters for each of the 3 ISEL ramp speeds

        values = []

        isel_currents = [0, 1, 3]
        for step_idx, isel_current in enumerate(isel_currents):
            # Status message ###############################
            min_progress = 10
            max_progress = 80
            _update_progress(
                self.progress,
                10 + (max_progress - min_progress) * step_idx / len(isel_currents),
                f"Capturing Calibration Data:",
            )
            LOGGER.debug(
                "Capturing Calibration Data for isel_current_ramp: %d", isel_current
            )
            # Get slope between lowest and highest cap select values
            slope, yint = self._get_slope_for_current_state(isel_current, channels)
            # finds suggested cap select that result in an event average of 500
            value = self._get_suggested_cap_from_isel_lin(slope, yint)
            values.append(value)

        for channel in channels:
            if np.isnan(values[1][channel]).any():
                channel_recs.append(np.nan)
                continue

            # choose the midrange current as well as the cap for midrange current
            value_to_append = [1, values[1][channel]]

            # if cap configuration is too low, choose the lower current and its cap config.
            if values[1][channel] < 0:
                value_to_append = [0, values[0][channel]]

            # if cap configuration is too high, choose the higher current and its cap config.
            if values[1][channel] > 15:
                value_to_append = [3, values[2][channel]]

            # edge case handling in case cap config is still out of bounds
            value_to_append[1] = min(value_to_append[1], 15)
            value_to_append[1] = max(value_to_append[1], 0)

            channel_recs.append(value_to_append)

        return channel_recs

    def _get_suggested_cap_from_isel_lin(
        self, slopes: list[float], yints: list[float]
    ) -> list:
        """Suggests a ISEL cap configuration to write to given a the slope and y-intercept of the
        ADC-count and isel-cap linear relationship. Suggests one for each channel given. If the
        slope for a given channel is 0, the suggested isel-cap will be board default (0)

        Args:
            slopes (list(float)): List of calculated slope for ADC-count/isel-cap for each channel
            yints (list(float)): List of calculated y-int for ADC-count/isel-cap for each channel

        Returns:
            list: List of suggested cap configs to write to "isel_cap_select" digreg. Per channel
        """
        values = []
        for slope, yint in zip(slopes, yints):
            if np.isnan(slope) or np.isnan(yint):
                values.append(np.nan)
            elif slope != 0:
                values.append(round((self.target_value - yint) / slope))
            else:
                values.append(0)

        return values

    def _get_slope_for_current_state(
        self, current_state: int, channels: list = range(16)
    ):
        """Gets the slope and y-intercept from the ADC-mv/isel-cap relationship by taking events at the lowest and highest cap
        config. for a given ISEL current state.

        Args:
            current_state (int): ISEL current state to try (0, 1, or 3)
            channels (list): List of channels per chip to get linear parameters for

        Returns:
            list(float), float: list of slopes per channel and the y-intercept for the given current state
        """

        self._change_isel_reg_of_channel(channels, "isel_ramp_current", current_state)
        self._change_isel_reg_of_channel(channels, "isel_cap_select", 0)

        min_data = self._get_data(channels)
        chan_min = self._get_channel_avgs_from_readout(min_data)

        self._change_isel_reg_of_channel(channels, "isel_cap_select", 15)

        max_data = self._get_data(channels)
        chan_max = self._get_channel_avgs_from_readout(max_data)

        chan_slopes = [
            x / self._channels_per_chip for x in np.subtract(chan_max, chan_min)
        ]

        return chan_slopes, chan_min

    def _get_channel_avgs_from_readout(self, events: deque):
        """Gets the average ADC count per channel of a given event
        Will average if there are multiple events
        Args:
            readout (deque): Deque of parsed events to get ADC count averages from

        Returns:
            list(float): List of ADC count averages, per channel
        """
        chan_avgs = []

        events_array = np.array([event["data"] for event in events])
        averaged_events = np.mean(events_array, axis=0)

        for channel in averaged_events:
            chan_avgs.append(np.mean(channel))

        return chan_avgs

    def _validate_channel_list_or_raise(self, channels):
        """Validates a list of channels, and raises an error
        if there's a problem with them.

        Args:
            channels: the object that is supposedly a channels list

        Raises:
            TypeError if the channel list is not a list or
                values are not an int
            ValueError if the values are out of range
        """
        if not isinstance(channels, (list, range)):
            raise TypeError(
                f"Channels needs to be a list, not a {type(channels).__name__}"
            )
        if len(channels) > self._num_channels:
            raise ValueError(f"Too many channels, max is {self._num_channels}")
        for channel in channels:
            if not isinstance(channel, int):
                raise TypeError(f"Channels can only contain integers")
            if channel >= self._num_channels or channel < 0:
                raise ValueError(f"Channel {channel} is out of bounds")

    def validate_iselrampcap_values(self, tuning_values: dict):
        """Validates parameters for isel ramp and cap. Ensures the channels,
        and values for ramp and cap are valids.

        Args:
            tuning_values (dict): the tuning parameters for isel ramp & cap

        Raises:
            TypeError if the parameters are not of type dict
            ValueError if the channel or tuning parameters are out of range
            KeyError if the parameters holds an invalid key for isel ramp & cap
        """
        cap_width = self.board.registers["analog_registers"]["isel_cap_select"][
            "bitwidth"
        ]
        ramp_width = self.board.registers["analog_registers"]["isel_ramp_current"][
            "bitwidth"
        ]
        max_values = {}
        max_values["isel_cap_select"] = 2**cap_width - 1
        max_values["isel_ramp_current"] = 2**ramp_width - 1
        if not isinstance(tuning_values, dict):
            raise InvalidOptimizationParameters(
                f"Conversion Ramp parameters should be of type dict, got type: {type(tuning_values).__name__}"
            )

        if len(tuning_values) > self._num_channels:
            raise InvalidOptimizationParameters(
                f"Dictionary contains more than {self._num_channels} channel values"
            )

        for channel, suggested_tuning in tuning_values.items():
            if channel < 0 or channel > self._num_channels:
                raise InvalidOptimizationParameters(
                    f"Channel {channel} is out of range"
                )

            for key, value in suggested_tuning.items():
                if not isinstance(value, int):
                    raise InvalidOptimizationParameters(
                        f"Tuning values should be of type int, got type: {type(value).__name__}"
                    )
                if key not in ["isel_ramp_current", "isel_cap_select"]:
                    raise InvalidOptimizationParameters(f"{key} Not in tuning file")
                if value < 0 or value > max_values[key]:
                    raise InvalidOptimizationParameters(
                        f"Value of {value} for key {key} is out of range"
                    )

    def _iter_err_str(self, channels: list[int]) -> str:
        """Get a string suitible for an error message when an iteration error occurs.

        Includes any missing channels and chips.
        """
        channels_per_chip = self.board.params.get("channels_per_chip", 16)
        missing_channels = find_missing_channels(channels, self._last_event_channels)
        missing_channels = group_channels_by_chip(missing_channels, channels_per_chip)

        chip_parts = []
        for chip, missing_in_chip in missing_channels.items():
            if len(missing_in_chip) == 0:
                continue
            msg = f"- Chip {chip}: all channels"
            if len(missing_in_chip) < channels_per_chip:
                chan_repr = ", ".join(map(str, missing_in_chip))
                msg = f"- Chip {chip}: channel(s) {chan_repr}"
            chip_parts.append(msg)

        missing_formatted = "\n".join(chip_parts)
        return (
            "Failed to generate ALO tuning because the following chips/channels "
            "cannot be read from the hardware:\n"
            f"{missing_formatted}\n\n"
            "Please try again and power cycle the board if the issue persists. To instead ignore this error, "
            "deselect the affected channel(s) and try again."
        )

    def _chan_data_err_str(self, channels: list[int]) -> str:
        """Get a string suitible for an error message when unable to capture
        data for some channels. States which channels have been tuned, and
        which ones have failed.
        """
        channels_per_chip = self.board.params.get("channels_per_chip", 16)
        missing_channels = find_missing_channels(channels, self._last_event_channels)
        missing_channels = group_channels_by_chip(missing_channels, channels_per_chip)
        tuned_channels = group_channels_by_chip(channels, channels_per_chip)
        tuned_chip_parts = []
        missing_chip_parts = []
        for chip, missing_in_chip in missing_channels.items():
            if len(missing_in_chip) == 0:
                continue
            for missing_chan in missing_in_chip:
                tuned_channels[chip].remove(missing_chan)
            msg = f"- Chip {chip}: all channels"
            if len(missing_in_chip) < channels_per_chip:
                chan_repr = ", ".join(map(str, missing_in_chip))
                msg = f"- Chip {chip}: channel(s) {chan_repr}"
            missing_chip_parts.append(msg)

        for chip, tuned_in_chip in tuned_channels.items():
            if len(tuned_in_chip) == 0:
                continue

            msg = f"- Chip {chip}: all channels"
            if len(tuned_in_chip) < channels_per_chip:
                chan_repr = ", ".join(map(str, tuned_in_chip))
                msg = f"- Chip {chip}: channel(s) {chan_repr}"
            tuned_chip_parts.append(msg)

        missing_formatted = "\n".join(missing_chip_parts)
        tuned_formatted = "\n".join(tuned_chip_parts)
        return (
            "Tuned chips/channels:\n"
            f"{tuned_formatted}\n\n"
            "Failed to generate ALO tuning for the following chips/channels\n"
            f"{missing_formatted}\n\n"
            "Please try again and power cycle the board if the issue persists."
            "deselect the affected channel(s) and try again."
        )


def _update_progress(receiver, percent: float, message: str):
    """Updates a progress "receiver" with a percent and message.

    The receiver can be a list or deque of (percent, message) tuples,
    or a ProgressDialog (for use with NaluScope).

    Args:
        receiver (list, deque, or ProgressDialog): the receiver of the progress update.
            Can be None to report nothing
        percent (float): the percent completion of the task
        message (str): a description of what is currently taking place
    """
    if receiver is None:
        LOGGER.debug("%s | %s", percent, message)
        return
    elif isinstance(receiver, (list, deque)):
        receiver.append((percent, message))
    else:
        try:
            receiver.update_status(percent, message)
        except:
            pass
