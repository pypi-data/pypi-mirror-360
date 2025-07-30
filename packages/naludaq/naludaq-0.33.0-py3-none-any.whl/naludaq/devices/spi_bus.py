from collections import defaultdict
from abc import ABC, abstractmethod


class SPIBus(ABC):
    def __init__(self, board):
        self.board = board
        self._devices = defaultdict(None)
        self._messages = defaultdict(None)
        self._initialized = False

    @abstractmethod
    def init(self):
        self._initialized = True

    def __getitem__(self, index):
        return self._devices[index]

    def __setitem__(self, index, value):
        self._devices[index] = value
        self._messages[index] = None
        self._initialized = False

    def __len__(self):
        return len(self._devices)

    def __iter__(self):
        for dev in self._devices.values():
            yield dev
