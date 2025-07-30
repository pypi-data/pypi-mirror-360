"""Readout settings for the board.

Controls the readout channels and the readout windows.
"""
from collections import defaultdict
from logging import getLogger

from naludaq.communication import DigitalRegisters

from .default import ReadoutController

LOGGER = getLogger("naludaq.readout_controller_hiper")
MAX_READOUT = 65536


class HiperReadoutController(ReadoutController):
    """Special readout controller for the HiPER.

    Overrides the channel-setting logic.
    """

    def __init__(self, board):
        super().__init__(board)

    def set_readout_channels(self, channels_to_read: list):
        """Select channels to readout.

        TRBHM currently doesn't support setting channels individually
        across both ASICs; their 'chansel' is shared.

        Args:
            channels_to_read(list): List of channel numbers to read
                Accepts channels 1..8 for consistent API, but does
                a logical OR between the upper and lower 4 channels.
        """
        self._validate_channels_or_raise(channels_to_read)

        chan_per_chip = self._get_chan_per_chip()
        channel_map = defaultdict(list)

        for ch in channels_to_read:
            chip, chan = divmod(ch, chan_per_chip)
            channel_map[chip].append(chan)

        for chip, chans in channel_map.items():
            excludechanmask = chan_per_chip**2 - 1
            excludechanmask -= sum([1 << x for x in chans])
            DigitalRegisters(self.board, chips=chip).write(
                "excludechannelmask", excludechanmask
            )

    def get_readout_channels(self) -> "list[int]":
        """Get the enabled readout channels as a list[int]."""
        output = []
        chan_per_chip = self._get_chan_per_chip()

        for chip in range(self.board.params["num_chips"]):
            excludemask = self.board.registers["digital_registers"][
                "excludechannelmask"
            ]["value"][chip]
            excludemask = f"{excludemask:016b}"
            output.extend(
                [
                    chip * chan_per_chip + c
                    for c in range(chan_per_chip)
                    if excludemask[c] == "0"
                ]
            )
        return output

    def _get_chan_per_chip(self):
        # Convert channels into a channels per chip
        nchips = self.board.params.get("num_chips", 14)
        nchannels = self.board.params.get("channels", 56)
        return nchannels // nchips
