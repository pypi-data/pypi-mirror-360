from typing import List

from naludaq.communication import ControlRegisters
from naludaq.helpers.exceptions import RegisterFileError

from .base import BaseDACController


class DacControllerUpac32(BaseDACController):
    def __init__(self, board) -> None:
        """DAC controller for the UPAC32.

        Writes to control registers instead of through I2C/SPI
        to set the external DAC.

        Args:
            board (Board): the board object

        Raises:
            RegisterFileError: if the `ext_dac` field of the board
                params is invalid.
        """
        super().__init__(board)

    def _write_dacs(self, channels: List[int]):
        """Writes the DAC values held in board object.

        Args:
            channels (list[int]): a list of which DAC values to write. The list
                should contain elements from the `register_mapping` field in the params.
        """
        self._validate_channels(channels)

        for chan in channels:
            value = self.board.dac_values[chan]
            register = self.dac_params["register_mapping"][chan]
            self._write_control_register(register, value)

        self._write_control_register("dac_write_strobe", True)
        self._write_control_register("dac_write_strobe", False)

    def _validate_ext_dac_params(self, params: dict):
        """Validates the ext_dac board parameters.

        Runs the same checks as the DAC controller base, but also
        makes sure the `register_mapping` field is correct.

        Raises:
            RegisterFileError if the ext_dac params are invalid and cannot be used
        """
        super()._validate_ext_dac_params(params)

        dac_params = params["ext_dac"]
        channels = set(dac_params["channels"].keys())
        register_mapping = dac_params.get("register_mapping", None)

        if register_mapping is None:
            raise RegisterFileError("Ext DAC params are missing the register mapping")
        if not isinstance(register_mapping, dict):
            raise RegisterFileError("Register mapping for ext DAC must be a dict")
        if set(channels) != set(register_mapping.keys()):
            raise RegisterFileError(
                "Register mapping for ext DAC does not match the available DAC channels"
            )
        if any(not isinstance(x, str) for x in register_mapping.values()):
            raise RegisterFileError(
                "Register mapping values for ext DAC must be register names"
            )

    def _validate_channels(self, channels: List[int]):
        """Makes sure the channels to set DACs for are correct.

        Runs the same checks as the DAC controller base, but also
        makes sure that only channels defined in the board params
        are present.
        """
        super()._validate_channels(channels)
        if len(set(channels) - set(self.dac_params["channels"].keys())) != 0:
            raise ValueError(f"Incorrect channels given ({len(channels)})")

    def _write_control_register(self, name: str, value: int):
        """Writes a control register."""
        ControlRegisters(self.board).write(name, value)  # pragma: no cover
