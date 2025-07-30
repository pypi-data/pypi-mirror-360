import logging

from naludaq.controllers import get_board_controller
from naludaq.helpers.exceptions import IterationError, RegisterNameError
from naludaq.helpers.helper_functions import (
    find_missing_channels,
    group_channels_by_chip,
)

from .udc16 import PedestalsGeneratorUdc16

LOGGER = logging.getLogger("naludaq.pedestals_generator_upac96")


def disable_trigger_monitor_signal(func):
    """Decorator to disable the trigger monitor signal during the execution of a function.

    Args:
        func (function): function to decorate

    Returns:
        function: decorated function
    """

    def wrapper(self, *args, **kwargs):
        try:
            previous = self.board.registers["control_registers"][
                "trigger_monitor_disable"
            ]["value"]
        except KeyError:
            raise RegisterNameError("trigger_monitor_disable")
        bc = get_board_controller(self.board)
        bc.set_trigger_monitoring_disabled(disabled=True)
        try:
            result = func(self, *args, **kwargs)
        finally:
            bc.set_trigger_monitoring_disabled(previous)
        return result

    return wrapper


class PedestalsGeneratorUpac96(PedestalsGeneratorUdc16):
    """Pedestals generator for UPAC96."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # last event, regardless of whether it's valid or not
        self._last_event_channels = []

    @disable_trigger_monitor_signal
    def _capture_data_for_pedestals(self) -> list[list[dict]]:
        return super()._capture_data_for_pedestals()

    def _validate_event(self, event):
        """Check if the event has a data field, which means it's parsed"""
        self._last_event_channels = []
        if "data" not in event:
            LOGGER.warning("Got an invalid event")
            return False
        chans_with_data = [i for i, x in enumerate(event.get("data", [])) if len(x) > 0]
        self._last_event_channels = chans_with_data
        is_superset = set(chans_with_data).issuperset(self.channels)
        if not is_superset:
            LOGGER.warning(
                "Got a parseable event, but the channels are incorrect: %s",
                chans_with_data,
            )
        return is_superset

    def _exc_str(self, e: Exception) -> str:
        """Override since UPAC96 can fail on a per-chip basis"""
        missing_channels = find_missing_channels(
            self.channels, self._last_event_channels
        )
        # IterationError means we're getting valid data but it's getting filtered
        # out by the constraints in `validate_event()`. Got a custom message for that.
        if not isinstance(e, IterationError) or len(missing_channels) == 0:
            return super()._exc_str(e)

        channels_per_chip = self.board.params.get("channels_per_chip", 16)
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
            "Failed to generate pedestals calibration because the following chips/channels "
            "cannot be read from the hardware:\n"
            f"{missing_formatted}\n\n"
            "Please try again and power cycle the board if the issue persists. To instead ignore this error, "
            "deselect the affected channel(s) and try again."
        )
