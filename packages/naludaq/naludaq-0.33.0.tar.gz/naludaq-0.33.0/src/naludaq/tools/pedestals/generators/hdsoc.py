import logging

import numpy as np

from naludaq.helpers import FancyIterator

from .default import PedestalsGenerator

LOGGER = logging.getLogger("naludaq.pedestals_generator_hdsoc")


class PedestalsGeneratorHdsoc(PedestalsGenerator):
    """Pedestals generator for HDSoC.

    It's the same as the regular pedestals generator, but with a a special fix
    which accounts for the first window being invalid. When the first window fix
    is enabled, the first window of every event captured is thrown away, since
    the first window is usually (always?) invalid. This will not affect the structure
    of the generated pedestals; all windows are still present in the output.
    """

    def __init__(
        self, board, num_captures: int, num_warmup_events: int, channels: list[int]
    ):
        super().__init__(board, num_captures, num_warmup_events, channels)
        self._first_win_fix = self.board.params.get("first_window_fix", True)

    @property
    def first_window_fix(self) -> bool:
        """Get/set whether the first window fix is enabled.
        The default is True unless otherwise specified in the board parameters.

        See the class documentation for more information on the first window fix.
        """
        return self._first_win_fix

    @first_window_fix.setter
    def first_window_fix(self, enabled: bool):
        if not isinstance(enabled, bool):
            raise TypeError("Type must be boolean")
        self._first_win_fix = enabled

    def _read_window(self, start_window: int) -> tuple[int, int, int]:
        """Override for the first window fix."""
        return (
            self._correct_block_size(self.block_size),
            self._correct_start_window(start_window),
            self.board.params["windows"],
        )

    def _create_validation_stage(self, pipeline: FancyIterator) -> FancyIterator:
        """Override for the first window fix."""
        if self.first_window_fix:
            pipeline = pipeline.map(self._remove_first_window)
        return super()._create_validation_stage(pipeline)

    def _calculate_expected_window_labels(
        self, start_window: int, block_size: int
    ) -> list[int]:
        """Calculate the window labels we expect to see from an event
        read from the given block.

        Reimplmented to account for the first window fix.
        If the first window fix is enabled, the actual start window is one less
        so that we can throw it away later, and the block size is one window more
        so we can still read until the end of the block.

        Args:
            start_window (int): the start window of the block
            block_size (int): the block size

        Returns:
            list[int]: the expected window labels
        """
        return super()._calculate_expected_window_labels(
            start_window,
            self._correct_block_size(block_size),
        )[1:]

    def _remove_first_window(self, event: dict) -> dict:
        """Remove the first window from the event in-place.

        Args:
            event (dict): the event

        Returns:
            dict: the same event object
        """
        samples = self.board.params.get("samples", 32)

        event["window_labels"] = np.delete(event["window_labels"], 0, 1)
        event["data"] = np.delete(event["data"], range(samples), 1)
        event["time"] = np.delete(event["time"], range(samples), 1)
        return event

    def _correct_start_window(self, start_window: int) -> int:
        """Correct the given start window by subtracting one
        when the first window fix is enabled. Does nothing
        if the switch is off.
        """
        if self.first_window_fix:
            start_window -= 1
            if start_window < 0:
                start_window = self.board.params["windows"] - 1
        return start_window

    def _correct_block_size(self, block_size: int) -> int:
        """Correct the block size by adding one when the first
        window fix is enabled. Does nothing when the switch is off.
        """
        if self.first_window_fix:
            block_size = min(block_size + 1, self.board.params["windows"])
        return block_size

    def _validate_event(self, event: dict, expected_window_labels: list[int]) -> bool:
        """Reimplemented to check all channels.

        Windows can be missing from individual channels on HDSoC.
        """
        for channel in self.channels:
            labels = event["window_labels"][channel]
            try:
                is_bad = np.any(labels != expected_window_labels)
            except Exception as error_msg:
                LOGGER.error(f"Event validation failed due to: {error_msg}")
                return False
            if is_bad:
                LOGGER.warning(
                    "Expected windows: %s != returned: %s",
                    expected_window_labels,
                    labels,
                )
                return False
        return True
