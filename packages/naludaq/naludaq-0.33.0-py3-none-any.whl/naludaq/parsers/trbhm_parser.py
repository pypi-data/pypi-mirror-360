import logging

import numpy as np

from naludaq.helpers.exceptions import BadDataError
from naludaq.parsers.headers import get_header_parser
from naludaq.parsers.parser import Parser

LOGGER = logging.getLogger(__name__)


class TRBHMParser(Parser):
    """Parser for the TRBHM data protocol.

    ```
    Dataformat:
        For EACH chip/window send:

        For UDP send the header in each package
        For UART send one header per event.
        Header
            1x16-bit chip number
            1x16-bit: active channels
            1x16-bit: number of windows in event
            1x16-bit event num
            1x16-bit: last written window (ASIC 1)
            2x16-bit: trigger time_ns (ASIC 2+3)

        Data
                1x channel header: 16-bit
                1x window header 16-bit
                64x data package 16-bit 0000_DDDD_DDDD_DDDD
            … x amount channels
        1x window header (AARDVARCv3 specific digitization timer)

        Footer
        FACE (only for UART, remove FACE in UDP)

        After all data for the event is sent (after final FACE):
        CAFE (Remove in UDP since reassemble happens with event num)

    ```
    Since the event package can contain 1-4 channels of data the window header position
    is hard to determine.

    The solution is to pre-generate all package length combinations and use as a lookup table.
    This allow us to quickly validate packages where channel amount is not ambiguous.

    IN the rare cases it's abiguous there is a test where it checks if window numbers are the same for
    each channel in a window package.

    """

    def __init__(self, params):
        self.params = params

        self._parse_event_headers = get_header_parser(self.params["model"])

        self.test_amount_windows = 3
        self.samples = self.params.get("samples", 64)
        self.windows = self.params.get("windows", 512)
        self.channels = self.params.get("channels", 4)

        self.num_evt_headers = self.params.get("num_evt_headers", 7)
        self.num_channel_headers = self.params.get("num_channel_headers", 2)
        self.num_window_headers = self.params.get("num_window_headers", 2)

        self.num_footer_words = self.params.get("num_footer_words", 1)

        self.chan_step_size = self.samples + self.num_channel_headers

        # Needed?
        self.num_chips = self.params.get("num_chips", 2)

        self.enabled_channels_offset = 1
        self.window_count_offset = 2

        self.trigger_time_offset = 5

        self.connection_type = "uart"

        # Generatethe valid bits dictionary
        # self.valid_bitlengths = self.create_valid_bitlengths()

    def parse(self, raw_data):
        """Parse raw data into an event dictionary

        Args:
            in_data (dict): a dictionary containing at least an entry:
                'rawdata' (bytearray) - the raw data to parse

        Returns:
            An event dictionary

        Raises:
            TypeError if `in_data` is not a dict
            BadDataError if there is no 'rawdata' entry, or if the data does not
                have an even number of bytes
        """

        event = {}
        try:
            # if self.connection_type == 'uart':
            event = self.parse_digital_data_uart(raw_data)
            # else:
            # return self.parse_digital_data_udp(in_data)
        except (TypeError, Exception) as e_msg:
            LOGGER.exception("parse_digital_data failed: %s", e_msg)
            event = raw_data
        else:
            # Add the X-Axis.
            event["time"] = self._add_xaxis_to_event(event)
            event["created_at"] = raw_data.get("created_at", None)
            event["pkg_num"] = raw_data.get("pkg_num", 0)
            event["event_num"] = raw_data.get("pkg_num", 0)
        event["name"] = None

        return event

    def parse_digital_data_uart(self, in_data):
        """Parse raw data into an event dictionary

        Args:
            in_data (dict): a dictionary containing at least an entry:
                'rawdata' (bytearray) - the raw data to parse

        Returns:
            An event dictionary

        Raises:
            TypeError if `in_data` is not a dict
            BadDataError if there is no 'rawdata' entry, or if the data does not
                have an even number of bytes
        """
        try:
            # make sure package contains data and there's an even amount of bytes to combine.
            self._validate_input_package(in_data)
        except:
            raise

        # Parsing variables
        num_chips = self.num_chips

        num_evt_headers = self.num_evt_headers
        num_window_headers = 2  # Move to params
        samples = self.samples
        channels_per_chip = 4  # Move to params

        channel_step_size = self.chan_step_size
        num_footer_words = self.num_footer_words

        channel_footers = 1  # AARDVARCv3 window timing footer
        # Split the event into the data for each chip
        data = np.frombuffer(in_data["rawdata"], dtype=">H")

        # enabled_channels = data[enabled_channels_offset] & enabled_channels_mask
        num_channels = 4  # bin(enabled_channels).count('1')  # replace with dict
        # Set up the event dict
        event = {
            "window_labels": [[] for _ in range(num_channels * num_chips)],
            "data": [[] for _ in range(num_channels * num_chips)],
            "start_window": data[num_evt_headers],
        }

        out_timing_data = []
        step_size = channel_step_size * num_channels + self.num_window_headers

        window_size = num_channels * channel_step_size + num_footer_words
        # num_windows = (len(data) - num_evt_headers) // window_size

        # Only add timing information for the first chip (all chips is too many windows)
        event["window_timings"] = data[window_size - 1]

        step_size = (samples + num_window_headers) * num_channels + channel_footers
        header_steps = range(0, len(data) - step_size, step_size + num_evt_headers + 1)
        self._parse_event_headers(event, data)
        self._parse_event_headers(event, data, step_size + num_evt_headers + 1)

        for idx in header_steps:
            window_steps = range(
                idx + num_evt_headers, idx + step_size - 1, samples + num_window_headers
            )
            chipnum = data[idx]

            for inner_idx in window_steps:
                # First two words are window and channel
                window = data[inner_idx]
                channel = data[inner_idx + 1] + (chipnum * channels_per_chip)
                event["window_labels"][channel].append(window)
                # Next 64 words are data.
                event["data"][channel].extend(
                    data[inner_idx + 2 : inner_idx + channel_step_size]
                )
            # Last word is the window timing
            out_timing_data.append(data[idx + step_size - 1])

        return event

    def _validate_input_package(self, in_data):
        """Validate the input data.

        Raises:
            BadDataException if:
            - there is no data.
            - there is not a en event amount of bytes, since 8-bits are combined to 16-bit words.
            - the data is not divisable by sample_num + window_headers.
        """
        # Correct format
        if not isinstance(in_data, dict):
            raise TypeError("raw_data is not a dict it's a %s", type(in_data))

        # No data
        if in_data.get("rawdata", None) == b"":
            raise BadDataError("No Data Found")

        # Edge case, data doesn't contain valid words.
        if len(in_data["rawdata"]) % 2 != 0:
            raise BadDataError(
                f"Bad package no {in_data.get('pkg_num', 'unknown')}, "
                f"length is not an even amount of words, "
                f"len {len(in_data.get('rawdata', {}))}"
            )

    def _add_xaxis_to_event(self, event):
        """Adds an x-axis to the data.

        Based on the amount of channels and samples it will add a timeaxis
        per channel to the event dict.

        Returns:
            numpy array with sample numbers for each channel.
        """
        times = list()
        samples = self.samples
        channels = len(event["data"])
        start_window = event["start_window"]
        for chan in range(0, channels):
            # LOGGER.debug("winds=%s", event["window_labels"][chan])

            winds = np.array(event["window_labels"][chan], dtype=int)
            winds += self.windows * (winds < start_window)
            winds -= start_window

            tim = (samples * np.repeat(winds, samples)) + (
                np.ones((len(winds), samples), dtype=int)
                * np.arange(0, samples, dtype=int)
            ).flatten()

            times.append(tim)

        return times
