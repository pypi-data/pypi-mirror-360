"""ASoCv3Parser

Use parser to parse the data from the Hardware.
The boards sends a raw bitstream and it needs to be parsed into events.
The parser class is a tool to parse the raw bitstream of 8-bit chunks
into 16 bit words then extracting the 12-bit data, the header info,
channels and window number data.

This data is then returned in a dictionary.
The raw data is preserved.

This module was previously located under the naludaq.daq.workers
subpackage, and was relocated to improve the organization of the
naludaq package.
"""

import logging
from typing import List

import numpy as np

from naludaq.helpers.exceptions import BadDataError
from naludaq.parsers.parser import Parser

LOGGER = logging.getLogger("naludaq.hdsoc_parser")


class HDSoCParser(Parser):
    def __init__(self, params):
        super().__init__(params)
        self._stop_word = params.get("stop_word", b"\xfa\x5a")
        if isinstance(self._stop_word, str):
            self._stop_word = bytes.fromhex(self._stop_word)
        self._chan_mask = params.get("chanmask", 0x3F)
        self._chan_shift = params.get("chanshift", 0)
        self._abs_wind_mask = params.get("abs_wind_mask", 0x3F)
        self._evt_wind_mask = params.get("evt_wind_mask", 0x3F)
        self._evt_wind_shift = params.get("evt_wind_shift", 6)
        self._headers = params.get("headers", 4)
        self._timing_mask = params.get("timing_mask", 0xFFF)
        self._timing_shift = params.get("timing_mask", 12)
        self._packet_size = params.get("packet_size", 72)

    def _validate_input_package(self, in_data):
        """HDSoC: Splits the input package into a list of packets,
        and validates each packet based on a fixed size. Returns
        a list of only valid packets.

        Args:
            in_data (dict): Raw event structure from packager

        Raises:
            BadDataError: If all packets are bad

        Returns:
            split_in_data (list): List of validated packets
        """
        split_in_data = self._split_rawdata_into_packets(in_data["rawdata"])
        for packet in split_in_data:
            if len(packet) != self._packet_size:
                split_in_data.remove(packet)
        if split_in_data == []:
            raise BadDataError("Input package has no valid packets")
        return split_in_data

    def parse_digital_data_old(self, in_data) -> dict:
        """Parse the raw data from the board.

        Since the data packets are constant length, we can extract the data
        in place with matrix operations, speeding up the parsing.

        Args:
            in_data (bytearray): Raw data from the board

        Returns:
            Parsed event as a dict.

        Raises:
            BadDataException if no data is found or if the data contains errors.
        """
        try:
            input_packets = self._validate_input_package(in_data)
        except:
            raise

        num_packets = len(input_packets)
        raw_data_in = np.frombuffer(np.array(input_packets).flatten(), dtype=">H")
        raw_data = np.reshape(
            np.array(raw_data_in, dtype="uint16"), (num_packets, self._packet_size // 2)
        )
        abs_wind_mask = self._abs_wind_mask
        evt_wind_mask = self._evt_wind_mask
        evt_wind_shift = self._evt_wind_shift
        chan_shift = self._chan_shift
        chan_mask = self._chan_mask
        timing_mask = self._timing_mask
        timing_shift = self._timing_shift
        headers = self._headers

        curr_event = {
            "window_labels": [[] for _ in range(self.params["channels"])],
            "evt_window_labels": [[] for _ in range(self.params["channels"])],
            "data": [[] for _ in range(self.params["channels"])],
            "timing": [[] for _ in range(self.params["channels"])],
            "time": [[] for _ in range(self.params["channels"])],
        }
        np.arange(0, len(raw_data), self._packet_size // 2)
        chans = (raw_data[:, 0] >> chan_shift) & chan_mask
        abs_wins = raw_data[:, 3] & abs_wind_mask
        evt_wins = (raw_data[:, 3] >> evt_wind_shift) & evt_wind_mask
        p1 = np.uint32(raw_data[:, 1] & timing_mask) << timing_shift
        p2 = np.uint32(raw_data[:, 2] & timing_mask)
        timings = p1 | p2

        for i, packet in enumerate(raw_data):
            # If all data bytes are zero the window comes from a disabled channel.
            if packet[12] == 0:
                if np.all(packet[headers:] == 0):
                    continue

            channel = chans[i]  # (packet[0] >> chan_shift) & chan_mask
            abs_window = abs_wins[i]  # packet[3] & abs_wind_mask
            evt_window = evt_wins[i]  # (packet[3] >> evt_wind_shift) & evt_wind_mask
            timing = timings[i]
            curr_event["window_labels"][channel].append(abs_window)
            curr_event["evt_window_labels"][channel].append(evt_window)
            curr_event["timing"][channel].append(timing)
            curr_event["data"][channel].extend(packet[headers : headers + self.samples])
        curr_event["data"] = [np.array(x) for x in curr_event["data"]]
        return curr_event

    def _split_rawdata_into_packets(self, rawdata: bytearray) -> List[bytearray]:
        """Splits raw event data into packets.

        Args:
            rawdata (bytearray): the raw data to split

        Returns:
            A list of raw packets.
        """
        return rawdata.split(self._stop_word)

    def expand_cyclic_labels(self, row_labels):
        """
        Expand a 1D array of cyclic labels into a new 1D array,
        inserting np.nan wherever a label is skipped.

        Example for max_label=61:
        [3,6,7]   -> [3, nan, nan, 6, 7]
        [61,2,3]  -> [61, nan, nan, 2, 3]
        """
        max_label = self.params["windows"]
        row_labels = np.asarray(row_labels, dtype=np.int16)
        if len(row_labels) == 0:
            return np.array([], dtype=float)

        diffs = np.diff(row_labels)
        diffs = np.where(diffs < 0, diffs + (max_label), diffs)
        missing = (
            diffs - 1
        )  # subtract 1 because going from x to x+diffs includes (diffs-1) "skipped" values
        positions = np.zeros(len(row_labels), dtype=int)
        positions[1:] = np.cumsum(1 + missing)

        final_len = positions[-1] + 1
        out_array = np.full(final_len, np.nan, dtype=float)

        out_array[positions] = row_labels

        return out_array

    def _fix_missing_windows(self, event: dict) -> np.ndarray:
        """Expands the window labels to fill in missing windows with np.nan.

        Args:
            event (dict): The event to fix the missing windows in.

        Returns:
            np.ndarray: A 2D array with the missing windows filled with np.nan
        """
        labels_2d = event["window_labels"]

        expanded_rows = [self.expand_cyclic_labels(row) for row in labels_2d]

        max_len = max(len(r) for r in expanded_rows) if expanded_rows else 0
        result = np.full((len(expanded_rows), max_len), np.nan, dtype=float)

        for i, row_expanded in enumerate(expanded_rows):
            result[i, : len(row_expanded)] = row_expanded
        return result

    def expand_cyclic_data(self, row_data, row_labels):
        """
        Expand a 1D array of cyclic data into a new 1D array,
        inserting np.nan wherever a label is skipped.
        """
        samples = self.params["samples"]
        max_label = self.params["windows"]
        row_data = np.asarray(row_data)
        row_labels = np.asarray(row_labels, dtype=int)
        if len(row_data) == 0:
            return np.array([], dtype=float), np.array([], dtype=float)
        diffs = np.diff(row_labels)
        diffs = np.where(diffs < 0, diffs + (max_label), diffs)
        missing = (
            diffs - 1
        )  # subtract 1 because going from x to x+diffs includes (diffs-1) "skipped" values
        positions = np.zeros(len(row_labels), dtype=int)
        positions[1:] = np.cumsum(1 + missing)
        final_len = positions[-1] + 1
        data_array = np.full(final_len * samples, np.nan, dtype=float)
        time_array = np.full(final_len * samples, np.nan, dtype=float)
        datapositions = (positions[:, None] * samples + np.arange(samples)).ravel()
        data_array[datapositions] = row_data
        time_array[datapositions] = datapositions

        return data_array, time_array

    def _fix_missing_data(self, event: dict) -> np.ndarray:
        """Expands the data to fill in missing windows with np.nan.

        Args:
            event (dict): The event to fix the missing windows in.

        Returns:
            np.ndarray: A 2D array with the missing windows filled with np.nan
        """
        labels_2d = event["window_labels"]
        data_2d = event["data"]
        expanded_data = []
        expanded_time = []
        for row_data, row_labels in zip(data_2d, labels_2d):
            expanded_row, time_array = self.expand_cyclic_data(row_data, row_labels)
            expanded_data.append(expanded_row)
            expanded_time.append(time_array)

        max_len = max(len(r) for r in expanded_data) if expanded_data else 0
        data_axis = np.full((len(expanded_data), max_len), np.nan, dtype=float)
        time_axis = np.full((len(expanded_data), max_len), np.nan, dtype=float)

        for i, (data_expanded, time_expanded) in enumerate(
            zip(expanded_data, expanded_time)
        ):
            data_axis[i, : len(data_expanded)] = data_expanded
            time_axis[i, : len(time_expanded)] = time_expanded

        return time_axis, data_axis

    def _add_xaxis_to_event(self, event):
        """Adds an x-axis to the data.

        Based on the amount of channels and samples it will add a timeaxis
        per channel to the event dict.

        During certain readout modes the window labels are not aligning,
        This function accounts for that and moves the time axis accordingly.

        It uses the window labels to determine the time axis by finding the lowest
        window number and offsetting the time axis by that amount.
        The 0-time will be the first samples in the lowest window.

        Args:
            event (dict): The event to add the x-axis to.

        Returns:
            numpy array with sample numbers for each channel.
        """
        channels = self.channels
        maxlen = max([len(x) for x in event["data"]])
        xax = np.tile(np.arange(0, maxlen), channels).reshape(channels, maxlen)

        # Fill in data with np.nan if the window labels are not in order.
        # This operation is channel by channel since the first window label
        # is not necessarily the same for all channels.

        return xax

    def parse(self, raw_data) -> dict:
        """Parses raw_data into a dict.

        Parses the data from the raw event and strips the timestamp/id.
        An dict is created from the parsed data with the id preserved.

        Args:
            raw_data (bytes): Raw data packaged with a header and a stopword.
        Returns:
            dict.
        """
        event = {}
        try:
            event = self.parse_digital_data(raw_data)
        except (TypeError, Exception) as e_msg:
            LOGGER.exception("parse_digital_data failed: %s", e_msg)
            event = raw_data
        else:
            event["time"], event["data"] = self._fix_missing_data(event)
            event["window_labels"] = self._fix_missing_windows(event)
            event["created_at"] = raw_data.get("created_at", 0)
            event["pkg_num"] = raw_data.get("pkg_num", 0)
        event["event_num"] = raw_data.get("pkg_num", 0)
        event["name"] = raw_data.get("name", None)

        return event
