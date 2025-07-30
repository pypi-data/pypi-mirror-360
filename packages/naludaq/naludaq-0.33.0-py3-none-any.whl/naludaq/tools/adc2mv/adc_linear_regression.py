# Builtin
from logging import getLogger

# 3rd Party
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Internal
from naludaq.board import Board
from naludaq.helpers.helper_functions import type_name

LOGGER = getLogger(__name__)


class ADCLinearReg:
    """
    This class utilizes DAC sweep data collected from the dac sweep controller,
    and is used to calculate two values: linear region and linear regression.
    For linear region, it finds the largest region that is linear, defined by
    R-squared parameters. For linear regression, the slope and intercept  is
    calculated for each sample in each channel. Unless a linear region is
    defined, it will calculate the slope and intercept using the region closest
    to 600-1000 mV.

    Args:
        board (naludaq.board): Board object used for params.
        min_dac_val (int or list): The beginning of the linear region in mV
        max_dac_val (int or list): The ending of the linear region in mV

    Raises:
        TypeError if the board parameter is not a valid type
        InvalidBoardModelError if the provided str for the board model is invalid.

    """

    def __init__(self, board: Board):
        if not isinstance(board, Board):
            raise TypeError(
                f"Invalid board type. Got {type_name(board)}, expected Board"
            )
        self.board = board
        self.channels = self.board.params["channels"]
        self.min_dac_val = None
        self.max_dac_val = None
        self._progress: list = []
        self._cancel = False

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError("Progress is stored in a list")
        self._progress = value

    def cancel(self):
        """Cancels the linear regression as soon as possible.
        No data is generated, and the `linear_regression` function
        will return `None`.

        Can only be called from a separate thread.
        """
        self._cancel = True

    def linear_regression(
        self, dac_data: dict, minimum_r2: float = 0.9998, minimum_range: int = 10
    ) -> dict:
        """Calculate the slope and intercept per sample using dac sweep data.

        Args:
            dac_data (dict): DAC sweep data collected from dac_sweep_controller
            minimum_r2 (float): The minimum R-squared value a region needs to be considered
                linear.
            minimum_range (int): The minimum number of points within the two endpoints to
                be considered a region. Used to optimize calculations of endpoints.
        Returns:
            lr_dict (dict): Contains slope & intercept of every sample per channel,
                formatted as:
                    {
                        "slope": 2D Array, channel major, sample minor,
                        "intercept": 2D Array, channel major, sample minor,
                        "linear_region": list of minmax tuples per channel
                    }
                Will return None if the operation was canceled.

        Raises:
            NoLinearRegionFoundError: No linear region was found for a channel.
        """
        self._cancel = False

        average_per_sample = list()
        sample_intercept = []
        sample_slope = []

        voltages = list(dac_data.keys())
        LOGGER.info("Voltages: %s", voltages)

        voltages = self._dac2mv(np.array(voltages))
        LOGGER.info("Converted voltages: %s", voltages)
        # Format data in form average_per_sample[channel #][sample #][dac_val]
        LOGGER.info("Reformatting DAC Sweep data")
        self.progress.append(
            (
                0,
                "Formatting DAC Sweep Data",
            )
        )
        average_per_sample = self._format_dac_sweep_to_sample(dac_data)

        _, out_minmax = self._linear_region(dac_data, minimum_r2, minimum_range)

        # Intercept and slope per sample
        for chan in range(self.channels):
            if self._cancel:
                return None

            if self.min_dac_val[chan] is None or self.max_dac_val[chan] is None:
                LOGGER.error(
                    f"Channel {chan} does not have a \
                linear region!"
                )
                continue
            LOGGER.info(f"Calculating slope & int. for channel {chan}")
            self.progress.append(
                (
                    int(20 + 80 * ((chan) / self.channels)),
                    f"Performing Linear Regression for Channel {chan}",
                )
            )
            sample_int, sample_s = self._linear_reg_for_multi_samples(
                voltages,
                average_per_sample[chan],
                vrange=(self.min_dac_val[chan], self.max_dac_val[chan]),
            )
            sample_intercept.append(sample_int)
            sample_slope.append(sample_s)

        if self._cancel:
            return None

        self.progress.append((100, "Linear Regression Completed"))

        lr_dict = {
            "slope": sample_slope,
            "intercept": sample_intercept,
            "linear_region": out_minmax,
        }

        return lr_dict

    def _linear_region(
        self, dac_data: dict, minimum_r2: float = 0.9998, minimum_range: int = 10
    ):
        """Detect the linear region
        Given a DAC Sweep, this will detect the linear region by taking all possible
        combination of two endpoints and calculate the linear regression and r-squared
        value. If it is above the minimum values, it will prefer the endpoints which
        give a greater range. If there are multiple pairs of endpoints with the same range,
        it will prefer the one with a higher r-squared value.

        Args:
            dac_data (dict): DAC sweep data collected frmo dac_sweep_controller
            minimum_r2 (float): The minimum R-squared value a region needs to be considered
                linear.
            minimum_range (int): The minimum number of points within the two endpoints to
                be considered a region. Used to optimize calculations of endpoints.

        Returns:
            out_r2 (list): Floats of R-squared value of the detected region
            out_minmax (list): Tuples of start and ending points of the linear region,
                given as mV.

        """
        voltages = self._dac2mv(np.array(list(dac_data.keys())))
        self.min_dac_val = [None] * self.channels
        self.max_dac_val = [None] * self.channels
        average_per_channel = [[] for _ in range(self.channels)]

        new_data_array = self._remove_peds_dict_from_dac_sweep(dac_data)

        # Mean the data points so average_per_channel[Channel #][DAC #]
        average_per_channel = np.swapaxes(np.mean(new_data_array, axis=(2, 3)), 0, 1)

        out_r2, out_minmax = self._scan_linear_region(
            voltages, average_per_channel, self.channels, minimum_r2, minimum_range
        )
        return out_r2, out_minmax

    def _scan_linear_region(
        self,
        voltages,
        average_per_channel,
        num_channels,
        minimum_r2,
        minimum_range,
    ):
        """Scans the dataset for the linear region.

        The average per channel is a curve made of the averages of all the data.
        The method uses grid search to check for the two end points with the lowest
        r2 score between them.

        TODO: Horrendously slow, this detection is not exact and is very slow O(n^2).
        Takes the average for a channel and tries to find the endpoints

        Args:
            voltages:
            average_per_channel:
            num_channels:
            minimum_r2:
            minimum_range:
        """
        out_r2 = [0] * num_channels
        out_minmax = [(0, 0) for _ in range(num_channels)]
        for chan in range(num_channels):
            max_range = 0
            for i in range(0, len(voltages) - minimum_range):
                for j in range(i + minimum_range, len(voltages)):
                    r2_xdata = []
                    intercept, coeff = self._single_sample_lr(
                        voltages[i:j], average_per_channel[chan][i:j]
                    )
                    r2_xdata.append(np.array(coeff) * voltages[i:j] + intercept)
                    r2 = r2_score(r2_xdata[0], average_per_channel[chan][i:j])
                    # Checks to see if the current endpoints are better than the current best
                    if r2 >= minimum_r2:
                        # We want as big of a range as possible
                        if (j - i) > max_range:
                            max_range = j - i
                            out_r2[chan] = r2
                            out_minmax[chan] = (int(voltages[i]), int(voltages[j]))
                        # If its the same size, we want to keep the better r2 value
                        elif (j - i) == max_range:
                            if r2 > out_r2[chan]:
                                out_r2[chan] = r2
                                out_minmax[chan] = (int(voltages[i]), int(voltages[j]))
            # Did not find a linear region
            if out_r2[chan] == 0:
                LOGGER.error(f"Did not detect a linear region in channel {chan}")
            else:
                self.min_dac_val[chan] = out_minmax[chan][0]
                self.max_dac_val[chan] = out_minmax[chan][1]
        return out_r2, out_minmax

    def _remove_peds_dict_from_dac_sweep(self, dac_data: dict):
        """Removes the pedestals dictionary from a dac sweep, replacing
        each event dict with peds['data'], and reformats array to
        recognize the newly added dimensions from the data array."""
        # TODO: Change DAC sweep data format to be dict major first,
        # So this function will be obsolete. Ex. dacdata['data'][0][0][0][0][0]
        try:
            new_data = np.array([dac_peds["data"] for dac_peds in dac_data.values()])
        except KeyError:
            LOGGER.error(
                "DAC sweep data does not contain 'data' key. \
                Please check the data format."
            )
            raise

        return new_data

    def _format_dac_sweep_to_sample(self, indata):
        """
        Changes the data format of dac sweep data to be sample major,
        dac val minor, for a specific channel. (outdata[sample #][dac_val])
        Args:
            indata (dict): DAC Sweep Data

        Returns:
            outdata (nparray): Data sample major, dac val minor
        """

        linearity_data = self._create_linearity_data(indata)
        averaged_data = []
        # average the 10 acquisitions for each capture
        for dac_val, dac_data in linearity_data.items():
            averaged_data.append(dac_data)

        sample_data = []
        for item in averaged_data:
            sample_data.append(item)
        # sample_data is in format sample_data[dac val][channel #][sample #]
        # fixed_sample_data: fixed_sample_data[channel #][sample #][dac val]
        fixed_sample_data = np.moveaxis(np.array(sample_data), 0, 2)
        return fixed_sample_data

    def _linear_reg_for_multi_samples(self, voltages, sample_data, vrange=(600, 1000)):
        """Run linear regression for each samples in the data.

        voltages is the xaxis and sample_data a multidim y_axis.
        By running it for each sample two arrays with 1.intercepts and 3. coeffs are returned.

        Args:
            voltages: voltages for the xaxis
            sample_data: matrix of datapoints for each samples along the voltage axis
            vrange: (min, max) voltages for the linear region in the data.

        Returns:
            list of intercepts, list of coefficients (`slopes`)
        """
        minv = self._find_nearest(voltages, vrange[0])
        maxv = self._find_nearest(voltages, vrange[1])
        intercepts = np.array([])
        slopes = np.array([])
        for sample in sample_data:
            intercept, slope = self._single_sample_lr(
                voltages[minv:maxv], sample[minv:maxv]
            )
            intercepts = np.append(intercepts, intercept)
            slopes = np.append(slopes, slope)

        return intercepts, slopes

    def _single_sample_lr(self, xdata, ydata):
        """Perform lienar regression of the provided samples.

        length of xdata and ydata must match or the linear regression will fail.

        Args:
            xdata: list of values along the xaxis
            ydata: list of values for the yaxis

        Returns:

        """
        if type(xdata) is list:
            xdata = np.array(xdata)
        reshaped_x = xdata.reshape(-1, 1)
        regressor = LinearRegression()
        regressor.fit(reshaped_x, ydata)

        return regressor.intercept_, regressor.coef_

    def _find_nearest(self, array, value):
        """Find the index of the sample in `array` with the value nearest `value`

        Subtract the value from the array and return the index with the smallest difference.

        Args:
            array: list of values
            value: target value to reference with `array` values

        Returns:
            index of the closest sample
        """
        array = np.asarray(array)
        idx = (
            np.abs(array - value)
        ).argmin()  # Returns the indices of the minimum values along an axis.
        return idx

    def _create_linearity_data(self, indata: dict):
        """Create linearity data by reshaping the pedestals data

        The pedestals data is in the format: [Channels][Windows][Sample],
        This function will flatten out all the samples into:
        [Channels][Windows * Samples]

        Args:
            indata: {dac_val, pedestals_data}

        Returns:
            {dac_val, pedestal_data_by_samples}
        """
        outdata = {}
        for dac_val, data in indata.items():
            data_array = np.array(data["data"])
            channels = data_array.shape[0]
            outdata[dac_val] = data_array.reshape((channels, -1))

        return outdata

    def _dac2mv(self, dac_val):
        return (
            dac_val
            * self.board.params["ext_dac"]["max_mv"]
            / (self.board.params["ext_dac"]["max_counts"])
        )
