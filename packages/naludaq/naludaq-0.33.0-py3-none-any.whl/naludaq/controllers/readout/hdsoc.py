"""Readout settings for the hdsocv1 board.

Controls the readout channels and the readout windows.
"""
from logging import getLogger
from typing import List

from naludaq.communication import AnalogRegisters

from .default import ReadoutController

LOGGER = getLogger("naludaq.readout_controller_hdsoc")


class HDSoCReadoutController(ReadoutController):
    """Readout controller for the hdsocv1 board.

    Controls the readout channels and the windows, lookback, and write after trigger.
    """

    def __init__(self, board):
        """Readout Controller for HDSoCv1.

        Args:
            board (Board): the board object.
        """
        super().__init__(board)

    def set_readout_channels(self, channels_to_read: List[int]):
        """Select channels to readout.

        Will turn on the chips necessary to read out from the given channels
        (e.g. channels [15, 16, 17] -> chips [0, 1]) and will turn off
        chips that are not being used.

        Args:
            channels_to_read (List[int]): List of channel numbers to read
        """
        self._validate_channels_or_raise(channels_to_read, min_valid=0)
        for chan in range(self.board.channels):
            self._set_channel_active(chan, chan in channels_to_read)

    def number_events_to_read(self, amount: int) -> None:
        """Tell the board the maximum number of events to readout.

        This only works if the readout is set with singleEv is set to True.

        Args:
            amount (int): Maximum number of events to read.
        """
        max_winds = self.board.params["max_numwinds"]
        read_windows = self.board.registers["digital_registers"]["readoutwindows"][
            "value"
        ][0]
        channels = len(self.get_readout_channels())
        if not isinstance(amount, int):
            raise TypeError(f"Amount must be an integer, got {type(amount)}")

        numwinds_to_read = amount * read_windows * channels
        if not 0 <= numwinds_to_read <= max_winds:
            raise ValueError(
                f"Calculated number of windows {numwinds_to_read} is larger "
                f"than the maximum of {max_winds}."
            )

        LOGGER.debug(f"Setting numwinds to {numwinds_to_read}")
        self._write_control_register("numwinds", numwinds_to_read)

    def get_readout_channels(self) -> list:
        """Get the current channels specified as enabled in the read out.

        Returns:
            The list of channels read out.
        """
        return [
            chan
            for chan in range(self._board.channels)
            if self._board.registers["analog_registers"][f"ch_{chan}_en"]["value"][0]
        ]

    def _set_channel_active(self, channel: int, active: bool):
        """Wrapper for an analog register write that connects/disconnects
        the channel to everything, essentially turning it on of off

        Args:
            board (Board):
            channel (int): channel to act on
            active (bool): whether the channel should be turned on.

        Raises:
            TypeError if "channel" is not an int, or "active" not a bool.
            ValueError if the channel is out of bounds.
        """
        self._validate_channels_or_raise([channel])
        if not isinstance(active, bool):
            raise TypeError('"active" must be a bool')
        self._write_analog_registers(
            {
                f"bufbias_bias_{channel}": 0x3E8 if active else 0,
                f"ch_{channel}_en": active,
                f"ch_{channel}_isel_en": active,
            }
        )

    def _write_analog_registers(self, registers: dict, chip=None):
        """Write several analog registers.

        Args:
            registers (dict): a dict of `reg_name: reg_value`.
            chip (int): the chip number (0, 1). If not `None`, a suffix
                '_left' or '_right' is appended to each register name.
        """
        ar = AnalogRegisters(self.board)
        chip_suffix = {
            0: "_left",
            1: "_right",
        }
        for register, value in registers.items():
            ar.write(register.format(chip_suffix.get(chip, "")), value)

    def _compute_write_after_trig(self, write_after_trig):
        """On HDSoC write after trigger is equal to windows"""
        return write_after_trig
