"""Timing correction calibration

Tool to generate the timing data.

To generate the timing data, data should be captured with a setup as shown in
link:

DESCRIPTION

A large number of events need to be captured, a minimum of 10k events is required.
The data must be captured using

"""
import logging
from copy import deepcopy
from typing import List

import numpy as np

from naludaq.helpers.exceptions import BadDataError

LOGGER = logging.getLogger(__name__)


class TimingCalibration:
    def __init__(self, board):
        """Create calibration data for timing calibration."""
        self.board = board
        self.progress = []
        self.num_xings = 2  # Assume two peaks
        self.threshold = 300
        self.xing_num = None
        self.samp_corr = False
        self._minimum_events = 50  # _000
        self._cancel = False

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

    @property
    def minimum_events(self):
        """Get/Set the minimum events needed to run calibration

        This is used to validate a dataset.
        """
        return self._minimum_events

    @minimum_events.setter
    def minimum_events(self, value):
        if not isinstance(value, int):
            raise TypeError("minimum_events must be an integer")
        if value <= 0:
            raise ValueError("minimum_events must be a positive value")
        self._minimum_events = value

    def cancel(self):
        self._cancel = True

    def generate(self, events, channel: int = 0, threshold: int = 300, peaks=(0, 1)):
        """Generate timing calibration and adds to board.

        Will validate the incoming data and raise and error if
        it doesn't contain enough data to run a validation

        Args:
            events: collection of events
            channel: channel containing data
            threshold: int value to intersect peaks.
        """
        LOGGER.info(
            "Generate timing cal constants using, %s events, ch: %s, threshold: %s",
            len(events),
            channel,
            threshold,
        )
        old_timingcal = deepcopy(self.board.timingcal)

        events = self._get_valid_events(events, channel, threshold, peaks)
        if len(events) < self.minimum_events:
            self.board.timingcal = old_timingcal
            raise BadDataError("Not enough valid events to run calibration")

        dt = self._try_generate_dts_or_log(events, threshold, channel)

        if self._cancel is True:
            return

        self.board.timingcal = dt
        self.progress.append(("Timing calibration set successfully", 100))
        LOGGER.debug("Timing calibration set successfully")
        return

    def _try_generate_dts_or_log(self, events, threshold, channel):
        dt = None
        try:
            dt = self.generate_dts(events, threshold)[channel]
        except Exception as emsg:
            import traceback

            track = traceback.format_exc()
            LOGGER.debug("Failed to generate dts due to %s\n%s", emsg, track)
            self._cancel = True
        return dt

    # VALIDATION ###################################################
    def _get_valid_events(
        self, events: dict, channel: int, threshold: int, peaks: tuple
    ) -> List[dict]:
        """Measure distance between two pulses using simple threshold

        Will skip the event if more or less than 2 peaks.

        Args:
            events: list of events to validate
            channel: channnel of interest
            threshold: integer for intersection with peak
            corrected: timing correct time field in event.
        Returns:
            list of distances between peaks.
        """
        indexed_distances = self._distances_between_two_peaks(
            events, channel, threshold, peaks
        )
        if indexed_distances:
            output_idx = self._drop_distance_outliers(indexed_distances)
        else:
            output_idx = []

        output = [events[i] for i in output_idx]

        return output

    def _find_all_rising_edge_xings(self, event: dict, channel: int, threshold: int):
        """Returns all rising edge xings in an event.

        Args:
            event: collection of events to check
            threshold: threshold value to use for the check.
            num_xings: number of crossing to expect

        Returns:
            List of all rising crossings between event data and threshold
        """
        return np.where(np.diff(np.sign(event["data"][channel] - threshold)) > 0)[0]

    def _distances_between_two_peaks(
        self, events: dict, channel: int, threshold, peaks: tuple
    ):  # -> List[int, float]:
        """Return a list[(index, distance)] for all distances."""
        distances = []
        for idx, evt in enumerate(events):
            if "data" not in evt.keys():
                continue
            xings = self._find_all_rising_edge_xings(evt, channel, threshold)
            if len(xings) == 0:
                continue
            xaxis = evt["time"][channel]
            x_0 = xaxis[xings[peaks[0]]]
            x_1 = xaxis[xings[peaks[1]]]
            dx = x_1 - x_0

            distances.append((idx, dx))
        return distances

    def _drop_distance_outliers(self, distances, deviation: float = 5.0):
        """Returns all distances within the tolerated interval

        Args:
            distances (list): List of tuples with (index, distance)
            deviation: distance in sample counts from the mean distance

        Returns:
            List of indexes that pass the test
        """

        mean = np.mean(np.array(distances)[:, 1])
        output = []
        for d in distances:
            if (mean - deviation) < d[1] < (mean + deviation):
                output.append(d[0])
        return output

    ################################################################

    def generate_dts(self, events, threshold=600):
        """Generates a `dt` array which is used to correct events.

        Combines combile_bof() and calc_dts() into a single function
        Determine the locations of the crossings

        Args:
            events (deque): List of events, see module description for setup.
            threshold (int): threshold value used.
        """
        samples = self.board.params.get("samples", 64)
        bof = self._compile_bof(events, threshold=threshold)
        results = list()

        for i, chan_bof in enumerate(bof):
            if np.all(np.isnan(chan_bof)):
                results.append(np.zeros(samples * 2))  # TODO: Assumes 128 samples.
            else:
                dts = self._calc_dts(chan_bof)
                results.append(dts)

        return results

    def _compile_bof(self, events, **kwargs):
        """
        Inputs a bunch of events with a randomly occuring pulse and determines
        the locations of the crossings

        Returns a list *for each channel*
        """
        channels = self.board.params.get("channels", 4)
        results = list()
        for chan in range(channels):
            results.append(list())
        for event in events:
            try:
                xings = self._find_bin_edge(event, **kwargs, samp_corr=True)
            except Exception as err:
                LOGGER.error("Couldn't find bin edge:%s", err)
                continue
            for chan, chan_xings in enumerate(xings):
                for xing in chan_xings:
                    results[chan].append(xing)
            if self._cancel is True:
                return []

        aresults = list()
        for result in results:
            # print(f"LEN RESULT: {len(result)}")
            aresults.append(np.array(result))

        return aresults

    def _find_bin_edge(self, event, **kwargs):
        if "threshold" in kwargs.keys():
            threshold = kwargs["threshold"]
        else:
            threshold = self.threshold  # 600
        if "xing_num" in kwargs.keys():
            xing_num = kwargs["xing_num"]
        else:
            xing_num = self.xing_num  # None

        if "samp_corr" in kwargs.keys():
            samp_corr = kwargs["samp_corr"]
        else:
            samp_corr = self.samp_corr  # False

        all_chan_xings = list()

        # loop over channels
        for data, winds in zip(event["data"], event["window_labels"]):
            chan_xings = list()

            # possible there isn't any data i guess
            if data is None:
                chan_xings.append(np.nan)
            else:
                xings = np.where(np.diff(np.sign(data - threshold)) > 0)[0]
                # print(f"{xings=}")
                if len(xings) <= 1:  # Can't use one peak
                    chan_xings.append(np.nan)
                    continue
                if (
                    len(xings) != self.num_xings
                ):  # Default two peaks, but no reason to run more
                    xings = xings[:2]
                    # print(f"{xings=}")
                    #  chan_xings.append(np.nan)
                # else:
                if xing_num is None:
                    for xing in xings:
                        # print(f"MEEP {xing=}")
                        if samp_corr:
                            value = self._xing_to_time_pos(xing, winds[0])
                        else:
                            value = xing
                        chan_xings.append(value)
                else:
                    if samp_corr:
                        value = self._xing_to_time_pos(xings[xing_num], winds[0])
                    else:
                        value = xings[xing_num]
                    chan_xings.append(value)
                # print(f"{chan_xings=}")
            all_chan_xings.append(chan_xings)

        return all_chan_xings

    def _xing_to_time_pos(self, xing, first_wind):
        samples = self.board.params.get("samples", 64)
        return (xing + (first_wind % 2) * samples) % (samples * 2)

    def _calc_dts(self, crossings):
        """
        Inputs a list containing the locations of zero crossings

        Calculates the timing calibration from this assuming that you expect an even distrubution

        Only for a *single channel*
        """
        bins = 2 * self.board.params.get("samples", 64)
        dt = (
            np.histogram(crossings % bins, bins, (-0.5, bins - 0.5), density=True)[0]
            * bins
        )
        positions = np.insert(np.cumsum(dt), 0, 0)[:-1]

        return positions - np.arange(0, bins)
