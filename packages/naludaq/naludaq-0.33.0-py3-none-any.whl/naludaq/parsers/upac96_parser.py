import numpy as np

from naludaq.helpers.exceptions import BadDataError

from .parser import Parser
from naluacq import ecc_check, ecc_correct


class Upac96Parser(Parser):
    """UPAC96 Parser

    Data Format
    For each chip:
        - Chip header (1 byte, 0x80)
        For each channel
            - 1 window header (2 bytes, 0xCCWW)
            - 4096 samples (2 bytes each: 6-bits ECC + 10 bits data)
            - 1 window footer (2 byte CRC, 0xZZFC)
        - Chip footer (3 bytes, 0x00FACE)
    """

    def __init__(self, params: dict):
        super().__init__(params)

        # physical parameters
        self._chips = params.get("num_chips", 6)
        self._channels = params.get("channels", 96)
        self._channels_per_chip = params.get(
            "channels_per_chip", self.channels // self._chips
        )
        self._windows = params.get("windows", 64)
        self._samples = params.get("samples", 64)

        # masks & shifts
        self._data_mask = params.get("data_mask", 0x03FF)  # 10 bits
        self._window_mask = params.get("windmask", 0x00FF)
        self._channel_mask = params.get("chanmask", 0xFF00)
        self._channel_shift = params.get("chanshift", 8)

        # headers & footers
        self._event_footers = params.get("event_footers", 2)  # bytes
        self._chip_header_bytes = params.get("chip_headers", 1)  # bytes
        self._chip_footer_bytes = params.get("chip_footers", 3)  # bytes
        self._window_headers = params.get("window_headers", 1)  # words
        self._window_footers = params.get("window_footers", 1)  # words

        self.invert_data = True

    @property
    def invert_data(self) -> bool:
        """Enable data inversion.

        If True, inverts each data point to (1023 - data)
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
        """Parse a UPAC96 raw event into the event dict structure.

        Args:
            in_data (dict): dict with 'rawdata' key.

        Returns:
            dict: the event dict.
        """
        self._validate_input_package(in_data)

        # cache useful values to limit lookup
        channels = self._channels
        channels_per_chip = self._channels_per_chip
        windows = self._windows
        samples = self._samples
        total_samples = windows * samples
        chip_header_bytes = self._chip_header_bytes
        chip_footer_bytes = self._chip_footer_bytes
        window_footers = self._window_footers
        window_headers = self._window_headers
        channel_shift = self._channel_shift
        channel_mask = self._channel_mask
        window_mask = self._window_mask
        data_mask = self._data_mask
        event_footers = self._event_footers

        # output goes into these arrays, faster than dict lookup each time
        output_data = np.full((channels, total_samples), np.nan)
        output_window_labels = np.full((channels, windows), np.nan)

        # Figure out how many chips there are in the data
        channel_stride = window_headers + total_samples + window_footers
        chip_stride_bytes = (
            chip_header_bytes
            + 2 * channel_stride * channels_per_chip
            + chip_footer_bytes
        )
        num_chips = (len(in_data["rawdata"]) - event_footers) // chip_stride_bytes

        # 2. Raw data gets reshaped into axes (chip, byte in chip) so we can pull out the start of each chip later
        raw_data = np.frombuffer(in_data["rawdata"], dtype=np.uint8)[:-event_footers]
        # print(raw_data)
        raw_data_matrix = raw_data.reshape((num_chips, chip_stride_bytes))

        # Data starts on odd bytes, need to strip out the beginning of each chip's data
        chip_data_matrix = np.reshape(
            np.frombuffer(
                raw_data_matrix[:, chip_header_bytes:-chip_footer_bytes].flatten(), "<H"
            ),
            (num_chips, channel_stride * channels_per_chip),
        )
        start_window = chip_data_matrix[0, 0] & window_mask

        chip_numbers = raw_data_matrix[:, 0] & 0x3F
        window_range = np.arange(windows)  # reused for window label computation
        for channel in range(channels_per_chip):
            # Grab the window headers for all chips with corresponding channel numbers at once.
            # This way we can do fancy indexing to parse more data with numpy and less with python
            current_window_headers = chip_data_matrix[:, channel * channel_stride]
            current_window_labels = current_window_headers & window_mask
            current_channels = (
                (current_window_headers & channel_mask) >> channel_shift
            ) + chip_numbers * channels_per_chip

            data_start = channel * channel_stride + window_headers
            data_stop = data_start + total_samples
            output_data[current_channels] = (
                chip_data_matrix[:, data_start:data_stop] & data_mask
            ) ^ self._max_data_value

            # Same as UDC16, start window can change but following window numbers are always in order
            window_labels = (current_window_labels[:, None] + window_range) % windows
            output_window_labels[current_channels] = window_labels

        # do some extra conversion to get the data into the right format
        output_data = self._remove_nan_channels(output_data)
        output_window_labels = self._remove_nan_channels(output_window_labels)
        output_window_labels = self._cast_sub_array_dtype(
            output_window_labels, np.uint16
        )
        start_windows = [(list(x) + [0])[0] for x in output_window_labels]

        event = {
            "chips": chip_numbers,
            "data": output_data,  # list[np.ndarray[float]]
            "window_labels": output_window_labels,  # list[np.ndarray[u16]]
            "start_window": start_window,  # int
            "start_windows": start_windows,  # list[int]
        }

        return event

    def parse(
        self, unparsed: dict, *args, check_ecc=False, correct_ecc=False, **kwargs
    ) -> dict:
        """Parse the raw data into a structured event.

        Returns:
            dict: Parsed event data.
        """
        if check_ecc or correct_ecc:
            raw = unparsed.get("rawdata", None)
            if raw is None:
                raise BadDataError("No raw data found in the input package.")

        if correct_ecc:
            raw = ecc_correct(raw)

        event = super().parse(unparsed)
        if check_ecc:
            event["ecc_errors"] = ecc_check(raw)

        return event

    def _add_xaxis_to_event(self, event):
        """Create a time axis for the event. Time axis is computed
        based on the start window on a per-channel basis.

        Returns:
            numpy array with sample numbers for each channel.
        """
        times = []
        samples = self.samples
        for window_labels, start_window in zip(
            event["window_labels"], event["start_windows"]
        ):
            winds = np.array(window_labels, dtype="int32")
            winds += self.windows * (winds < start_window)
            winds -= start_window

            timmy = (samples * np.repeat(winds, samples)) + (
                np.ones((len(winds), samples), dtype=int)
                * np.arange(0, samples, dtype=int)
            ).flatten()
            times.append(timmy)

        return times

    def _validate_input_package(self, in_data):
        """Run preliminary checks on the input package to see if it can be parsed."""
        raw_data = in_data["rawdata"]
        data_len = len(raw_data) - self._event_footers
        instance_data_len = (
            self._chip_header_bytes
            + (
                self.windows * self.samples
                + self._window_headers
                + self._window_footers
            )
            * 2
            * self._channels_per_chip
            + self._chip_footer_bytes
        )

        if data_len & 1 != 0:
            raise BadDataError(f"Data is not an even number of bytes (got {data_len})")
        if data_len % instance_data_len != 0:
            raise BadDataError(
                f"Data length ({data_len} bytes) is not divisible "
                f"by instance data size ({instance_data_len} bytes)"
            )

    def _align_event_windows(
        self, data: list[np.ndarray], window_labels: list[np.ndarray], start_window: int
    ):
        """Align windows in the data/window label array based on the starting window. Modification is in-place."""
        samples = self._samples
        for chan, (chan_data, chan_window_labels) in enumerate(
            zip(data, window_labels)
        ):
            if len(chan_data) == 0 or len(chan_window_labels) == 0:
                continue
            window_roll_amt = chan_window_labels[0] - start_window
            data[chan] = np.roll(chan_data, window_roll_amt * samples)
            window_labels[chan] = np.roll(chan_window_labels, window_roll_amt)

    @staticmethod
    def _remove_nan_channels(arr: np.ndarray) -> list[np.ndarray]:
        """Replace nan-filled channels with an empty array.

        Args:
            arr (np.ndarray): 2D array

        Returns:
            list[np.ndarray]: list of arrays.
        """
        return [np.array([]) if np.any(np.isnan(c)) else c for c in arr]

    @staticmethod
    def _cast_sub_array_dtype(arr: list[np.ndarray], dtype) -> list[np.ndarray]:
        """Cast dtype of arrays within a list"""
        result = []
        for x in arr:
            if not isinstance(x, np.ndarray):
                x = np.array(x)
            result.append(x.astype(dtype))
        return result
