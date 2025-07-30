from naludaq.communication import AnalogRegisters

from .default import TriggerController


class TriggerControllerAodsoc(TriggerController):
    """Trigger controller for AODSOC boards."""

    def __init__(self, board):
        super().__init__(board)

        self._num_chips = board.params.get("num_chips", 2)
        self._num_trig_chans_per_chip = board.params.get("num_trig_chans_per_chip", 4)

    def _set_trigger_thresholds(
        self, trigger_values: "dict[int, int] | int | list[int] | None" = None
    ):
        """Sets the trigger values to those in the board object and writes to hardware."""
        values = trigger_values or self.values
        self._write_analog_registers_per_chip("trigger_threshold_{:02}", values)

    def _set_wbiases(self):
        """Set the wbias registers based on the board trigger values"""
        wbias = {
            ch: self.wbias[ch] if bool(val) else 0 for ch, val in self.values.items()
        }
        self._write_analog_registers_per_chip("wbias_{:02}", wbias)

    def _set_trigger_offsets(self):
        """Set the offset registers to those in the trigger values"""
        vofs = self.offsets
        self._write_analog_registers_per_chip("offset_{:02}", vofs)

    def _write_analog_registers_per_chip(
        self, reg_name_format: str, values: "list | dict"
    ):
        """Write analog registers with a given register name format using the
        values provided. Writes values to both chips individually.

        Args:
            reg_name_format (str): register name format string, must take one integer argument.
            values (list|dict): list or dict of values to write. Should be all 8 values across both chips.
        """
        for chip in range(self.board.available_chips):
            for idx in range(self._num_trig_chans_per_chip):
                name = reg_name_format.format(idx)
                val = values[idx + chip * self._num_trig_chans_per_chip]
                AnalogRegisters(self.board, [chip]).write(name, val)
