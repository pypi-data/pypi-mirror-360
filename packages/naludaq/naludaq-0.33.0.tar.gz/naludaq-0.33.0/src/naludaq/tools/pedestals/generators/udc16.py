import logging

import numpy as np

from naludaq.helpers import FancyIterator
from naludaq.helpers.exceptions import (
    IterationError,
    OperationCanceledError,
    PedestalsDataCaptureError,
)

from .default import PedestalsGenerator

LOGGER = logging.getLogger("naludaq.pedestals_generator_udc16")


class PedestalsGeneratorUdc16(PedestalsGenerator):
    """Pedestals generator for UDC16."""

    def _capture_data_for_pedestals(self) -> list[list[dict]]:
        """Capture raw data for pedestals.

        For UDC16/UPAC96 it's a bit different. We need to throw away the first window and there's no forced mode,
        so it's random where the window hole shows up in the data. This capture function makes sure that
        regardless of where the hole shows up in each event, we have enough captures for all windows.

        Returns:
            list[list[dict]]: list of data for blocks. Warmup events
                are removed from the output.

        Raises:
            PedestalsDataCaptureError: if pedestals failed to generate.
            OperationCanceledError: if pedestals generation was cancelled.
        """
        LOGGER.debug(
            "Capturing pedestals for %s. channels=%s",
            self.board.model,
            self.channels,
        )
        get_actual_count = lambda events: np.min(
            self._get_window_counts(events)[self.channels]
        )
        pipeline = (
            self._create_data_pipeline()
            .accumulated()
            .take_while(lambda all: get_actual_count(all) <= self._num_captures)
            .unaccumulated()
        )
        try:
            return [pipeline.collect()]
        except OperationCanceledError:
            raise
        except (TimeoutError, IterationError) as e:
            LOGGER.error("Failed to generate pedestals data! %s", exc_info=e)
            msg = self._exc_str(e)
            raise PedestalsDataCaptureError(msg) from e

    def _create_validation_stage(self, pipeline: FancyIterator) -> FancyIterator:
        return pipeline.filter(self._validate_event, exclusion_limit=10)

    def _validate_event(self, event: dict) -> bool:
        """Validate an event.

        The expected_window_labels argument is ignored for UDC16,
        since if it's parsed then it's probably valid.
        """
        return "data" in event

    def _backup_settings(self) -> dict:
        return {}

    def _create_progress_update_stage(self, pipeline: FancyIterator) -> FancyIterator:
        n_warmup = self.num_warmup_events
        total_events = n_warmup + self._num_captures
        min_progress = 20
        max_progress = 80

        def inner(events):
            idx = len(events)
            if idx > n_warmup:
                window_counts = self._get_window_counts(events[n_warmup:])
                n_actual_events = np.min(window_counts[self.channels])
                idx = n_warmup + n_actual_events
            idx -= 1
            percent = min_progress + (max_progress - min_progress) * idx / total_events
            msg = f"Capturing event {idx}/{total_events}"
            self._update_progress(percent, msg)

        return pipeline.accumulated().for_each(inner).unaccumulated()

    def _store_raw_data(self, blocks: list[list[dict]]):
        num_captures = self._num_captures
        channels = self.board.params.get("channels", 16)
        windows = self.board.params.get("windows", 64)
        samples = self.board.params.get("samples", 64)
        rawdata = self.board.pedestals["rawdata"]
        window_counts = np.zeros((channels, windows), dtype=int)
        for event in blocks[0]:  # only one block for UDC16/UPAC96
            for chan in range(channels):
                chan_data = event["data"][chan]
                for window_idx, window in enumerate(event["window_labels"][chan]):
                    # first/last windows are junk
                    if window_idx == 0 or window_idx == windows - 1:
                        continue

                    cap = window_counts[chan, window]
                    window_counts[chan, window] += 1
                    if cap >= num_captures:  # only take the first "num_captures" events
                        continue

                    data = chan_data[window_idx * samples : (window_idx + 1) * samples]
                    rawdata[chan, window, :, cap] = data

        return True

    def _get_window_counts(self, events: list[dict]) -> np.ndarray:
        """Calculate the number of times each window occurs in the given events.

        Args:
            events (list[dict]): list of validated events.

        Returns:
            np.ndarray: 2D int array with shape (channels, windows) containin
                window counts.
        """
        channels = self.board.channels
        windows = self.board.params["windows"]
        window_hits = np.zeros((channels, windows), dtype=int)

        # Count the number of times each window shows up in the data.
        for event in events:
            for chan, chan_window_labels in enumerate(event["window_labels"]):
                if len(chan_window_labels) == 0:
                    continue
                # skip first/last windows, they're junk.
                window_hits[chan][chan_window_labels[1:-1]] += 1
        return window_hits

    def _exc_str(self, e: Exception) -> str:
        """Get a string describing pedestals generation errors/possible fixes.

        Two types of exceptions are relevant here:
        - TimeoutError: when no valid data is received for a while.
        - IterationError: when we get valid data but it's filtered out by the
            constraints in `validate_event()` or somewhere else.

        Args:
            e (Exception): exception that was raised.
        """
        return (
            "Failed to generate pedestals calibration. Please try again and power cycle the board "
            "if the problem persists."
        )
