"""Base class for all controllers

"""
from abc import ABC


class Controller(ABC):
    def __init__(self, board):
        self._board = None
        self.board = board

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board):
        self._board = board
