from naludaq.parsers.headers.base import HeaderParser


class ASoCv2HeaderParser(HeaderParser):
    @staticmethod
    def parse_header(event: dict, raw_data: bytes):
        """Parse event headers from raw data and store them into an event dict.

        Args:
            event (dict): the event
            raw_data (bytes): the raw data to parse.
        """
        # head0: 1110TTTTTTTT
        # head1: TTTTTTTTTTTT
        # head2: TTTTWWWWWWWW
        trigger_time_ns = (raw_data[0] & 255) << 16  # 1
        trigger_time_ns += raw_data[1] << 4  # 2 # 24 bit number
        trigger_time_ns += raw_data[2] % 255
        event["prev_final_window"] = raw_data[2] & 255  # evt header 0
        event["trigger_time_ns"] = trigger_time_ns
        event["head0"] = raw_data[0]
        event["head1"] = raw_data[1]
        event["head2"] = raw_data[2]
        # event['event_id": raw_data[3] # 3 # not a thing, maybe will add later
