"""
"""
import logging

from naludaq.helpers.exceptions import InvalidTriggerMaskError

from .default import TriggerController

LOGGER = logging.getLogger("naludaq.trigger_controller_upac")


class TriggerControllerUpac(TriggerController):
    """TriggerController for UPAC series of boards.

    Based on the default Controller

    """

    def __init__(self, board):
        super().__init__(board)
        self._num_chips = board.params.get("num_chips", 4)

    @property
    def _num_trig_chans(self):
        return self.board.params.get("num_trigger_channels", 8)

    def set_trigger_mask(self, chips: list):
        """Sets the chip trigger mask.

        Currently only supports UPAC32, UPAC-I, and Z-Digitizer boards.

        Args:
            chips (list): a list of enabled channels

        Raises:
            TypeError if the given list is not actually a list
            InvalidTriggerMaskError if the list supplied is the wrong length
                or contains invalid elements
        """
        self._validate_chip_list_or_raise(chips)

        reg_name = "trigger_mask_enable"
        trigmask = 0xF0  # Only the lower 4 bits are used
        for chip in chips:
            trigmask |= 1 << chip

        LOGGER.debug(f"Setting trigger mask: {reg_name}: {trigmask:04b}")
        self._write_control_register(reg_name, trigmask)

    def _validate_chip_list_or_raise(self, chips):
        """Validates a list of chips, and raises an error
        if there's a problem with them.

        Args:
            chips: the object that is supposedly a chip list

        Raises:
            TypeError if the chip list is not a list
            InvalidTriggerMaskError if the list is too long,
                contains elements that are not an int,
                or contains elements that are too large.
        """
        if not isinstance(chips, list):
            raise TypeError(f"Chips needs to be a list, not a {type(chips)}")
        elif len(chips) > self._num_chips:
            raise InvalidTriggerMaskError(f"Too many chips, max is {self._num_chips}")
        for chip in chips:
            if not isinstance(chip, int):
                raise InvalidTriggerMaskError("Chips can only contain integers")
            elif chip >= self._num_chips or chip < 0:
                raise InvalidTriggerMaskError(f"Chip number {chip} is out of bounds")

    def set_trigger_edge(self, rising: bool = True):
        """Set which signal edge to trigger on.

        Shift between positive going signals (rising) and negative (falling).

        Args:
            rising(bool): If true, trigger on positive going signals, else falling edge.

        Raises:
            TypeError if raises is not a bool.
        """
        if not isinstance(rising, bool):
            raise TypeError("rising must be a bool, got %s", type(rising))

        self._write_control_register("trigger_sign", rising)

    def _set_trigger_thresholds(self):
        """Sets the trigger values and send to hardware.

        Take the trigger values from the board
        """
        trigger_values = self.board.trigger.values

        for chan in range(self._num_trig_chans):
            register = f"psec4a_trigthresh{chan}_out"
            tval = trigger_values[chan]
            self._write_control_register(register, tval)

    def write_triggers(self):
        """Write the trigger values to the hardware.

        This writes the current set triggers to the hardware.
        By setting the trigger_offsets or the trigger_values
        this function is called automatically and the hardware is updated.
        """
        self._set_trigger_thresholds()
