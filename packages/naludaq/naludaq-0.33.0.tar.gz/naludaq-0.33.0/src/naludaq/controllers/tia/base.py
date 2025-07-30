import abc

from naludaq.controllers.controller import Controller


class BaseTIAController(Controller):
    def __init__(self, board):
        """ABC for TIA controllers.

        Args:
            board (Board): the board object.
        """
        super().__init__(board)

    @abc.abstractmethod
    def set_dac_values(self, values: list[int]):
        """Set multiple dac values.

        Args:
            values (list): index in list corresponds to the channel number.
        """
