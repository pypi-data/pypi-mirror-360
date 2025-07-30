"""IO module

Collection of IO functions to support disk IO.
"""
import csv
import logging
import os

import numpy as np

LOGGER = logging.getLogger(__name__)


def get_csv_writer(params: dict):
    """Get the correct CSV writer for the board.

    Args:
        params (dict): board params.
        time_per_channel (bool): export time per channel rather than per row.
        include_timing (bool): include timing information in the CSV file.

    Returns:
        CSVWriter: CSV writer object.
    """
    try:
        model = params["model"]
    except Exception:
        model = None
    writer = CSVWriter
    if model in ["upac96", "udc16"]:
        writer = UpacCsvWriter

    return writer()


class CSVWriter:
    """
    CSV writer writes to CSV files.
    The CSV writer technically is two parts, a writer and a parser
    The parser is responsible for parsing the data into a format that the writer can write to disk.

    Attributes:
        time_per_channel (bool): export time per channel rather than per row.
        include_timing (bool): include timing information in the CSV file.
    """

    def export_acq_to_csv(
        self, filename: str, acqs: list, max_channels=None, time_per_channel=False
    ):
        """Exporting multiple acquisitions to a csv file.
        Args:
            filename (str): full filepath inlcuding directory and filename.
            acqs (list): list of acquisitions to export data from.
            max_channels (int): set the maximum channels to readout.
            time_per_channel (bool): export time per channel rather than per row.

        Output:
            csv file written to disk.
        """
        LOGGER.debug("Exporting %s acquisitions to csv", len(acqs))

        path, _ = os.path.split(filename)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a valid directory: {path}")
        if not isinstance(acqs[0], dict):
            events = self._compress_acquisitions(acqs)
        else:
            events = acqs
        self._export_acq_to_csv_per_event(
            filename, events, max_channels, time_per_channel
        )

    def _export_acq_to_csv_per_event(
        self, filename: str, events: list, max_channels=None, time_per_channel=False
    ):
        """Iterate over a list of events using a np.array buffer to write to a csv file on disk. Use if
        events are the same in size.

        Generate the event matrix by realigning the columns based on the window label.
        There is a master label list and all the other will be moved accordingly
        This means that the first label in the master label is used as a relative 0 x-axis
        All other data is moved accordngly

        Args:
            filename (str): full filepath inlcuding directory and filename.
            events (list): list of events to export data from.
            max_channels (int): set the maximum channels to readout.
            time_per_channel (bool): export time per channel rather than per row.

        Output:
            csv file written to disk.
        """
        num_events = len(events)
        num_channels = self._calculate_num_channels(events)
        include_timing = False
        decimals_to_round = 1
        # Override time_per_channel if window labels are not uniform in each event.
        if not self._check_window_label_uniformity(events):
            time_per_channel = True
        if events[0].get(
            "timing", False
        ):  # If data contains timing field, it must be included per channel
            time_per_channel = True
            include_timing = True

        csv_header = self._create_csv_header(
            num_channels, time_per_channel, include_timing
        )
        with open(filename, "w", newline="") as evt_file:
            header = ",".join(csv_header) + "\n"
            evt_file.write(header)

        num_columns = len(csv_header)  # Columns is common for all events

        for i, evt in enumerate(events):
            if "data" not in evt:
                LOGGER.debug("Event %s has no data, skipping", i)
                continue
            samples = self._calculate_sp_per_chan(evt)
            labels = self._calculate_window_labels(
                evt
            )  # Will produce errors on HDSoC no matter what
            rows = len(labels) * samples

            np_array = np.full(shape=(rows, num_columns), fill_value="", dtype=object)

            # write evt & acq column
            acq_col = 0
            evt_num_col = 1
            np_array[:, acq_col] = evt.get("acq_num", 0)
            np_array[:, evt_num_col] = evt.get("pkg_num", i)

            if not time_per_channel:
                window_label_col_idx = 2
                window_label_column = self._generate_label_column(labels, samples)
                np_array[:, window_label_col_idx] = window_label_column
            col_idx = 0
            for idx, data in enumerate(evt.get("data", list())):
                if (
                    len(data) == 0
                ):  # Channel isn't enabled if it has no corresponding window labels
                    continue
                xaxis = evt["time"][idx]
                win_labels = evt["window_labels"][idx]
                data_rows = self._get_start_end(
                    data, win_labels, labels, samples
                )  # Generates issues with HDSoC

                (
                    window_label_col_idx,
                    data_col_idx,
                    time_col_idx,
                    timing_label_col_idx,
                ) = self._generate_column_indexes(
                    col_idx, time_per_channel, include_timing
                )

                if time_per_channel:
                    window_label_column = self._generate_label_column(
                        win_labels, samples
                    )
                    np_array[data_rows, window_label_col_idx] = window_label_column

                if include_timing:
                    timings = evt["timing"][idx]
                    timings_column = self._generate_label_column(timings, samples)
                    np_array[data_rows, timing_label_col_idx] = timings_column

                if not isinstance(data[0], int):
                    data = np.round(
                        np.array(data).astype(float), decimals=decimals_to_round
                    )
                col_idx += 1

                np_array[data_rows, data_col_idx] = data
                np_array[data_rows, time_col_idx] = xaxis

            with open(filename, "a", newline="", buffering=10_000_000) as evt_file:
                np.savetxt(evt_file, np_array, fmt="%s", delimiter=",")

        LOGGER.info("Finished writing %d events to CSV", num_events)

    def _generate_label_column(self, labels: list[int], samples: int) -> np.array:
        """Generate a column of window labels for a single event.

        Window numbers start with the earliest window number then continues until all numbers have been listed.
        There can be holes in the window number but data will not "Wrap around", window labels will continue.

        Args:
            labels (list): list of window labels.
            samples (int): number of samples per window.

        Returns:
            np.array: array of window labels.
        """
        num_window_labels = len(labels)
        window_label_column = np.reshape(
            np.repeat(labels, samples), [samples, num_window_labels]
        ).flatten()
        return window_label_column

    def _generate_column_indexes(
        self, idx, time_per_channel: bool = True, include_timing: bool = False
    ) -> "tuple[int, int, int, int|None]":
        """Generate the column indexes for the np.array based on the time_per_channel flag.

        The two first columns are always the same, the rest is dependent on the time_per_channel flag.

        If time_per_channel is True, every three columns, are:
        window_label_X, data_X, time_X where X is the channel number.

        If time_per_channel is False, the third column is the time column and the rest are data columns.

        Args:
            time_per_channel (bool): export time per channel rather than per row.
            idx (int): index of the channel.
            include_timing (bool): include timing information in the CSV.

        Returns:
            tuple: window_label_col_idx, data_col_idx, time_col_idx
        """
        if time_per_channel:
            window_label_col_idx = 2 + ((3 + include_timing) * idx)
            data_col_idx = window_label_col_idx + 1
            time_col_idx = window_label_col_idx + 2
            timing_col_idx = window_label_col_idx + 3 if include_timing else None
        else:
            window_label_col_idx = 2
            data_col_idx = 4 + idx
            time_col_idx = 3
            timing_col_idx = None
        return window_label_col_idx, data_col_idx, time_col_idx, timing_col_idx

    def _get_start_end(self, data, win_labels, labels, samples) -> slice:
        """Get the start and end of the data in the np.array.

        Args:
            data (list): list of data.
            win_labels (list): list of window labels.
            labels (list): list of labels to export.
            samples (int): number of samples per window.

        Returns:
            slice: start and end of the data in the np.array.

        Raises:
            IndexError: if the label doesn't exist in the merged labels.
        """
        # create a data array with the correct number of rows and np.nan
        label_pos = np.where(win_labels[0] == labels)
        try:
            label_pos = (label_pos[0].astype(int) * samples)[0]
        except IndexError:
            LOGGER.debug("Label doesn't exist in the merged labels.")
            label_pos = 0

        start = label_pos
        end = start + len(data)
        return slice(start, end)

    @staticmethod
    def _compress_acquisitions(acquisitions):
        """Converts multiple acquisitions into a single
        acquistion.

        Args:
            acquisitions (list): A list of acquisition

        Returns:
            acquisition (list): Combined acquisition of all events
        """
        events = list()
        for acq in acquisitions:
            events.extend(acq)

        return events

    @staticmethod
    def _calculate_max_channels(events):
        """Calculates the maximum channels that exists of
        all events.

        Args:
            events (list): List of events, or acq

        Returns:
            max_chan (int): Max channels from all events
        """
        return max([len(x.get("data", list())) for x in events])

    def export_pedestals_csv(self, board, filename: str, pedestals: dict):
        """Export all data from the pedestals to CSV.

        Please note this will only export the data, not the information regarding the pedestals.
        This function also assumes filename is in the correct format.
        It will override any existing file.

        Args:
            board (Board): A board object with the pedestals data attached to it.
            filename (path): Filename for the csv file.
        """
        path, _ = os.path.split(filename)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a valid directory: {path}")

        max_channels = self._calculate_max_channels([pedestals])
        _csv_header = self._create_csv_header(max_channels, False)

        with open(filename, mode="w", newline="") as evt_file:
            writer = csv.writer(evt_file, delimiter=",")
            writer.writerow(_csv_header)
            peds_shape = pedestals["data"].shape
            sample_count = peds_shape[2]
            # sample_count = board.params["samples"]
            window_count = peds_shape[1]
            channels_count = peds_shape[0]
            for window in range(window_count):
                for sample in range(sample_count):
                    row = []
                    row.append(-1)  # acq number
                    row.append(-1)  # evt number
                    row.append(window)
                    row.append(window * sample_count + sample)  # timing

                    for channel in range(channels_count):
                        row.append(round(pedestals["data"][channel][window][sample], 2))
                    writer.writerow(row)

    @staticmethod
    def _create_csv_header(
        max_channels: "int|list",
        time_per_channel: bool = True,
        include_timing: bool = False,
    ) -> list[str]:
        """Creates the csv file header depending on number of channels.

        The determine the amount of channels the csv file need to handle.

        Args:
            max_channels(int|list): list of channels or amount of channels in the header.
            time_per_channel(bool): Add time and window columns per channel
            pedestals(bool): If true, add column for pedestals

        Returns:
            list of header labels
        """
        if isinstance(max_channels, int):
            channels = range(max_channels)
        elif isinstance(max_channels, list):
            channels = max_channels
        else:
            raise TypeError("max_channels must be an int or list")

        csv_header = ["acq_num", "evt_num"]
        if time_per_channel is False:
            csv_header.append("windnum")
            csv_header.append("time")
        for index in channels:
            if time_per_channel is True:
                csv_header.append("windnum_ch" + str(index))
            csv_header.append("data_ch" + str(index))
            if time_per_channel is True:
                csv_header.append("time_ch" + str(index))
            if include_timing is True:
                csv_header.append("timing_ch" + str(index))

        return csv_header

    def _calculate_num_channels(self, events) -> int:
        """Calculates the unique of channels in a list of events.

        Args:
            events (list): List of events

        Returns:
            int: Number of channels
        """

        if isinstance(events, dict):
            events = [events]
        channels = set()
        for event in events:
            data = event.get("data", None)
            if data is None:
                continue
            evt_chans = [i for i, d in enumerate(data) if len(d) > 0]
            channels.update(evt_chans)
        return list(channels)

    def _calculate_sp_per_chan(self, event):
        """Calculates the number of samples per channel in an event.

        It used the amount of window labels and the number of samples to calculate
        the number of samples per channel.
        """
        labels = [(i, x) for i, x in enumerate(event["window_labels"]) if len(x) > 0]
        ch = labels[0][0]  # Guaranteed data
        num_samps = len(event["data"][ch]) // len(labels[0][1])
        return num_samps

    def _calculate_window_labels(self, event: dict) -> list[int]:
        """Merges the window labels in order.

        Args:
            event: standard event format
            include_timing: include timing to determine start window

        Returns:
            A list of merged labels in order of appearance.
        """
        output = []
        nextround = [x for x in event["window_labels"] if len(x) > 0]
        while nextround:
            longest_remaining = max([len(x) for x in nextround])
            if longest_remaining == 0:
                break
            topop = CSVWriter()._calculate_first_window_idx(nextround)
            nxt_lbl = nextround[topop][0]
            if output:  # Guard against empty list
                if output[-1] != nxt_lbl:  # Guard against duplicates
                    output.append(nxt_lbl)
            else:
                output.append(nxt_lbl)
            available_labels = [y for y in nextround if len(y) > 0]
            nextround = [x[1:] if x[0] == nxt_lbl else x for x in available_labels]

        return output

    def _calculate_first_window_idx(self, alabels: list[list[int]]) -> int:
        """Calculates the index of the first window in the list of labels.

        Args:
            alabels: list of labels

        Returns:
            int: index of the first window
        """
        rollvers = [
            (p, i[0])
            for p, i in [(p, x) for (p, x) in enumerate(alabels) if len(x) > 0]
            if i[0] > i[-1]
        ]
        no_rollover = [
            (p, i)
            for p, i in [(p, x) for (p, x) in enumerate(alabels) if len(x) > 0]
            if i[0] < i[-1]
        ]

        first = []
        if rollvers:  # channel with rollovers
            # check if first is in the remaining alabels
            # if it is, then it can't be the first window
            output = []
            for f in rollvers:
                for n in no_rollover:
                    if f[1] in n[1]:
                        break
                    output.append(f)

            first = output

        if not first:
            first = [(pos, x[0]) for pos, x in enumerate(alabels) if len(x) > 0]

        topop = min(first, key=lambda x: x[1])  # smallest of the visible
        return topop[0]

    def _calculate_first_chan(self, event):
        """USes the timing labels to determine the first channel sampled.

        NNTE: lowest timing = first sampled data is an UNCONFIRMED assumption!
        """
        timings = [(i, x[0]) for i, x in enumerate(event["timing"]) if len(x) > 0]
        mintim = min(timings, key=lambda x: x[1])
        minidx = mintim[0]
        return event["window_labels"][minidx][0]

    def _check_window_label_uniformity(self, events: list[dict]) -> bool:
        """Will return true if all channels in every events in a list of events have the same window labels."""
        for event in events:
            labels = event.get("window_labels", None)
            if labels is None:
                continue
            labels = [x for x in labels if len(x) > 0]
            chans = set()
            for ch in labels:
                chans.update(ch)
            for ch in labels:
                if len(ch) != len(chans):
                    return False

        return True

    def export_thresholdscan_to_csv(
        self,
        filename: str,
        trigger_values,
        threshold_results: np.array,
        channels: "list|None" = None,
    ):
        """Write the results of a threshold scan to a csv file.
        The file will be formatted such that rows correspond to threshold values and columns correspond to channels

        Expected file output:
            Trigger value,ch0,ch1,ch2,...
            5,0,0,0,...
            10,2000,2000,0,...
            ...

        Args:
            filename (str): full filepath of of csv file to write to
            trigger_values (Iterable[Int]): contains the values which the threshold value were triggered on
            threshold_outputs (np.array): An array of shape len(trigger_values) x num_channels
            channels (list[int] or None): List of channels to include, or None to include all channels

        Output:
            thresholdscan outputs to csv file
        """
        try:
            threshold_results.shape
        except AttributeError:
            raise TypeError(
                f"threshold_results should be a numpy array, got {type(threshold_results)}"
            )
        if channels is not None:
            channels = sorted(channels)
            threshold_results = threshold_results[:, tuple(channels)]
        else:
            channels = range(threshold_results.shape[1])

        if len(trigger_values) != threshold_results.shape[0]:
            raise ValueError(
                "The length of trigger values and thresholdscan values should match ({} vs {})".format(
                    len(trigger_values), threshold_results.shape[0]
                )
            )

        header = ["Trigger value"] + ["ch{}".format(x) for x in channels]
        with open(filename, "w", newline="") as dst:
            writer = csv.writer(dst)
            writer.writerow(header)
            for i, trig_val in enumerate(trigger_values):
                writer.writerow([trig_val, *threshold_results[i]])


class UpacCsvWriter(CSVWriter):
    def _export_acq_to_csv_per_event(
        self,
        filename: str,
        events: list,
        max_channels=None,
        time_per_channel: bool = True,
    ):
        """Iterate over a list of events using a np.array buffer to write to a csv file on disk. Use if
        events are the same in size.

        Generate the event matrix by realigning the columns based on the window label.
        There is a master label list and all the other will be moved accordingly
        This means that the first label in the master label is used as a relative 0 x-axis
        All other data is moved accordngly

        Args:
            filename (str): full filepath inlcuding directory and filename.
            events (list): list of events to export data from.
            max_channels (int): set the maximum channels to readout.
            time_per_channel (bool): export time per channel rather than per row.
                The value is ignored since the UDC data format requires time per window.

        Output:
            csv file written to disk.
        """
        time_per_channel = True
        num_events = len(events)
        num_channels = self._calculate_num_channels(events)

        decimals_to_round = 1

        csv_header = self._create_csv_header(
            num_channels,
            time_per_channel=time_per_channel,
            include_timing=False,
        )
        with open(filename, "w", newline="") as evt_file:
            header = ",".join(csv_header) + "\n"
            evt_file.write(header)

        num_columns = len(csv_header)  # Columns is common for all events

        for i, evt in enumerate(events):
            if "data" not in evt:
                LOGGER.debug("Event %s has no data, skipping", i)
                continue
            samples = self._calculate_sp_per_chan(evt)
            labels = max([len(x) for x in evt.get("window_labels", []) if len(x) > 0])
            rows = labels * samples

            np_array = np.full(shape=(rows, num_columns), fill_value="", dtype=object)

            # write evt & acq column
            acq_col = 0
            evt_num_col = 1
            np_array[:, acq_col] = evt.get("acq_num", 0)
            np_array[:, evt_num_col] = evt.get("pkg_num", i)

            if not time_per_channel:
                window_label_col_idx = 2
                window_label_column = min(
                    [x[0] for x in evt.get("window_labels", []) if len(x) > 0]
                )
                np_array[:, window_label_col_idx] = window_label_column
            col_idx = 0
            for idx, data in enumerate(evt.get("data", list())):
                if (
                    len(data) == 0
                ):  # Channel isn't enabled if it has no corresponding window labels
                    continue
                xaxis = evt["time"][idx]
                win_labels = evt["window_labels"][idx]
                data_rows = slice(0, len(data))
                (
                    window_label_col_idx,
                    data_col_idx,
                    time_col_idx,
                    timing_label_col_idx,
                ) = self._generate_column_indexes(
                    col_idx, time_per_channel, include_timing=False
                )

                if time_per_channel:
                    window_label_column = self._generate_label_column(
                        win_labels, samples
                    )
                    np_array[data_rows, window_label_col_idx] = window_label_column

                if not isinstance(data[0], int):
                    data = np.round(
                        np.array(data).astype(float), decimals=decimals_to_round
                    )
                col_idx += 1

                np_array[data_rows, data_col_idx] = data
                np_array[data_rows, time_col_idx] = xaxis

            with open(filename, "a", newline="", buffering=500_000) as evt_file:
                np.savetxt(evt_file, np_array, fmt="%s", delimiter=",")

        LOGGER.info("Finished writing %d events to CSV", num_events)
