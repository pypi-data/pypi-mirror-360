"""Answer parsers

Contains a factory function for retrieving an answer parser
based on the board firmware version.

This module was previously located under the naludaq.daq.workers
subpackage, and was relocated to improve the organization of the
naludaq package.
"""


def get_answer_parser(new_firmware=False):
    response = _parse_answers_old
    if new_firmware is True:
        response = _parse_answers

    return response


def _parse_answers(buffer: bytearray) -> dict:
    """Parses a raw binary answer into python data formats.

    Args:
        buffer (bytes): Response to parse.

    Returns:
        parsed answer as a dict expected format.
    """
    header = int.from_bytes(buffer[0:2], byteorder="big", signed=False)
    response = {
        "header": header,
        "read_reg": header & 255,  # only 8 lsb]
        "value": int.from_bytes(buffer[2:4], byteorder="big", signed=False),
        "cmd_id": int.from_bytes(buffer[4:6], byteorder="big", signed=False),
    }

    # end = buff_data[6:8]
    return response


def _parse_answers_old(buffer: bytearray) -> dict:
    """Parses a raw binary answer into python data formats.

    Args:
        buffer (bytes): Response to parse.

    Returns:
        parsed answer as a dict expected format.
    """
    header = int.from_bytes(buffer[0:2], byteorder="big", signed=False)
    response = {
        "header": header,
        "read_reg": header & 255,  # only 8 lsb]
        "value": int.from_bytes(buffer[2:4], byteorder="big", signed=False),
    }

    return response
