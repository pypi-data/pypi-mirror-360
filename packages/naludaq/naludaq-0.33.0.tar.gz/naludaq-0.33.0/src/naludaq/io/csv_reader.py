"""IO module

Collection of IO functions to support disk IO.
"""
import csv
import logging

import numpy as np

LOGGER = logging.getLogger(__name__)


def get_csv_reader(params: dict):
    """Get the correct CSV reader for the board.

    Args:
        params (dict): board params.
        time_per_channel (bool): export time per channel rather than per row.
        include_timing (bool): include timing information in the CSV file.

    Returns:
        CSVReader: CSV reader object.
    """
    try:
        model = params["model"]
    except Exception:
        model = None
    reader = CSVReader
    if model in ["upac96", "udc16"]:
        reader = UpacCsvReader

    return reader()


class CSVReader:
    """
    CSV reader reads from CSV files.
    The CSV reader technically is two parts, a reader and a parser
    The parser is responsible for parsing the data after the reader has read from disk.

    Attributes:
        time_per_channel (bool): export time per channel rather than per row.
        include_timing (bool): include timing information in the CSV file.
    """

    def import_acq_from_csv(self, filename, channels):
        """
        Reads a csv file that has stored events and stored that data into a
        variant of the acquisition structure, called a kacquisition. (Name is a WIP)
        The difference is that a kacq flattens all events into a single list

        Args:
            filename (str): Filename
            channels (list): Specific channels to parse out of the csv

        """
        if not isinstance(channels, list):
            raise TypeError(f"Expected chans to be list, got {type(channels)}")

        with open(filename) as open_file:
            csv_f = csv.reader(open_file)

            acq = {
                "evt_num": [],
                "windnum": [],
                "data": [],
                "time": [],
            }

            for chan in channels:
                acq["evt_num"].append([])
                acq["windnum"].append([])
                acq["data"].append([])
                acq["time"].append([])

            _ = next(csv_f)
            if _[0] == "acq_num":
                for row in csv_f:
                    for index, chan in enumerate(channels):
                        acq["evt_num"][index].append(int(row[1]))
                        acq["windnum"][index].append(int(row[(chan * 3) + 2]))
                        acq["data"][index].append(int(float(row[(chan * 3) + 3])))
                        acq["time"][index].append(int(row[(chan * 3) + 4]))
            else:
                for row in csv_f:
                    for index, chan in enumerate(channels):
                        acq["evt_num"][index].append(int(row[0]))
                        acq["windnum"][index].append(int(row[(chan * 3) + 1]))
                        acq["data"][index].append(int(float(row[(chan * 3) + 2])))
                        acq["time"][index].append(int(row[(chan * 3) + 3]))

        return acq

    def import_pedestals_from_csv(self, filename: str):
        """Reads pedestal data from a csv. Assumes the csv file is formatted like
        the ouput to io.csv_writer.CSVWriter.export_pedestals_csv

        Args:
            filename (path): Filename for the csv file.

        Output:
            dict in pedestal format
        """
        self._validate_csv_file(
            filename, ["acq_num", "evt_num", "windnum", "time"], ["data_ch"]
        )
        pedestals = []
        with open(filename, "r") as src:
            csv_src = csv.reader(src).__iter__()
            next(csv_src)  # Ignore header
            curr_window = 0
            window_vals = []
            for vals in csv_src:
                window = int(vals[2])
                if window != curr_window:
                    curr_window = window
                    pedestals.append(window_vals)
                    window_vals = []
                window_vals.append([float(val) for val in vals[4:]])

        # Check all same length
        for row in pedestals:
            if len(row) != len(pedestals[0]):
                raise ValueError(
                    "Incorrect CSV file - mismatch between window size in different windows"
                )

        # pedestals is now num_windows x num_samples x num_channels, reformat to num_channels x num_windows x num_samples
        pedestals = np.transpose(np.array(pedestals), (2, 0, 1))
        return {"data": pedestals, "raw_data": pedestals[:, :, :, np.newaxis]}

    def import_thresholdscan_from_csv(
        self, filename: str, num_channels: "int | None" = None
    ):
        """Read the results of a threshold scan from a csv file.
        Assumes the csv file is formatted like the output to io.csv_writer.CSVWriter.export_thresholdscan_to_csv

        Args:
            filename (str): full filepath of of csv file to read from
            num_channels (int or None): Number of channels to consider. If None, consider all channels in file.
                Channels not present in the file will be set to 1.

        Output:
            (threshold_values, trigger_values) where:
                threshold_values: np.array of threshold values in the shape len(trigger_values) x num_channels,
                trigger_values: list of trigger values used to generate threshold values
        """
        self._validate_csv_file(filename, ["Trigger value"], ["ch"])
        trigger_values = []
        threshold_values = []
        with open(filename, "r") as src:
            csv_src = csv.reader(src).__iter__()
            header = next(csv_src)
            channels = [int(s[2:]) for s in header[1:]]
            if num_channels is None:
                num_channels = max(channels) + 1
            for row in csv_src:
                trigger_values.append(int(row[0]))
                threshold_values.append([1] * num_channels)
                for ch, val in zip(channels, row[1:]):
                    try:
                        threshold_values[-1][ch] = float(val)
                    except IndexError:
                        pass  # ch > num_channels
        return np.array(threshold_values), trigger_values

    def _validate_csv_file(self, filename, prepended_headers, per_channel_headers):
        """Reads a csv file and validates that it is formatted as the given headers suggest

        Args:
            filename (str): full filepath of the csv file to validate
            prepended_headers (list[str]): list of headers at beginning
            per_channel_headers (list[str]): list of headers which are repeated per channel. Should not include channel number

        Ex:
            expected header: acq_num, evt_num, windnum, time, data_ch0, data_ch1, ...
            prepended_headers: acq_num, evt_num, windnum, time
            per_channel_headers: data_ch

        Returns:
            whether csv file is valid
        """
        NUMBERS = "0123456789"
        with open(filename, "r") as src:
            csv_src = csv.reader(src)
            csv_iter = iter(csv_src)
            header = next(csv_iter)
            header_iter = iter(header)

            # Check prepended headers
            for header_read, header_need in zip(header_iter, prepended_headers):
                if header_read != header_need:
                    raise ValueError(
                        "Incorrect CSV header - got {} but was expecting {}".format(
                            header_read, header_need
                        )
                    )

            # Check per channel headers
            channels = set()
            for col in header_iter:  # Check header_read subset header_need
                if (
                    col.rstrip(NUMBERS) not in per_channel_headers
                    or col in per_channel_headers
                ):
                    raise ValueError(
                        "Incorrect CSV header - got extraneous channel header {}".format(
                            col
                        )
                    )
                for i in range(len(col) - 1, 0, -1):
                    if col[i - 1] not in NUMBERS:
                        break
                channels.add(col[i:])
            for channel in channels:  # Check header_need subset header_read
                for head in per_channel_headers:
                    if head + channel not in header:
                        raise ValueError(
                            "Incorrect CSV header - did not find header {}".format(
                                head + channel
                            )
                        )

            # Check that row sizes match
            for i, row in enumerate(csv_iter):
                if len(row) != len(header):
                    raise ValueError(
                        "Incorrect CSV format - row {} wrong length ({} vs {})".format(
                            i + 1, len(row), len(header)
                        )
                    )
        return True


class UpacCsvReader(CSVReader):
    pass
