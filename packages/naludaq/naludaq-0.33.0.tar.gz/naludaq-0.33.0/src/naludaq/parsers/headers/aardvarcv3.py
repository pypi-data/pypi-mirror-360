from naludaq.parsers.headers.base import HeaderParser


class AARDVARCv3HeaderParser(HeaderParser):
    @staticmethod
    def parse_header(event: dict, raw_data: bytes):
        # nibbles: ETT TTT TWW
        # byte one: ETT
        # byte two: TTT
        # byte three: TWW
        # E is an E
        # T is a trigger time nibbles
        # W is previous final window
        trigger_time_ns = raw_data[2] >> 8  # 2 # 24 bit number
        trigger_time_ns += raw_data[1] << 12  # 1
        trigger_time_ns += (raw_data[0] & 0x0FF) << 24
        event["trigger_time_ns"] = trigger_time_ns
        event["prev_final_window"] = raw_data[2] & 0xFF
