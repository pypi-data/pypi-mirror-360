import logging

import numpy as np

from naludaq.controllers import get_readout_controller
from naludaq.helpers.exceptions import OperationCanceledError
from naludaq.tools.pedestals.generators.default import PedestalsGenerator

from .default import PedestalsGenerator

LOGGER = logging.getLogger("naludaq.pedestals_generator_udc16")


class PedestalsGeneratorHiper(PedestalsGenerator):
    def __init__(
        self, board, num_captures: int, num_warmup_events: int, channels: list[int]
    ):
        self._board = board
        chan_per_chip = self._get_chan_per_chip()
        channels = channels or [
            x * chan_per_chip + y
            for x in self.board.params["installed_chips"]
            for y in range(chan_per_chip)
        ]
        super().__init__(board, num_captures, num_warmup_events, channels)
        trigger_limit = self.board.params.get("pedestals", {}).get("trigger_limit", 2.0)
        self._dc.trigger_interval_limit = trigger_limit

    def _get_chan_per_chip(self):
        # Convert channels into a channels per chip
        nchips = self.board.params.get("num_chips", 14)
        nchannels = self.board.params.get("channels", 56)
        return nchannels // nchips

    def _restore_backup_settings(self, backup_settings: dict):
        """Restore all backuped settings to the board.

        Returns:
            True if settings have been restored, False if no old settings were found.
        """
        if not backup_settings:
            return

        channels = backup_settings.get("readout_channels", None)
        if channels is not None:
            get_readout_controller(self.board).set_readout_channels(channels)

    def _validate_event(self, event: dict, expected_window_labels: list[int]) -> bool:
        """Returns true if the window labels matches the expected window labels.

        The validation matches the received window_labels with the expected
        window labels to make sure the block contains only data from that
        block. The firmware buffer sometimes contains more data from a previous block
        this makes sure it doesn't enter the next block buffer.

        Args:
            event (dict): event to validate
            expected_block (list): a list of expected window numbers

        Returns:
            True if validated, False if the events windows doesn't match expected.
        """
        for test_channel in self.channels:
            try:
                is_bad = False
                labels = np.array(event["window_labels"][test_channel])
                if not np.all(labels == expected_window_labels):
                    is_bad = True
                    LOGGER.warning(
                        "Channel %s.Expected: %s != returned: %s",
                        test_channel,
                        expected_window_labels,
                        labels,
                    )
                if len(event["data"][test_channel]) == 0:
                    LOGGER.warning(
                        "Missing data, channel %s, only has %s datapoints",
                        test_channel,
                        len(event["data"][test_channel]),
                    )
            except Exception as error_msg:
                LOGGER.error(f"Event validation failed due to: {error_msg}")
                return False
            if is_bad:
                LOGGER.warning("Event didn't pass validation")
                return False
        return True

    def generate_pedestals(self):
        """Generates pedestals and stores them in the board.pedestals.

        Pedestals stored on the board, they will be used on the next acquisition.

        If canceled, the board is set back to its previous state, and no pedestals
        are generated.
        """
        self._cancel = False
        old_pedestals = self.board.pedestals
        self._debug_raw_events = []

        self._update_progress(0, "Saving board state")
        backup = self._backup_settings()

        self.reset_pedestals()
        self._store_board_metadata()

        try:
            self._generate_pedestals_metadata_pre()
            blocks = self._capture_data_for_pedestals()
            self._generate_pedestals_metadata_post()
        except (OperationCanceledError, KeyboardInterrupt):
            self.board.pedestals = old_pedestals
        except:
            self.board.pedestals = old_pedestals
            raise
        else:  # else runs before finally if no error is raised
            self._update_progress(80, "Processing data")
            self._store_raw_data(blocks)
            self._store_averaged_data()
        finally:
            self._update_progress(90, "Restoring board state")
            self._restore_backup_settings(backup)
