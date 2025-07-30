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

import numpy as np

from naludaq.parsers.parser import Parser

LOGGER = logging.getLogger(__name__)


class ASoCv3Parser(Parser):
    def __init__(self, params):
        super().__init__(params)

    def parse_digital_data_old(self, in_data) -> dict:
        """Parse the raw data from the board.
        Assuming that the data packets are constant length, we can extract the data
        in place with matrix operations, speeding up the parsing.

        Parses the data spit out by the digitial readout portion of the firmware

        Channel data is interleaved, e.g
        pkt0,4,8,.... - ch0,
        pkt1,5,9,.... - ch1,
        etc

        TODO: To speed this up more, we do not want two matrices (bitshift & raw),
        we would perferably only want one.

        Args:
            in_data (bytearray): Raw data from the board
        Returns:
            Parsed event as a dict.
        Raises:
            BadDataException if no data is found or if the data contains errors.

        Additional info:
        The word is 16-bit and the data is 12-bit.
        The data is in the form:
        ZZZX XXXX XXXX XXXZ
        Where Z are unused bits.
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
        raw_data = np.array(
            np.frombuffer(in_data["rawdata"], dtype=">H"), dtype="uint16"
        )

        # The raw_data is in the form:
        # ZZZX XXXX XXXX XXXZ
        # Where Z are unused bits.

        # Bitshifted data will make it in the form:
        # 0000 XXXX XXXX XXXX
        bitshifted_data = self._bitshift_data(raw_data)

        curr_event = {
            "window_labels": [[] for _ in range(self.params["channels"])],
            "data": [[] for _ in range(self.params["channels"])],
            "start_window": np.uint16(
                (raw_data[self.params["headers"]] & self.params["windmask"])
                >> self.last_bits
            ),
        }

        self._parse_event_headers(curr_event, bitshifted_data)

        # Reshape the 1D array into a 2D array, packet major uint minor
        num_headers = self.params["headers"]
        data_end = len(bitshifted_data) - self.num_footers

        event_size = len(bitshifted_data) - self.num_footers - num_headers + 1
        packet_size = self.num_wind_header + self.params["samples"]
        num_packet = event_size // packet_size

        event_matrix = np.reshape(
            bitshifted_data[num_headers : data_end + 1],
            [packet_size, num_packet],
            order="F",
        )
        raw_event_matrix = np.reshape(
            raw_data[num_headers : data_end + 1], [packet_size, num_packet], order="F"
        )
        # Pull channel info from all packets
        channels = (raw_event_matrix[0, :] & self.params["chanmask"]) >> self.params[
            "chanshift"
        ]
        available_channels = np.unique(channels[: self.params["channels"]])
        for idx, chan in enumerate(available_channels):
            curr_event["data"][chan] = (
                event_matrix[1:packet_size, idx :: len(available_channels)]
            ).flatten(order="F")
            curr_event["window_labels"][chan] = list(
                (
                    raw_event_matrix[0, idx :: len(available_channels)]
                    & self.params["windmask"]
                )
                >> self.last_bits
            )

        return curr_event
