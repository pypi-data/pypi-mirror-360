"""Parser

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

import numpy as np

from naludaq.helpers.exceptions import BadDataError, IncompatibleParserError
from naludaq.parsers.headers import get_header_parser

LOGGER = logging.getLogger(__name__)


class Parser:
    """Class containing the parsers.

    Functions:
    ----------
        parse: Parse the raw event based on set parameters.
        parse_digital_data: raw event to a dict, no time.

    Args:
        params (dict): Contains hardware parameters.
        minimum_params = {
            'channels': amount of channels,
            'samples': amount of samples,
            'chanmask': bits for channels in the window headers,
            'windmask': bits for windows number in the window headers,
            'chanshift': bits the channel number is shifted up in windows headers,
            'headers': expected amount of event headers,
        }

    Attributes:
        num_wind_headers (int): Number of window  headers
        num_footers (int): Number of bytes in the footer
        last_bits (int): how many bits in the end of the word.
        data_bitmask (int): bits of data before shifting last bit
    """

    def __init__(self, params):
        self.params = params
        self.samples = params["samples"]
        self.channels = params["channels"]
        self.windows = params["windows"]
        self._parse_event_headers = get_header_parser(self.params["model"])
        self.num_wind_header = 1
        self.num_footers = 2
        self.last_bits = self.params.get("lastbits", 1)
        self.data_bitmask = 8191
        self.validation_patterns = None
        # Default to old behaviour.
        if self.params["model"] == "aardvarcv3":
            raise IncompatibleParserError(
                "This parser is not compatible with AARDVARCv3 data."
            )
        elif self.params.get("use_new", False) is True:
            self.parse_digital_data = self.parse_digital_data_new
        else:
            self.parse_digital_data = self.parse_digital_data_old

    def parse(self, raw_data, *args, **kwargs) -> dict:
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
            # raise Exception(f'parse_digital_data failed: {e_msg}')
        else:
            # Add the X-Axis.
            event["time"] = self._add_xaxis_to_event(event)

            event["created_at"] = raw_data.get("created_at", 0)
            event["pkg_num"] = raw_data.get("pkg_num", 0)
            event["event_num"] = raw_data.get("pkg_num", 0)

        event["name"] = None

        return event

    def parse_digital_data_new(self, in_data) -> dict:
        """Parse the raw data from the board.

        Parses the data spit out by the digitial readout portion of the firmware

        Args:
            in_data (bytearray): Raw data from the board
        Returns:
            Parsed event as a dict.
        Raises:
            BadDataException if no data is found or if the data contains errors.

        Additional info:
        The word is 16-bit and the data is 12-bit.
        0x00 is not a valid byte, ever

        Example format for ASoC:
        first three bits are the "identifier", last bit is always 1
        4 x event headers:
          '001' 'prev_final_window' '1'
          '001' 'trigger_time_ns(23 dt 12)' '1'
          '001' 'trigger_time_ns(11 dt 0 )' '1'
          '001' 'eventNumber' '1'
        { 1x *digitization header*:
          "001" '12-bit timer' '1'
         [ 1x window header:
          '100' 'chan' '00' 'window' '1'
          64x data packets
           '100' 'data' '1'
           ] for every channel
          } for every window
        1x end packet (x"FACE")

        """
        # try:
        #    self._validate_input_package(in_data)
        # except:
        #    raise
        # Convert the 8-bit binary to 16-bit unsigned int and bit mask+shift the entire array
        raw_data = np.frombuffer(in_data["rawdata"], dtype=">H")
        bitshifted_data = self._bitshift_data(raw_data)
        curr_event = {
            "window_labels": [[] for _ in range(self.params["channels"])],
            "data": [[] for _ in range(self.params["channels"])],
            "start_window": (raw_data[self.params["headers"]] & self.params["windmask"])
            >> 1,
            "digitize_times": list(),
        }

        self._parse_event_headers(curr_event, bitshifted_data)

        # Determine how many digitization headers there are
        num_headers = self.params["headers"]
        identifiers = raw_data >> 13
        dig_head_locs = np.where(identifiers == 1)[0][num_headers:]
        num_dig_headers = len(dig_head_locs)
        curr_event["num_dig_headers"] = num_dig_headers
        curr_event["digitize_times"] = bitshifted_data[dig_head_locs]
        LOGGER.debug("dig_times:%s", curr_event["digitize_times"])

        # Move through data one window at the time.
        data_locs = np.where(identifiers == 4)[0]
        LOGGER.debug("data_locs:%s", data_locs)
        step_size = self.num_wind_header + self.params["samples"]
        for window_idx in data_locs[::step_size]:
            # Extract the window header data
            channel = (raw_data[window_idx] & self.params["chanmask"]) >> self.params[
                "chanshift"
            ]
            window = (raw_data[window_idx] & self.params["windmask"]) >> self.last_bits
            curr_event["window_labels"][channel].append(window)

            curr_event["data"][channel].extend(
                bitshifted_data[
                    window_idx + 1 : window_idx + (self.params["samples"] + 1)
                ]
            )

        curr_event["data"] = np.array(curr_event["data"])

        return curr_event

    def parse_digital_data_old(self, in_data) -> dict:
        """Parse the raw data from the board.

        Parses the data spit out by the digitial readout portion of the firmware

        Args:
            in_data (bytearray): Raw data from the board
        Returns:
            Parsed event as a dict.
        Raises:
            BadDataException if no data is found or if the data contains errors.

        Additional info:
        The word is 16-bit and the data is 12-bit.
        0x00 is not a valid byte, ever

        Example format for ASoC:
        first three bits are the "identifier", last bit is always 1
        4 x event headers:
          '001' 'prev_final_window' '1'
          '001' 'trigger_time_ns(23 dt 12)' '1'
          '001' 'trigger_time_ns(11 dt 0 )' '1'
          '001' 'eventNumber' '1'
        1x window header:
          '010' 'chan' '00' 'window' '1'
        64x data packets
          '100' 'data' '1'
        1x end packet (x"FACE")

        """
        try:
            self._validate_input_package(in_data)
        except:
            raise
        # Convert the 8-bit binary to 16-bit unsigned int and bit mask+shift the entire array
        raw_data = np.frombuffer(in_data["rawdata"], dtype=">H")
        bitshifted_data = self._bitshift_data(raw_data)

        curr_event = {
            "window_labels": [[] for _ in range(self.params["channels"])],
            "data": [[] for _ in range(self.params["channels"])],
            "start_window": (raw_data[self.params["headers"]] & self.params["windmask"])
            >> self.last_bits,
        }

        self._parse_event_headers(curr_event, bitshifted_data)

        # Move through data one window at the time.
        num_headers = self.params["headers"]
        data_end = len(bitshifted_data) - self.num_footers
        step_size = self.num_wind_header + self.params["samples"]
        for window_idx in range(num_headers, data_end, step_size):
            # Extract the window header data
            channel = (raw_data[window_idx] & self.params["chanmask"]) >> self.params[
                "chanshift"
            ]
            window = (raw_data[window_idx] & self.params["windmask"]) >> self.last_bits
            curr_event["window_labels"][channel].append(window)

            curr_event["data"][channel].extend(
                bitshifted_data[
                    window_idx + 1 : window_idx + (self.params["samples"] + 1)
                ]
            )

        curr_event["data"] = np.array(curr_event["data"])

        return curr_event

    def _validate_input_package(self, in_data):
        """Validate the input data.

        Raises:
            BadDataException if:
            - there is no data.
            - there is not a en event amount of bytes, since 8-bits are combined to 16-bit words.
            - the data is not divisable by sample_num + window_headers.
        """
        if not isinstance(in_data, dict):
            raise TypeError("raw_data is not a dict it's a %s", type(in_data))

        if "rawdata" not in in_data or in_data["rawdata"] == b"":
            raise BadDataError("No Data Found")

        # Edge case, data doesn't contain valid words.
        if len(in_data["rawdata"]) % 2 != 0:
            raise BadDataError(
                f"Bad package no {in_data.get('pkg_num', 'unknown')}, "
                f"length is not an even amount of words, "
                f"len {len(in_data['rawdata'])}"
            )

        # Split this validation into it's own package.
        if self.params["model"] != "aardvarcv3":
            if (len(in_data["rawdata"]) // 2 - self.params["headers"] - 1) % (
                self.params["samples"] + 1
            ) != 0:
                raise BadDataError(
                    f"Bad package no {in_data.get('pkg_num', 'unknown')}"
                    f", length is not dividable by window sizes,"
                    f" len {len(in_data['rawdata'])}"
                )

    def _bitshift_data(self, raw_data):
        """Bitshift and bitmask the data.

        The 12-bit data can be positioned differently in the 16-bit data.
        By moving the last_bits and changing the data_bit_mask it's possbile to
        have data of various bit-length and position.
        """
        return (raw_data & self.data_bitmask) >> self.last_bits

    def _add_xaxis_to_event(self, event):
        """Adds an x-axis to the data.

        Based on the amount of channels and samples it will add a timeaxis
        per channel to the event dict.

        Returns:
            numpy array with sample numbers for each channel.
        """
        times = list()
        samples = self.samples
        channels = self.channels
        start_window = event["start_window"]
        for chan in range(0, channels):
            # LOGGER.debug("winds=%s", event["window_labels"][chan])
            winds = np.array(event["window_labels"][chan], dtype="int32")
            winds += self.windows * (winds < start_window)
            winds -= start_window

            tim = (samples * np.repeat(winds, samples)) + (
                np.ones((len(winds), samples), dtype=int)
                * np.arange(0, samples, dtype=int)
            ).flatten()

            times.append(tim)

        return times
