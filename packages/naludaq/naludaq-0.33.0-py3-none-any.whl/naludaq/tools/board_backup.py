import copy

from naludaq.communication import AnalogRegisters, ControlRegisters, DigitalRegisters
from naludaq.controllers import get_readout_controller


class BoardBackup:
    """A back up of the board registers at a point in time.
    Can be used to restore the board to an earlier state.
    """

    def __init__(self, board) -> None:
        self._board = board
        self._backup = None

    def backup(self):
        """Back up the registers for the board."""
        rc = get_readout_controller(self._board)
        self._backup = {
            "readout_channels": rc.get_readout_channels(),
            "registers": copy.deepcopy(self._board.registers),
        }

    def restore(self, exclude_registers: list[str] = []):
        """Restores the backup by writing all registers to the board.

        Args:
            exclude_registers (list[str]): list of register names to exclude
                from restoration (e.g. "analog_registers").

        Raises:
            ValueError: if there was no backup previously created.
        """
        if self._backup is None:
            raise ValueError("No backup was previously generated")
        rc = get_readout_controller(self._board)
        rc.set_readout_channels(self._backup["readout_channels"])

        reg_types = {
            "analog_registers": AnalogRegisters,
            "control_registers": ControlRegisters,
            "digital_registers": DigitalRegisters,
        }
        for name, type_ in reg_types.items():
            if name in exclude_registers:
                continue
            self._board.registers[name] = self._backup["registers"][name]
            type_(self._board).write_all()
