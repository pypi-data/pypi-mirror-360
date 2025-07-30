"""Pedestals generator for UPAC32.

UPAC32 works differently because the data cannot be captured in blocks.


NOTE: this does not work anymore, but it's left here for reference if UPAC32 ever rises from the dead
"""
import copy
import logging
from collections import deque

from naludaq.controllers import get_board_controller
from naludaq.tools import EventWaiter
from naludaq.tools.pedestals.pedestals_controller import (
    PedestalsController,
    _update_progress,
    sleep_calc,
)

LOGGER = logging.getLogger("naludaq.upac32_pedestal_generator")


class UpacPedestalsController(PedestalsController):
    """Pedestals controller for UPAC32"""

    def __init__(
        self,
        board,
        num_captures: int = 10,
        num_warmup_events: int = 10,
        channels: "list[int] | None" = None,
    ):
        super().__init__(board, num_captures, num_warmup_events)
        self.failed_validation = deque()

        self.margin = 2
        self.sleeptime = sleep_calc(self.board, self.margin)

    def _capture_data_for_pedestals(self, timeout: int = 3):
        """ """
        num_captures = self.num_captures
        num_warmup_events = self.num_warmup_events
        expected_amount = num_captures + num_warmup_events

        timeout_cnt = 0
        self.block_buffer = deque(maxlen=expected_amount)
        self._daq.output_buffer = self.block_buffer

        while len(self.validated_data) < num_captures and self._cancel is False:
            if timeout_cnt > timeout:
                break
            self.block_buffer = deque(maxlen=expected_amount)
            self._daq.output_buffer = self.block_buffer

            # Check the amount of data needed
            needed_amount = expected_amount - len(self.validated_data)
            # Extra code for status #############################################
            min_value = 0
            max_value = 80
            step_value = (max_value - min_value) / expected_amount
            #####################################################################
            # Capture data
            self._daq.start_capture()
            get_board_controller(self.board).start_readout()
            for idx in range(needed_amount + 1):
                if self._cancel:
                    break
                required_buffer_size = len(self._daq.output_buffer) + 1
                get_board_controller(self.board).toggle_trigger()

                _update_progress(
                    self.progress,
                    min_value + step_value * idx,
                    f"Capturing data, block: {len(self.block_buffer)+1}/{expected_amount}",
                )

                waiter = EventWaiter(
                    self._daq.output_buffer,
                    amount=required_buffer_size,
                    timeout=self.sleeptime,
                )
                try:
                    waiter.start(blocking=True)
                except TimeoutError:
                    LOGGER.warning("Event timed out")
            get_board_controller(self.board).stop_readout()
            self._daq.stop_capture()

            if len(self.block_buffer) != needed_amount:
                LOGGER.warning("data capture failed, increasing sleeptime")
                self._increase_sleeptime(needed_amount)

            # transfer data
            while self.block_buffer and len(self.validated_data) != num_captures:
                try:
                    event = (
                        self.block_buffer.pop()
                    )  # Pop from right skips warmup events
                except Exception:
                    continue
                LOGGER.debug("Transfer event")
                _update_progress(
                    self.progress,
                    min_value + step_value * len(self.validated_data),
                    f"Validate data {len(self.validated_data) + 1}/{expected_amount}",
                )

                # transfer validated data
                if event.get("data", None) is not None:
                    self.validated_data.append(event)

            if len(self.validated_data) == 0:
                LOGGER.debug(
                    "Pedestals buffer is empty, indicating transmission error, retrying."
                )
                timeout_cnt += 1
                continue
            elif self._store_warmup_events:
                self._warmup_data.append(self.block_buffer)

            # if len(self.validated_data) != needed_amount:
            #     LOGGER.debug("data capture failed, restarting")
            #     self._increase_sleeptime(needed_amount)

    def _backup_settings(self) -> dict:
        """Backup settings that might get overwritten to a dict.

        Returns:
            dict with the backup settings
        """
        backup = {
            "control_registers": copy.deepcopy(
                self.board.registers.get("control_registers", {})
            ),
        }

        return backup

    def _restore_backup_settings(self, backup_settings):
        """Restore all backuped settings to the board.

        Returns:
            True if settings have been restored, False if no old settings were found.
        """
        if not backup_settings:
            return

        for register in ["control_registers"]:
            reg = backup_settings.get(register, {})
            if reg:
                self.board.registers[register] = reg

    def _generate_pedestals_data(self, num_captures=None):
        """Generates the pedestals data from captured data.

        Uses captured events in the pedestals_raw_data deque
        to generate the data.

        Args:
            nCaptures (int): Number of captures, default 10
            blocksize (int): size of blocks, default 16
        """

        if num_captures is None:
            num_captures = self.num_captures

        block_size = self.board.params["pedestals_blocks"]

        self._reset_pedestals_data(num_captures)

        LOGGER.debug(
            "Generating pedestals from %s samples with blocksize: %s",
            num_captures,
            block_size,
        )

        return self._validate_and_transfer_data_to_pedestals(block_size, num_captures)

    def _validate_and_transfer_data_to_pedestals(self, block_size, num_captures):
        """Move data to board.pedestals after validating.

        Since data already is prevalidated this is just a logic check,

        Args:
            block_size(int): windows per block
            num_captures(int): amount of events averaged.
        """
        num_blocks = self._calculate_number_blocks(
            block_size, self.board.params["windows"]
        )
        for block in range(num_blocks):
            LOGGER.info("Block %s/%s", block, num_blocks)

            for cap in range(num_captures):
                try:
                    event = self.validated_data.popleft()
                except IndexError:
                    return False

                for chan in range(self.board.params["channels"]):
                    for window_num in range(block_size):
                        real_window = event["window_labels"][chan].index(window_num)
                        window = window_num + block * block_size
                        if block != 0 and (window < block_size):
                            continue
                        if window >= self.board.params["windows"]:
                            continue
                        for sample in range(self.board.params["samples"]):
                            index = sample + real_window * self.board.params["samples"]
                            data = event["data"][chan][index]
                            self.board.pedestals["rawdata"][chan][window][sample][
                                cap
                            ] = data

        return True

    def _store_time_metadata(self):
        """Store event times into pedestals metadata"""
        LOGGER.debug("Storing time metadata")
        self.metadata.store_event_times(self.validated_data)
