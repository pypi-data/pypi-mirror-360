import abc

from naludaq.board.connections.base_connection import BaseConnection


class BaseSerialConnection(BaseConnection):
    @property
    @abc.abstractmethod
    def rtscts(self) -> bool:
        pass

    @rtscts.setter
    @abc.abstractmethod
    def rtscts(self, value: bool):
        self._set_rtscts(value)
