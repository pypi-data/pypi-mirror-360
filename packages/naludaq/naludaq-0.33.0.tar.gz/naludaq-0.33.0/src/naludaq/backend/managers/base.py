from naludaq.backend.context import Context
from naludaq.backend.exceptions import ContextError


class Manager:
    def __init__(self, board) -> None:
        if not hasattr(board, "context"):
            raise ContextError("A context is required")
        self._board = board

    @property
    def board(self):
        return self._board

    @property
    def context(self) -> Context:
        return self._board.context
