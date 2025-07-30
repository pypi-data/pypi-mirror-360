"""ASoCv3S Parser, parser for the ASoC with a serial connection.

Use parser to parse the data from the Hardware.
The boards sends a raw bitstream and it needs to be parsed into events.
The parser class is a tool to parse the raw bitstream of 8-bit chunks
into 16 bit words then extracting the 12-bit data, the header info,
channels and window number data.

This data is then returned in a dictionary.
The raw data is preserved.

"""

import logging

import numpy as np

from naludaq.helpers.exceptions import BadDataError
from naludaq.parsers.headers import get_header_parser
from naludaq.parsers.parser import Parser

LOGGER = logging.getLogger(__name__)


class ASoCv3SParser(Parser):
    def __init__(self, params):
        super().__init__(params)
        self.params = params

        self._parse_event_headers = get_header_parser(self.params["model"])

        self.test_amount_windows = 3
        self.samples = self.params.get("samples", 64)
        self.windows = self.params.get("windows", 254)
        self.channels = self.params.get("channels", 4)
        self.num_evt_headers = self.params.get("headers", 3)
        self.num_channel_headers = self.params.get("channel_headers", 1)
        self.num_window_headers = self.params.get("window_headers", 0)
        self.num_window_footers = self.params.get("window_footers", 0)
        self.data_bitmask = self.params.get("data_bitmask", 8191)
        self.chanmask = self.params.get("chanmask", 1023)
        self.windmask = self.params.get("windmask", 255)
        self.chanshift = self.params.get("chanshift", 8)
        self.num_event_footers = self.params.get("footer_words", 1)
        self.last_bits = self.params.get("lastbits", 0)
        self.chan_step_size = self.samples + self.num_channel_headers

        # Generatethe valid bits dictionary
        self.valid_bitlengths = self.create_valid_bitlengths()

    def create_valid_bitlengths(self):
        """ASoCv3S valid bitlentgth combinations

        There are only certain amount of bytes that are valid for the asocv3 serial protocol.

        Returns:
            Dictionary of valid combinations, {bytes: [(channels, windows), (channels, windows)]}
        """
        windows = self.windows
        channels = self.channels
        chan_step_size = self.chan_step_size
        headers = self.num_evt_headers
        win_footers = self.num_window_footers
        num_footers = self.num_event_footers
        bitlengths = {}
        for win in range(1, windows):  # winn never read out 0 windows
            for chan in range(1, channels + 1):
                packlen = (
                    (chan_step_size * chan + win_footers) * win + headers + num_footers
                )
                cur_value = bitlengths.get(packlen, [])
                cur_value.append((chan, win))
                bitlengths[packlen] = cur_value
        return bitlengths

    def get_conflicts(self):
        """Get all bitlengths with ambiguity.

        Args:
            bitlengths (dict):

        """
        potentials = {key: x for key, x in self.valid_bitlengths.items() if len(x) > 1}
        return potentials

    def _validate_input_package(self, in_data):
        """Validate the input data.

        Returns:
            chan (int): Number of channels in data
            wind (int): Number of windows in data

        Raises:
            BadDataException if:
            - there is no data.
            - there is not a en event amount of bytes, since 8-bits are combined to 16-bit words.
            - the data is not divisable by sample_num + window_headers.
            - the data is not a multiple of a combination of windows and channels
        """
        if not isinstance(in_data, dict):
            raise TypeError("raw_data is not a dict it's a %s", type(in_data))

        if in_data["rawdata"] == b"":
            raise BadDataError("No Data Found")

        # Edge case, data doesn't contain valid words.
        if len(in_data["rawdata"]) % 2 != 0:
            raise BadDataError(
                f"Bad package no {in_data.get('pkg_num', 'unknown')}, "
                f"length is not an even amount of words, "
                f"len {len(in_data['rawdata'])}"
            )
        return self.get_chan_wind_from_bitlength(in_data)

    def get_chan_wind_from_bitlength(self, in_data):
        """Get channels and window amoutns from package length."""
        raw_data = np.frombuffer(in_data["rawdata"], dtype=">H")
        raw_data_length = len(raw_data)

        chanwinds = self.valid_bitlengths.get((raw_data_length), [])
        chan = wind = 0

        if not chanwinds:
            raise BadDataError(
                f"Bad package no {in_data.get('pkg_num', 'unknown')}, "
                f"the amount of bytes is not a valid length."
            )

        if len(chanwinds) == 1:
            chan = chanwinds[0][0]
            wind = chanwinds[0][1]

        elif len(chanwinds) > 1:  # potentials.get(rawlen-4, False):
            for chanwind in sorted(chanwinds, key=lambda x: x[0], reverse=True):
                chan = chanwind[0]
                wind = chanwind[1]

                if self.test_chanwinds(raw_data, chan):
                    break

        return chan, wind

    def test_chanwinds(self, raw_data, chans):
        """Check data integrity using the channels
        All windows should be the same in one block of channels.
        If they are not something is wrong, and the check will stop and return False.

        Args:
            raw_data is the the raw data byteshifted and bytes combined to 16-bit words.
            chans is the amount of channel to test for.
        Returns:
            True if test is passed, False on fail.

        """
        step_size = self.chan_step_size * chans + self.num_window_headers
        num_evt_headers = self.num_evt_headers
        last_bits = self.last_bits
        pass_fail = False

        # runs through a predefined number of windows.
        header_steps = range(
            num_evt_headers, step_size * self.test_amount_windows, step_size
        )
        pass_fail_windows = [
            True
        ]  # Converting to set will fail unless the intial value is True.
        for idx in header_steps:
            # step size depends on channel

            windows = []
            window_steps = range(idx, idx + step_size - 1, self.chan_step_size)
            for inner_idx in window_steps:
                pkt = raw_data[inner_idx]
                window = pkt & self.windmask
                window = window >> last_bits
                windows.append(window)
                # check all windownums are the same
            if len(set(windows)) == 1:
                pass_fail_windows.append(True)
            else:
                pass_fail_windows.append(False)
                break

        if len(set(pass_fail_windows)) == 1:
            pass_fail = True

        return pass_fail

    def parse_digital_data(self, in_data):
        """Parse the raw data from the board into events."""
        try:
            # make sure package contains data and there's an even amount of bytes to combine.
            chans, wind = self._validate_input_package(in_data)
        except:
            raise

        channels = self.channels
        num_headers = self.num_evt_headers
        num_footers = self.num_event_footers
        chanmask = self.chanmask
        windmask = self.windmask
        last_bits = self.last_bits
        samples = self.samples
        num_channel_headers = self.num_channel_headers
        num_window_headers = self.num_window_headers
        num_packet = wind
        chanshift = self.chanshift

        data_bitmask = 8191
        raw_data = np.frombuffer(in_data["rawdata"], dtype=">H")
        len(raw_data)

        bitshifted_data = (raw_data & data_bitmask) >> last_bits

        # Create the empty event
        curr_event = {
            "window_labels": [[] for _ in range(channels)],
            "data": [[] for _ in range(channels)],
            "start_window": (raw_data[num_headers] & windmask) >> last_bits,
        }

        # Compute sizes
        data_end = len(bitshifted_data) - num_footers
        len(bitshifted_data) - num_footers - num_headers
        chan_step_size = samples + num_channel_headers
        packet_size = (
            chan_step_size * chans
        ) + num_window_headers  # num_wind_header + samples

        event_matrix = np.reshape(
            bitshifted_data[num_headers:data_end],
            [packet_size, num_packet],
            order="F",
        )
        raw_event_matrix = np.reshape(
            raw_data[num_headers:data_end], [packet_size, num_packet], order="F"
        )

        curr_event["window_timings"] = event_matrix[-1, :]

        for i in range(chans):
            curr_chan = (
                raw_event_matrix[i * chan_step_size, 0] & chanmask
            ) >> chanshift
            curr_event["data"][curr_chan] = (
                event_matrix[1 + i * chan_step_size : (i + 1) * chan_step_size, :]
            ).flatten(order="F")
            curr_event["window_labels"][curr_chan] = (
                raw_event_matrix[i * chan_step_size, :] & windmask
            ) >> last_bits

        return curr_event
