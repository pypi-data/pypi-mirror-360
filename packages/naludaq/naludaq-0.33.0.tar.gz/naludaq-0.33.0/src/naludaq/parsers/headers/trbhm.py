import numpy as np

from naludaq.parsers.headers.base import HeaderParser


class TrbhmHeaderParser(HeaderParser):
    @staticmethod
    def parse_header(event: dict, raw_data: np.ndarray, offset=0):
        """Parse event headers from raw data and store them into an event dict.

        Args:
            event (dict): the event
            raw_data (ndarray): the raw data as words
            offset (int): offset in words of the header
        """
        chip_num = raw_data[offset] & 1

        _store_header_value(event, "channels", chip_num, raw_data[offset + 1])
        _store_header_value(event, "num_winds", chip_num, raw_data[offset + 2])
        _store_header_value(event, "event_id", chip_num, raw_data[offset + 3])
        _store_header_value(event, "prev_final_window", chip_num, raw_data[offset + 4])
        _store_header_value(
            event,
            "trigger_time_ns",
            chip_num,
            (raw_data[offset + 5] << 12) | raw_data[offset + 6],
        )


def _store_header_value(event: dict, key: str, chip_num: int, value: int, num_chips=2):
    headers_dict = event.setdefault("headers", {})
    headers_dict.setdefault(key, [-1] * num_chips)[chip_num] = value
