from naludaq.communication import AnalogRegisters, ControlRegisters

from .default import TriggerController

BOARD_SYSCLK = 78.125e6


class TriggerControllerTrbhm(TriggerController):
    """Trigger controller for TRBHM boards."""

    def __init__(self, board):
        super().__init__(board)

        self._num_chips = board.params.get("num_chips", 2)
        self._num_trig_chans_per_chip = board.params.get("num_trig_chans_per_chip", 4)

    @property
    def trigger_rate(self) -> float:
        """Get/Set the trigger rate in Hz.

        The rate is read as the top 16 bits of a 24-bit counter.
        Because of this, the rate is limited to between 5 and 300_000 Hz.
        The boards clock is running at 78.125 MHz, so the rate is calculated as:
        rate = (78.125 MHz / counter_value in Hz) >> 8.

        4.7 Hz is the minimum rate.
        305175.8 Hz is the maximum rate.

        Args:
            rate (int): The trigger rate in Hz, must be between 5 and 300_000 Hz.

        Returns:
            int: The trigger rate in Hz.
        """
        rate_reg = ControlRegisters(self.board).read("trigger_rate_limit")
        try:
            rate_reg = rate_reg["value"]
        except KeyError:
            return 0
        rate_val = rate_reg << 8
        if rate_val == 0:
            return 0
        rate = BOARD_SYSCLK / rate_val
        return rate

    @trigger_rate.setter
    def trigger_rate(self, rate: int):
        if not isinstance(rate, int):
            raise TypeError("Rate must be an integer.")
        if rate < 5 or rate > 300_000:
            raise ValueError("Rate must be between 5 and 300_000 Hz.")

        rate_reg = int(BOARD_SYSCLK / rate) >> 8

        self._write_control_register("trigger_rate_limit", rate_reg)

    def write_triggers(self):
        """Write the trigger values to the hardware.

        This writes the current set triggers to the hardware.
        By setting the trigger_offsets or the trigger_values
        this function is called automatically and the hardware is updated.
        """
        self._set_trigger_thresholds()
        self._set_wbiases()

        return True

    def _set_trigger_thresholds(self):
        """Sets the trigger values to those in the board object and writes to hardware."""
        trigger_values = self.values
        self._write_analog_registers_per_chip("trigger_threshold_{:02}", trigger_values)

    def _set_wbiases(self):
        """Set the wbias registers based on the board trigger values"""
        wbias = {ch: self.wbias[ch] if x > 0 else 0 for ch, x in self.values.items()}
        self._write_analog_registers_per_chip("wbias_{:02}", wbias)

    def _write_analog_registers_per_chip(
        self, reg_name_format: str, values: "list | dict"
    ):
        """Write analog registers with a given register name format using the
        values provided. Writes values to both chips individually.

        Args:
            reg_name_format (str): register name format string, must take one integer argument.
            values (list): list of values to write. Should be all 8 values across both chips.
        """
        for chip in range(self.board.available_chips):
            for idx in range(self._num_trig_chans_per_chip):
                name = reg_name_format.format(idx)
                val = values[idx + chip * self._num_trig_chans_per_chip]
                AnalogRegisters(self.board, [chip]).write(name, val)
