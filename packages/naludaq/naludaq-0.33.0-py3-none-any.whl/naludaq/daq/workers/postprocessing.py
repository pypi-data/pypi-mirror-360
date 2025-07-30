"""Center the timescale of an event around the trigger value.

DESCRIPTION:
Finds the first intersections between the graph and the trigger value.
Then creates a new timescale with the

"""
from copy import deepcopy
from logging import getLogger

import numpy as np

LOGGER = getLogger(__name__)


class PostProcessing:
    def __init__(self):
        # self.flags
        self.postprocessors = list()

    def process_event(self, event):
        for processor in self.postprocessors:
            processor(event)


def trim_event(evt, keep_left=False, keep_right=False):
    """Prunes all channels on both left and right side.

    This function is destructive, it will alter the inputed event permanently.


    Args:
        evt(Event): prune target
        keep_left(int): samples to keep before the trigger
        keep_right(int): samples to keep after the trigger

    """
    # should be negative and the amount to cut is based on this.
    first_sample = int(evt["time"][0][0])
    last_sample = int(evt["time"][0][-1])

    remove_left = 0
    if keep_left is not False:
        if abs(first_sample) >= keep_left > -1:  # first sample should be negative
            remove_left = abs(first_sample) - keep_left

    remove_right = -1
    if keep_right is not False:
        if last_sample >= keep_right > -1:
            remove_right = (
                abs(first_sample) + keep_right
            )  # keep to the right of the trigger

    output = []
    for chan in range(len(evt["data"])):
        output.append(evt["data"][chan][remove_left:remove_right])  # Trim all channels
    evt["data"] = None
    evt["data"] = output

    output = None
    try:
        output = evt["time"][:, remove_left:remove_right]
        evt["time"] = None
        evt["time"] = output
    except TypeError as error_msg:
        raise TypeError(
            f"{str(error_msg)} types: "
            f" {str(type(evt['time']))}, {str(type(evt['data']))}"
            f" Values: {str(remove_left)}, {str(remove_right)}"
        )

    return evt


class CenterOnTrigger:
    def __init__(self, rising_edge=True):
        self.rising_edge = rising_edge

    def find_intersection(self, evt, trigger_value, chan=0):
        """Find the first intersection between data and trigger_value.

        Args:
            evt(Event): Event to find the intersection in
            trigger_value(int): value to intersect
            chan(int): Which channel to track?

        Returns:
            the sample number where the data intersects with the trigger_val or 0.
        """
        if getattr(evt, "data", False):
            return 0

        index_intersection = 0
        event_data = np.array(evt["data"][chan], dtype="int")

        try:
            diff = np.diff(np.sign(event_data - trigger_value))
        except (Exception, TypeError) as e_msg:
            LOGGER.debug("something wrong with Center on trigger, %s", e_msg)
            return 0

        coefficient = -1 + 2 * self.rising_edge
        index_intersection = np.argwhere(coefficient * diff > 0).flatten()
        for x in index_intersection:
            return x

        # Can't find the edge? flip the rising edge to falling edge.
        self.flip_edge()

        index_intersection = np.argwhere(coefficient * diff < 0).flatten()

        for x in index_intersection:
            return x

        return 0

    def adjust_time_axis(self, evt, trigger_val, chan=0):
        """Align the timeline based on the trigger.

        find the intersection with the trigger value and center the timescale on the intersection.
        The function updates the passed event.

        Args:
            evt(Event): event to centera
            trigger_val(int): value the board tirggers on.
            chan(int): Channel to find intersction on.
        """
        adjusted_evt = deepcopy(evt)
        flip_pt = self.find_intersection(evt, trigger_val, chan)

        if evt["time"][chan][flip_pt] == 0:
            flip_pt = 0
        try:
            event_time = np.array(evt["time"], dtype=float)
        except ValueError:
            event_time = np.array(evt["time"], dtype=object)

        adjusted_evt["time"] = event_time - flip_pt

        return adjusted_evt

    def flip_edge(self):
        self.rising_edge = not self.rising_edge


class LinearCorrect:
    """Old Bencode to linear correct an event.

    Currently it will only correct on sample at the time.
    Incredibly slow.

    """

    def __init__(self):
        # Linear correction is
        lin_corr_fit = [5.38991698e02, -5.03758060e-01, 6.53423798e-04, -6.60463292e-08]
        self.lin_corr_x = np.arange(0.0, 4096.0)
        self._lin_corr_lin = (
            (lin_corr_fit[3] * self.lin_corr_x**3)
            + (lin_corr_fit[2] * self.lin_corr_x**2)
            + (lin_corr_fit[1] * self.lin_corr_x)
            + lin_corr_fit[0]
        )

    def linear_correction(self, sample):
        """Linear correct a sample."""
        lin_index = np.abs(self._lin_corr_lin - sample).argmin()
        corr = self.lin_corr_x[lin_index]
        return corr


def shift_time_for_forced_mode(event: dict, insert_nan: bool = True):
    """Shifts the time axis to start at the start window. Mainly useful for events
    captured in forced mode.

    If the window labels roll over (end of sampling array is reached in event),
    then the time axis is adjusted to roll over as well. For use in plotting, this
    can cause some ugly jumps, hence the `insert_nan` parameter.

    Warning: as a safety precaution against shifting the axis multiple times,
    this function will ignore events if the time axis does not start at zero.

    Args:
        event (dict): event to work on. The event is modified in-place.
        insert_nan (bool): whether to insert a single `np.nan` into the
            time and data arrays when a discontinuity is created. Useful
            for plotting.

    Returns:
        dict: the same event dict passed in.
    """
    # If the time axis doesn't start at zero, all the processing is invalid
    if int(event["time"][0][0]) != 0:
        return event

    # Disabled channels are empty lists, which cause an error since the data/time arrays are ragged
    _fill_empty_channels_with_nan(event)

    data = np.array(event["data"], dtype=np.float)  # float required for using np.nan
    time = np.array(event["time"], dtype=np.float)
    window_labels = np.array(event["window_labels"])

    # Shift time axis to start at start window
    samples = data.shape[1] // window_labels.shape[1]
    start_sample = event["start_window"] * samples
    time += start_sample

    # If window labels roll over, make sure the time axis rolls over too
    roll_over_loc = np.argwhere(
        window_labels < event["start_window"]
    )  # Doesn't necessarily roll back to zero
    if len(roll_over_loc) != 0:
        rollover_chan, rollover_idx = roll_over_loc[0][0], roll_over_loc[0][1]
        max_winds = window_labels[rollover_chan, rollover_idx - 1] + 1
        time %= max_winds * samples

        if insert_nan:
            time = np.insert(time, rollover_idx * samples, np.nan, axis=1)
            data = np.insert(data, rollover_idx * samples, np.nan, axis=1)

    event["data"] = data
    event["time"] = time

    return event


def _fill_empty_channels_with_nan(event: dict):
    """Fill data/time/window_labels fields with np.nan for channels that are
    disabled to make the arrays non-ragged.
    """
    total_samples = max([len(x)] for x in event["data"])
    total_windows = max([len(x) for x in event["window_labels"]])
    nan_for_samples = np.full(total_samples, np.nan, dtype=np.float)
    nan_for_windows = np.full(total_windows, np.nan, dtype=np.float)

    for chan, chan_data in enumerate(event["data"]):
        if len(chan_data) != 0:
            continue
        event["data"][chan] = nan_for_samples
        event["time"][chan] = nan_for_samples
        event["window_labels"][chan] = nan_for_windows
