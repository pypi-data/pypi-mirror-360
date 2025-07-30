import abc


class HeaderParser(abc.ABC):
    """Base class for header parsers.

    All subclasses must implement the static `parse_header` method.
    """

    @staticmethod
    @abc.abstractmethod
    def parse_header(event: dict, raw_data: bytes):
        """Parse event headers from raw data and store them into an event dict.

        Args:
            event (dict): the event
            raw_data (bytes): the raw data to parse.
        """


class NoOpHeaderParser(HeaderParser):
    """No-op header parser, doesn't do anything. Used only as a placeholder
    for data that doesn't have event headers.
    """

    @staticmethod
    def parse_header(event: dict, raw_data: bytes):
        """Placeholder for

        Args:
            event (dict): the event
            raw_data (bytes): the raw data to parse.
        """
