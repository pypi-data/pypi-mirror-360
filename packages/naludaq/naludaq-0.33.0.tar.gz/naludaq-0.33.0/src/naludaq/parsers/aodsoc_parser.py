"""Parser for the Oddsock boards

The oddsocks can either have an ASOC or an AODS chip.
The parsing is exactly the same for types of chips.
"""
from logging import getLogger

import numpy as np

from naludaq.helpers.exceptions import BadDataError
from naludaq.parsers.parser import Parser

LOGGER = getLogger("naludaq.oddsock_parser")


class OddsockParser(Parser):
    """Parser for both flavors of the oddsock board."""

    def __init__(self, params) -> None:
        """Create an oddsock parser using the given board params.

        Args:
            params (dict): the board params. If necessary fields are missing,
                reasonable defaults are used instead.
        """
        super().__init__(params)
        self.channels = self.params.get("channels", 8)
        self.channels_per_chip = self.params.get("channels_per_chip", 4)
        self.num_chips = self.params.get("num_chips", 2)
        self.samples = self.params.get("samples", 64)

        self.chip_footer = self.params.get("chip_stop_word", 0xFFFF)
        self.windmask = self.params.get("windmask", 0x0FF)
        self.chanmask = self.params.get("chanmask", 0x300)
        self.chanshift = self.params.get("chanshift", 8)
        self.data_mask = self.params.get("datamask", 0xFFF)

        self.num_window_headers = self.params.get("num_window_headers", 1)
        self.num_chip_headers = self.params.get("chip_headers", 3)

    def _validate_input_package(self, in_data: dict):
        """Run some sanity checks on the raw event before parsing

        Args:
            in_data (dict): raw event with key 'rawdata' (bytes).

        Raises:
            BadDataError: if the event is invalid and cannot be parsed.
        """
        if not isinstance(in_data, dict):
            raise TypeError("Raw event must be a dict")
        raw_data = in_data.get("rawdata", b"")
        if raw_data == b"":
            raise BadDataError("Event contains no data")
        if len(raw_data) % 2 != 0:
            raise BadDataError(
                f"Bad package no {in_data.get('pkg_num', 'unknown')}, "
                f"length is not an even amount of words, "
                f"len {len(in_data['rawdata'])}"
            )

        # data_size strips out chip headers/footers, but not window headers
        data_size = (
            (len(raw_data) // 2)
            - self.num_chip_headers * self.num_chips
            - (self.num_chips - 1)
        )
        if data_size % (self.samples + self.num_window_headers) != 0:
            f"Bad package no {in_data.get('pkg_num', 'unknown')},"
            f"length {len(raw_data)} is not divisible by window size"

    def parse_digital_data_old(self, in_data) -> dict:
        """Parse the raw data from the board.

        Parses the data spit out by the digital readout portion of the firmware

        Args:
            in_data (bytearray): Raw data from the board

        Returns:
            Parsed event as a dict.

        Raises:
            BadDataException if no data is found or if the data contains errors.

        ### Data format
        For each event:
            For each chip:
                For each window:
                    - Chip header (CCCC_XXXX_XXXX_TTTT)
                    - Upper timing header (XXXX_TTTT_TTTTT_TTTT)
                    - Lower timing header (XXXX_TTTT_TTTTT_TTTT)
                    For each channel:
                        - Window header (XXXX_XXCC_WWWW_WWWW)
                        - 64x data packets (XXXX_DDDD_DDDD_DDDD)
                - Chip footer 0xFFFF
            - 0xCAFE
        """
        try:
            self._validate_input_package(in_data)
        except (TypeError, BadDataError):
            raise

        raw_data = np.frombuffer(in_data["rawdata"], dtype=">H")

        # cache a whole bunch of useful values to avoid lookup inside the loops
        channels = self.channels
        channels_per_chip = self.channels_per_chip
        chip_footer = self.chip_footer
        num_window_headers = self.num_window_headers
        num_chip_headers = self.num_chip_headers
        samples = self.samples
        window_stride = num_window_headers + samples
        windmask = self.windmask
        chanshift = self.chanshift
        chanmask = self.chanmask
        datamask = self.data_mask

        curr_event = {
            "window_labels": [[] for _ in range(channels)],
            "data": [[] for _ in range(channels)],
            "start_window": raw_data[num_chip_headers] & windmask,
            "chip_timing": [],
        }

        chip_footer_locs = np.argwhere(raw_data == chip_footer).flatten()
        chip_data_list = np.split(
            raw_data, chip_footer_locs + 1
        )  # +1 includes footer in previous package
        for chip_data in chip_data_list:
            chip_number = chip_data[0] >> 12
            timing = ((chip_data[1] & datamask) << 12) | (chip_data[2] & datamask)
            curr_event["chip_timing"].append(timing)

            window_data = chip_data[
                num_chip_headers:-1
            ]  # -1 to discard chip/event footer
            window_data = np.reshape(
                window_data, (window_data.shape[0] // window_stride, window_stride)
            )
            window_data = np.bitwise_and(window_data, datamask)

            for channel_data in window_data:
                window_number = channel_data[0] & windmask
                channel_number = (
                    (channel_data[0] & chanmask) >> chanshift
                ) + chip_number * channels_per_chip
                curr_event["window_labels"][channel_number].append(window_number)
                curr_event["data"][channel_number].extend(channel_data[1:])

        return curr_event
