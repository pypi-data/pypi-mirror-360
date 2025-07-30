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

from naludaq.helpers.exceptions import BadDataError
from naludaq.parsers.headers import get_header_parser
from naludaq.parsers.parser import Parser

LOGGER = logging.getLogger(__name__)


class Aardvarcv3Parser(Parser):
    """Parser for the AARDVARCv3 data protocol.

    The AARDVARCv3 adds a windows header compared to the other protocol which
    causes bitlength to be an unreliable way to determine channels/windows in data.
    This parser implements ways to work around this in a consistent manner.

    ```
    Dataformat:
        - 3 x event headers
        - N x window packet
            - 1-4 x channels
                - 1 x channel hader
                - 64 x data packets
            - 1 x window footer
        - 1 x event footer
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
        self.num_evt_headers = self.params.get("num_evt_headers", 3)
        self.num_channel_headers = self.params.get("num_channel_headers", 1)
        self.num_window_headers = self.params.get("num_window_headers", 1)
        self.data_bitmask = self.params.get("data_bitmask", 8191)
        self.chanmask = self.params.get("chanmask", 3072)
        self.windmask = self.params.get("windmask", 1022)
        self.chanshift = self.params.get("chanshift", 10)
        self.num_footer_words = self.params.get("num_footer_words", 2)
        self.last_bits = self.params.get("lastbits", 1)
        self.chan_step_size = self.samples + self.num_channel_headers

        # Generatethe valid bits dictionary
        self.valid_bitlengths = self.create_valid_bitlengths()

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

    def parse_digital_data(self, in_data):
        """Parse the raw data from the board.
        Assuming that the data packets are constant length, we can extract the data
        in place with matrix operations, speeding up the parsing.

        Parses the data spit out by the digitial readout portion of the firmware

        Channel data is interleaved per packet, e.g
        pkt0: [header, ch0, ch1, ch2, ch3, dig. ftr.]
        pkt1: [header, ch0, ch1, ch2, ch3, dig. ftr.]
        etc

        TODO: To speed this up more, we do not want two matrices (bitshift & raw),
        we would perferably only want one.

        Args:
            in_data (bytearray): Raw data from the board
        Returns:
            Parsed event as a dict.
        Raises:
            BadDataError if no data is found or if the data contains errors.

        Args:
            data (np.array or list): all the data, not multi dimensional so one channel at the time.

        """
        try:
            # make sure package contains data and there's an even amount of bytes to combine.
            chans, wind = self._validate_input_package(in_data)
        except:
            raise

        # TODO(Marcus): Need logic for the different channels. Since this needs to be processed from readout data.
        channels = self.channels
        num_headers = self.num_evt_headers
        windmask = self.windmask
        last_bits = self.last_bits
        chan_step_size = self.chan_step_size
        # Converts two bytes into 16-bit words, effectively swapping byteorder and combining in one.
        raw_data = np.frombuffer(in_data["rawdata"], dtype=">H")

        bitshifted_data = self._bitshift_data(raw_data)

        curr_event = {
            "window_labels": [[] for _ in range(channels)],
            "data": [[] for _ in range(channels)],
            "start_window": (raw_data[num_headers] & windmask) >> last_bits,
        }

        self._parse_event_headers(curr_event, bitshifted_data)

        # Packet size
        packet_size = self.chan_step_size * chans + self.num_window_headers

        # Num packets
        num_packet = wind

        data_end = len(bitshifted_data) - self.num_footer_words

        event_matrix = np.reshape(
            bitshifted_data[num_headers : data_end + 1],
            [packet_size, num_packet],
            order="F",
        )
        raw_event_matrix = np.reshape(
            raw_data[num_headers : data_end + 1], [packet_size, num_packet], order="F"
        )

        curr_event["window_timings"] = event_matrix[-1, :]
        for i in range(chans):
            curr_chan = (
                raw_event_matrix[i * chan_step_size, 0] & self.params["chanmask"]
            ) >> self.params["chanshift"]
            curr_event["data"][curr_chan] = (
                event_matrix[1 + i * chan_step_size : (i + 1) * chan_step_size, :]
            ).flatten(order="F")
            curr_event["window_labels"][curr_chan] = (
                raw_event_matrix[i * chan_step_size, :] & self.params["windmask"]
            ) >> self.last_bits

        return curr_event

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
        # PARAMS #################################

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

    def create_valid_bitlengths(self):
        """AARDVARCv3 valid bitlentgth combinations

        There are only certain amount of bytes that are valid for the aardvarcv3 protocol.

        Returns:
            Dictionary of valid combinations, {bytes: [(channels, windows), (channels, windows)]}
        """
        bitlengths = {}
        headers = 4
        for win in range(1, self.windows):  # winn never read out 0 windows
            for chan in range(1, self.channels + 1):
                packlen = (self.chan_step_size * chan + 1) * win + headers
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
        print(potentials)
        return potentials
