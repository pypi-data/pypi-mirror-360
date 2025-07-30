"""Board controller specific for HDSoC series of boards
"""
from logging import getLogger
from typing import List

from naludaq.communication import AnalogRegisters, ControlRegisters
from naludaq.helpers.register_cache import RegisterCache
from naludaq.helpers.semiton import SemitonABC

from .default import BoardController

LOGGER = getLogger("naludaq.board_controller_hdsoc")


class HDSoCBoardController(BoardController, SemitonABC):
    """Board controller for HDSoCv1.

    Only one instance of this class per board object is allowed.
    """

    def __init__(self, board):
        super().__init__(board)
        self._channels_per_chip = board.params.get("channels_per_chip", 16)
        self._num_chips = board.params.get("num_chips", 2)
        self._chip_states = {chip: True for chip in range(self._num_chips)}
        self._waittime = 0.01
        self._init_power_state_caches()

    def _init_power_state_caches(self):
        """Initializes the analog register cache used to remember
        the values of registers after they are ovewritten when
        turning off the chip.
        """
        self._disable_register_states = {
            "channel_bias_bias_{}": 0,
            "scvbias_{}": 0xFFF,
            "scvstab_{}": 0,
            "channel_dac_bias_{}": 0,
            "channel_dac_bias_bias_{}": 0,
            "cmpbias_{}": 0,
            "pubias_{}": 0xFFF,
            "cmpbias2_{}": 0,
            "isel_{}": 0,
            "ref_output_bias_{}": 0,
            "ref_output_bias_bias_{}": 0,
        }

        self._power_state_caches: List[RegisterCache] = []
        for side in range(self._num_chips):
            side_name = {0: "left", 1: "right"}[side]
            cache = RegisterCache(self._board)
            for name in self._disable_register_states:
                name = name.format(side_name)
                cache.add(name, AnalogRegisters)
            self._power_state_caches.append(cache)

    def stop_readout(self):
        """Toggles the "stopacq" signal on the readout module.

        It's equivalent of asking it nicely to stop reading.
        """
        super().stop_readout()
        self.clear_buffer()

    def digital_reset(self):
        """Toggles the "reset" port on the readout module.

        Forcibly returns the chip to default state.
        """
        self._write_control_register("idig_rst", True)
        self._write_control_register("idig_rst", False)

    def clear_buffer(self):
        """Clears the UART buffer on both CPU and FPGA side."""
        self._clear_fpga_buffer()
        super().clear_buffer()

    def _clear_fpga_buffer(self):
        """Resets the FPGA FIFO"""
        ControlRegisters(self.board).write("wave_fifo_rst", True)
        ControlRegisters(self.board).write("wave_fifo_rst", False)

    #############################################################################
    # Random Stuff, may or maynot work... Below functions need to be validated.
    #############################################################################

    def set_enabled_chips(self, chips: List[int]):
        """Sets which chips are enabled.

        Args:
            chips (List[int]): the list of chips. Chip numbers can be
                repeated; it makes no difference in the register writes.
        """
        self._validate_chip_numbers_or_raise(chips)
        for chip in range(self._num_chips):
            self.set_chip_enabled(chip, chip in chips)

    def set_chip_enabled(self, chip_num: int, enabled: bool):
        """Turns on/off a lot of biases on one side of a specific chip.

        Args:
            chip_num (int): the chip number, 0 or 1.
            enabled (bool): whether the channel should be enabled or disabled.

        Raises:
            TypeError if the `chip_num` is not an int, or `enabled` not a bool.
            ValueError if the chip number is out of bounds.
        """
        self._validate_chip_numbers_or_raise([chip_num])
        if not isinstance(enabled, bool):
            raise TypeError('"enabled" must be a bool')

        if enabled:
            self._enable_chip(chip_num)
        else:
            self._disable_chip(chip_num)

    def _enable_chip(self, chip_num: int):
        """Turns on a lot of biases on one side of the chip.

        Args:
            chip_num (int): 0 or 1, which side to turn on biases

        Raises:
            TypeError if the argument is not an int.
            ValueError if the chip number is out of bounds.
        """
        self._validate_chip_numbers_or_raise([chip_num])
        self._power_state_caches[chip_num].restore_all()
        self._chip_states[chip_num] = True

    def _disable_chip(self, chip_num: int):
        """Turns off a lot of biases on one side of the chip to reduce power draw.

        Args:
            chip_num (int): 0 or 1, which side to turn off biases

        Raises:
            TypeError if the argument is not an int.
            ValueError if the chip number is out of bounds.
        """
        self._validate_chip_numbers_or_raise([chip_num])

        # Disabling the chip overwrites old values, need to cache to be able to restore
        if self._chip_states[chip_num]:
            self._power_state_caches[chip_num].update_all()
        self._write_analog_registers(self._disable_register_states, chip=chip_num)
        self._chip_states[chip_num] = False

    def _validate_chip_numbers_or_raise(self, chips: List[int]):
        """Validates a list of chip numbers

        Args:
            chips (List[int]): the list of chips

        Raises:
            TypeError if the argument is not a list of ints.
            ValueError if any chip number is out of bounds.
        """
        if not isinstance(chips, list):
            raise TypeError("Chip numbers must be a list")
        if not all(isinstance(x, int) for x in chips):
            raise TypeError("Chip numbers must all be ints")
        if len(chips) != 0:
            if min(chips) < 0:
                raise ValueError(f"Invalid chip number: {min(chips)}")
            if max(chips) >= self._num_chips:
                raise ValueError(f"Invalid chip number: {max(chips)}")

    def _write_analog_registers(self, registers: dict, chip=None):
        """Write several analog registers.

        Args:
            registers (dict): a dict of `reg_name: reg_value`.
            chip (int): the chip number (0, 1). If not `None`, a suffix
                '_left' or '_right' is appended to each register name.
            preserve (bool): whether to preserve the original value in the
                software registers after writing.
        """
        ar = AnalogRegisters(self.board)
        chip_suffix = {
            0: "left",
            1: "right",
        }
        for register, value in registers.items():
            reg_name = register.format(chip_suffix.get(chip, ""))
            ar.write(reg_name, value)

    def enable_serial_padding(self, enabled: bool):
        """Enable or disable serial padding FW module.

        Serial padder expands the 12-bit data to 16-bit words before transmission.

        Args:
            enabled (bool): whether to enable or disable serial padding.
        """
        self._write_control_register("serial_pad_en", enabled)
