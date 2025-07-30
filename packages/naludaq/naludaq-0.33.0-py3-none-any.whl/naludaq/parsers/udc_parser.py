"""UPACParser

*This parser inverts the 10-bit values as the internal ramp is operating in reverse*
This inversion is around 10-bits which means each value is subtracted from 1023.

Use parser to parse the data from the Hardware.
The boards sends a raw bitstream and it needs to be parsed into events.
The parser class is a tool to parse the raw bitstream of 8-bit chunks
into 16 bit words then extracting the 10-bit data, the header info,
channels and window number data.

This data is then returned in a dictionary.
The raw data is preserved.

"""

import logging

import numpy as np

from naludaq.helpers.exceptions import BadDataError  # IncompatibleParserError,
from naludaq.parsers.parser import Parser

LOGGER = logging.getLogger(__name__)


class UDCParser(Parser):
    """Parser for UDC16 data.

    The dataformat is:
        header: b'10' + "CHIP_ID"(6-bits) (1 byte)
        16 ea: (16 x 8196 bytes = 131_136 bytes)
            - "WINDOW"(8-bit) + "CHANNEL"(8-bit) (2 byte)
            - 4196 samples (each sp 16-bits) (8192 BYTES)
            - CRC(1-byte) + 0xFC (2 bytes)
        footer: 0xCAFE (2 byte)

        131,139 bytes total
    """

    def __init__(self, params: dict):
        """Instantiate the parser using the given parameters.

        Args:
            params (dict): the parameters to use when parsing the data. Make sure
                to only pass in params that match those the data was captured with.
        """
        super().__init__(params)
        self.num_wind_header = params.get("window_headers", 1)
        self.num_wind_footers = params.get("window_footers", 1)
        self._data_mask = params.get("data_mask", 0x03FF)  # 10 bits
        self._chip_mask = params.get("chip_mask", 0x3F)  # 6 bits
        self._channel_mask = params.get("chanmask", 0xFF00)
        self._wind_mask = params.get("windmask", 0x00FF)
        self._channel_shift = params.get("chanshift", 8)
        self.invert_data = True

    @property
    def invert_data(self) -> bool:
        """Enable data inversion.

        If true, inverts each data point to (1023 - data)
        """
        return bool(self._max_data_value)

    @invert_data.setter
    def invert_data(self, val: bool):
        if val:
            # Bitwise XOR of 1's results in subtraction (inversion)
            self._max_data_value = 0x03FF
        else:
            # Bitwise XOR of 0's results in no bit flips
            self._max_data_value = 0x0000

    def parse_digital_data_old(self, in_data) -> dict:
        """Parse UDC data

        Args:
            in_data (dict):

        Returns:
            event dict with parser 'data' field.

        Raises:
            BadDataException if length is more or less than expected or no data in the packet.
        """
        self._validate_input_package(in_data)

        data = in_data.get("rawdata", None)
        if data is None:
            raise BadDataError("No raw_data field in input data")

        channels = self.channels
        samples = self.samples
        windows = self.windows
        chan_mask = self._channel_mask
        chan_shift = self._channel_shift
        wind_mask = self._wind_mask
        data_mask = self._data_mask
        raw_data = np.frombuffer(data[1:], dtype="<H")
        max_data_value = self._max_data_value

        # All lengths below in words
        start = 0
        step = self.num_wind_header + windows * samples + self.num_wind_footers
        end = len(raw_data) - 1

        curr_event = {
            "chip": data[0] & self._chip_mask,
            "window_labels": np.zeros(shape=(channels, windows), dtype=int),
            "data": np.zeros(shape=(channels, windows * samples)),
            "start_window": int(raw_data[0] & wind_mask),  # first word
            "footers": [],
        }

        for chidx in range(start, end, step):
            window = int(raw_data[chidx] & wind_mask)
            chan = int((raw_data[chidx] & chan_mask) >> chan_shift)
            # Remaining window numbers are always in order
            window_labels = [int(x % windows) for x in range(window, window + windows)]

            footer = raw_data[chidx + step]
            # bitwise XOR is used flip the bits without assuming max values and data_mask
            # bitwise XOR is also faster then using subtraction.
            curr_event["data"][chan] = max_data_value ^ (
                raw_data[chidx + 1 : chidx + step - 1] & data_mask
            )
            curr_event["window_labels"][chan] = window_labels
            curr_event["footers"].append(footer)

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
        # The UDC dataformat has a 1 byte header, making the amount uneven
        if len(in_data["rawdata"]) % 2 != 1:
            raise BadDataError(
                f"Bad package no {in_data.get('pkg_num', 'unknown')}, "
                f"length is not an even amount of words, "
                f"len {len(in_data['rawdata'])}"
            )
