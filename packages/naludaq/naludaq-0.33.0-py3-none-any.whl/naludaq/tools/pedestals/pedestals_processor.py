import numpy as np


def process_peds(pedestals, filter_outlier=True, filter_threshold=10, channels=None):
    """Filters the outliers from data and rawdata and finds std values for rawdata.

    This function will remove outliers from a copy of pedestals unless specified, leaving the input
    pedestals untouched.

    Args:
        pedestals (dict): Pedestals with params "data" and "raw_data"
        filter_outlier (bool): True to filter outliers
        filter_threshold (float): The modified z-score used to determine if a point is an outlier.
        channels (list): The channels to process peds

    Returns:
        ped (dict):
            Processed pedestal data with keys: "data" & "std_data" and
            "num_removed" if filter_outlier is enabled, with channels in
            the order of the channels argument.
    """
    num_channels = pedestals["params"]["channels"]
    return_ped = {
        "data": [[] for _ in range(num_channels)],
        "std_data": [[] for _ in range(num_channels)],
    }

    if channels is None:
        channels = range(0, pedestals["params"]["channels"])
    if filter_outlier:
        return_ped["num_removed"] = {
            "data": [0] * num_channels,
            "std_data": [0] * num_channels,
        }

    for chan in channels:
        ped_data = np.hstack(pedestals["data"][chan])
        if pedestals["params"]["model"] == "hdsocv1":
            stitched_rawpeds = []
            lengths = [len(p) for p in pedestals["rawdata"][chan]]

            for i in range(min(lengths)):
                window = [p[i] for p in pedestals["rawdata"][chan]]
                stitched_rawpeds.append(np.hstack(window))

            ped_stddata = np.std(stitched_rawpeds, axis=0)
        else:
            ped_stddata = np.std(pedestals["rawdata"][chan], 2).flatten()
        if filter_outlier and not np.all(
            ped_data == ped_data[0]
        ):  # Filter outliers utilizing a modified z-score
            data_length = len(ped_data)
            stddata_length = len(ped_stddata)
            ped_data = filter_outliers(ped_data, filter_threshold)
            ped_stddata = filter_outliers(ped_stddata, filter_threshold)
            return_ped["num_removed"]["data"][chan] = data_length - len(ped_data)
            return_ped["num_removed"]["std_data"][chan] = stddata_length - len(
                ped_stddata
            )
        return_ped["data"][chan] = ped_data
        return_ped["std_data"][chan] = ped_stddata

    return return_ped


def is_outlier(data, thresh=3.5, axis=-1):
    """Using a modified Z-score to detect outliers.

    Returns a boolean array with True if points are outliers and False
    otherwise.

    Args:
        data (np.array): numpy array of data
        thresh (float) : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.
        axis (int): Axis along which to compute & sum the modified z-score. Default is -1

    Returns:
        A numobservations-length boolean array.

    References:
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.
    """
    if len(data.shape) == 1:
        data = data[:, None]
    median = np.median(data)
    diff = (data - median) ** 2
    if axis:
        diff = np.sum(diff, axis=axis)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)
    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh


def filter_outliers(data, thresh):
    """Filter outliers from the data and return data without outliers.

    This function doesn't give an indication of where the outliers are, it just removes them.
    Useful to run before plotting data to remove outliers.

    Args:
        data (np.array): data array to filter
        thresh: Z-value threshold, see `is_outlier` function description.

    Returns:
        filtered np.array
    """

    indexes = np.where(is_outlier(data, thresh) is False)  # invert

    modified_data = data[indexes]

    return modified_data
