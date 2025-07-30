from naludaq.communication import AnalogRegisters, DigitalRegisters
from naludaq.controllers.controller import Controller
from naludaq.helpers.semiton import SemitonABC


class BiasingModeControllerUDC16(Controller, SemitonABC):
    def __init__(self, board):
        """Controls how the internal amplifiers are generally biased.

        Current biasing is mode stable but cant be tweaked (unless reflow).
        Voltage biasing is less stable but can be tweaked

        NOT to be confused with external DAC biasing.
        Will need to retake pedestals when changing biasing mode.

        Args:
            board (Board): Board to change biasing mode
        """
        super().__init__(board)

    def set_voltage_biasing(self):
        """Quick access function to select which channels to operate in voltage biasing mode."""

        self.set_biasing_mode(chan0_7="v", chan8_15="v")

    def set_current_biasing(self):
        """Quick access function to select which channels to operate in current biasing mode."""

        self.set_biasing_mode(chan0_7="c", chan8_15="c")

    def set_biasing_mode(self, chan0_7: "str|None" = None, chan8_15: "str|None" = None):
        """Changes between either voltage or current biasing type

        Voltage biasing is the "traditional" way of biasing the input signal
        via external DAC. Current mode is using a fixed biasing that is supposed to
        be more stable, but is experimental for this design.

        Args:
            bias_mode (str): "current" or "voltage" mode selection
            chan0_7 (str, optional): if true, will change channels 0-7 to biasing mode, defaults to "True".
            chan8_15 (str, optional): if true, will change channels 0-7 to biasing mode, defaults to "True".
        """

        self._validate_inputs_or_raise(chan0_7)
        self._validate_inputs_or_raise(chan8_15)
        self._reset_side_selectors()

        biasing_registers = {
            "comp": (0, 0xFF),
            "ramp7_4": (0, 0xF),
            "ramp3_0": (0, 0xF),
            "transfer": (0, 0xFF),
        }

        # Registers to switch comparator, transfer buffer, and ramp to either current or voltage biasing
        # Logical 1 sets the component to voltage mode, logical 0 sets to current mode
        for bias_mode, side in zip([chan0_7, chan8_15], ["l", "r"]):
            if bias_mode is None:
                continue
            bias_mode = bias_mode.lower()[0]
            paramname = {"l": "0_7", "r": "8_15"}[side]
            if bias_mode != self.board.params[f"intamp_bias_mode_chan{paramname}"]:
                self._write_digital_register(f"writemask_{side}", 0x1FF)

                sel = {"c": 0, "v": 1}[bias_mode]

                for register, value in biasing_registers.items():
                    self._write_analog_register(register, value[sel])

                self._write_digital_register(f"writemask_{side}", 0x0FF)

        self.board.params["intamp_bias_mode_chan0_7"] = chan0_7
        self.board.params["intamp_bias_mode_chan8_15"] = chan8_15
        self._write_digital_register(f"writemask_l", 0x1FF)
        self._write_digital_register(f"writemask_r", 0x1FF)

    def _validate_inputs_or_raise(self, bias_mode):

        if bias_mode is not None:
            if not isinstance(bias_mode, str):
                raise TypeError("bias_mode must be a string")
            if bias_mode.lower()[0] not in ["c", "v"]:
                raise ValueError('Type must be either "current" or "voltage"')

    def _reset_side_selectors(self):
        for side in ["l", "r"]:
            self._write_digital_register(f"writemask_{side}", 0x0FF)

        # RegWrite wrapper for ease of testing

    def _write_analog_register(self, register, value):
        AnalogRegisters(self.board).write(register, value)

    def _write_digital_register(self, register, value):
        DigitalRegisters(self.board).write(register, value)
