"""Timing calibration correcter.

Corrects single and batches of events using a dt array.

"""
import numpy as np


class TimingCorrecter:
    """Correct the timing in an event.

    The timing in the delay line is not perfect and can be calibrated
    The chip clock is divided down 128 times by the DLL in the ASIC, the clock
    is reset at ech 128th window boundary, starting at 0.

    THe correcter takes the correction constants for 128 samples and applies to
    the events `time` field.
    """

    def __init__(self, timingcal):

        self.timingcal = timingcal

    def run(self, event):
        """Correct the time on a single event using the dts

        Args:
            event(dict):

        Returns:
            Timing corrected array
        """
        try:
            shp = event["data"].shape
        except AttributeError:
            shp = (len(event["data"]), len(event["data"][0]))
        corr_times = np.zeros(shp)
        dts = self.timingcal

        for chan, windows in enumerate(event["window_labels"]):
            read_winds = len(windows)

            # if a channel has no data
            if read_winds == 0:
                corr_times[chan] = np.nan
                continue

            # Make sure the tile is larger than the following data
            # Make longer to handle uneven amounts of windows
            time_corrs = np.tile(dts, int(np.round(read_winds / 2)) + 2)

            odd_start_window = self._check_odd_startwin(windows)

            if odd_start_window:
                time_corrs = time_corrs[64:-64]
            else:
                time_corrs = time_corrs[:-128]
            time_corrs = time_corrs[: shp[1]]

            corr_time = np.arange(len(time_corrs)) + time_corrs

            corr_times[chan] = corr_time

        return corr_times

    def _check_odd_startwin(self, windows):
        """Returns True if start window is odd"""
        return windows[0] % 2 == 1

    def batch_correct(self, events):
        """
        input a full acqusition and it will add a corrected_time field to each event

        that uses the dts provided
        """

        for event in events:
            corr_time_dict = {}
            corr_times = self.run(event)
            corr_time_dict["corrected_times"] = corr_times
            event.update(corr_time_dict)
