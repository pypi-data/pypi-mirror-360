from .base import HeaderParser


class UPAC32HeaderParser(HeaderParser):
    @staticmethod
    def parse_header(event: dict, raw_data: bytes):
        """Parse event headers from raw data and store them into an event dict.

        Args:
            event (dict): the event
            raw_data (bytes): the raw data to parse.
        """
        # event['prev_final_window'] = (raw_data[0]&255) # evt header 0
        # trigger_time_ns = raw_data[0] << 12 + raw_data[1] # 1
        # trigger_time_ns += raw_data[1] # 2 # 24 bit number
        event["trigger_time_ns"] = (raw_data[0] << 12) + raw_data[1]
        event["event_id"] = raw_data[2]  # 3
