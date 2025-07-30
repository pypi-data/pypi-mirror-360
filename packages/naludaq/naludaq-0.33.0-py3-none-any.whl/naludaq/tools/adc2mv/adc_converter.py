"""Convert ADC 2 mV.

Tool to convert the data fields in an event dict from ADC counts to mV.
It requires the board to have calibration data loaded as an attribute `caldata`


"""
# import operator
# import pathlib
from copy import deepcopy

import numpy as np

# from naludaq.board import Board
from naludaq.tools.lookup_table import LookupTable

# from nalu_analyzer.helper_functions import open_data


class ADC2mVConverter:
    def __init__(self, params: dict = None, caldata: dict = None):
        self._caldata = None
        self.lr_dict = dict()
        self.params = params
        self.caldata = caldata

    @property
    def caldata(self):
        """Get/Set the calibration data.

        {
            "slope": 2D Array, channel major, sample minor,
            "intercept": 2D Array, channel major, sample minor,
            "linear_region": list of minmax tuples per channel
        }
        """
        return self._caldata

    @caldata.setter
    def caldata(self, caldata):
        self._caldata = caldata

    def run(self, event: dict, immutable: bool = True, lin_shift: bool = False) -> dict:
        """Convert the data field from adc counts2 mV.

        Args:
            evt: event to correct, must contain a data field
            immutable: Overwrite original or create a copy
            lin_shift: linear correction constants

        Returns:
            converted event or original event if there's no data field.
        """
        if event.get("data", None) is not None:
            return_evt = self._adc2mv_sample(event, immutable, lin_shift)
        else:
            return_evt = event
        return return_evt

    def _adc2mv_sample(
        self, evt: dict, immutable: bool = True, lin_shift: bool = False
    ):
        """Converts ADC to mV using correction constants for each sample.

        This function iterates of each individial sample and correct it.
        The function can either overwrite the original event or create a copy.
        Note the copy operation is time consuming.

        Args:
            evt: event to correct, must contain a data field
            immutable: Overwrite original or create a copy
            lin_shift: linear correction constants

        Returns:
            New converted event if immutable is True, else converts the input event.
        """
        evt_out = evt
        if immutable:
            data_mv_evt = deepcopy(evt)
            evt_out = data_mv_evt

        converted = list()

        window_labels = evt["window_labels"]

        samples = self.params["samples"]
        channels = self.params["channels"]

        for chan in range(channels):

            winds = window_labels[chan]
            num_winds = len(winds)
            if num_winds == 0:
                converted.append(np.array([], dtype="float"))
                continue

            locs = (samples * np.repeat(winds, samples)) + (
                np.ones((num_winds, samples), dtype=int)
                * np.arange(0, samples, dtype=int)
            ).flatten()

            try:
                if lin_shift:
                    converted.append(
                        self._inv_linear_shift(
                            evt_out["data"][chan],
                            slope=self.caldata["slope"][chan],
                            intercept=self.caldata["intercept"][chan],
                        )
                    )

                else:
                    converted.append(
                        self._inv_linear_function(
                            evt["data"][chan],
                            slope=self.caldata["slope"][chan].take(locs, mode="wrap"),
                            intercept=self.caldata["intercept"][chan].take(
                                locs, mode="wrap"
                            ),
                        )
                    )
            except:
                raise

        evt_out["data"] = np.array(converted)
        return evt_out

    def _linear_function(self, x_data, slope, intercept):
        """
        This function will apply a linear transformation on the x_data, in the form:
        return_data = (slope * x_data) + intercept.
        """
        return (np.array(slope) * x_data) + intercept

    def _inv_linear_function(self, x_data, slope, intercept):
        """
        This function will apply a inv. linear transformation on the x_data, in the form:
        return_data = (x_data - intercept) / slope
        """
        return (np.array(x_data) - intercept) / slope

    def _inv_linear_shift(self, x_data, slope):

        """
        This function will apply a inv. linear transformation on the x_data, in the form:
        return_data = (x_data - intercept) / slope
        """
        return (np.array(x_data)) / slope

    def _adc2mv_lookup(
        self, evt: dict, lookup_table: LookupTable, immutable: bool = True
    ):
        """Converts ADC to DAC using a lookup table

        This function iterates determines the corresponding sample number
        in the event, and determines the corresponding DAC value

        Args:
            evt: event to correct, must contain a data field
            lookup_table: lookup table containing ADC 2 DAC values
            immutable: Overwrite original or create a copy
        Returns:
            New converted event if immutable is True, else converts the input event.
        """
        evt_out = evt
        if immutable:
            evt_out = deepcopy(evt)

        converted = list()

        window_labels = evt["window_labels"]
        samples = self.params["samples"]
        channels = self.params["channels"]
        with lookup_table as lt:
            for chan in range(channels):
                channel_slice = np.array(lt[:, chan, :])
                winds = window_labels[chan]
                num_winds = len(winds)
                if num_winds == 0:
                    nan_arr = np.empty(samples * channels, dtype="float")
                    nan_arr = nan_arr.fill(np.nan)
                    converted.append(nan_arr)
                    continue

                data = np.array(evt_out["data"][chan])
                for wind_idx, wind in enumerate(winds):
                    # Get idxs of the data for samples in a window
                    start = wind_idx * samples
                    end = start + samples
                    adc_idx = data[start:end].astype(np.int64)
                    # Get idxs of the sample_num to be read from the lookup table
                    sample_start = wind * samples
                    sample_end = sample_start + samples
                    sample_num_idx = range(sample_start, sample_end, 1)
                    if np.isnan(channel_slice[adc_idx, sample_num_idx]).any():
                        raise LookupError(
                            "Lookup table is not filled, try interpolating empty values?"
                        )
                    data[start:end] = channel_slice[adc_idx, sample_num_idx]
                converted.append(data)

        evt_out["data"] = np.array(converted)
        return evt_out
