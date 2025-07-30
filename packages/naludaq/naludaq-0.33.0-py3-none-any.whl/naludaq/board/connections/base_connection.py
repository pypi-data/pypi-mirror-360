from abc import ABC, abstractmethod


class BaseConnection(ABC):
    """Base for all connections."""

    def __init__(self):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def read_all(self):
        pass

    @abstractmethod
    def read_until(self):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def reset_input_buffer(self):
        pass

    @abstractmethod
    def reset_output_buffer(self):
        pass

    @property
    @abstractmethod
    def is_open(self) -> bool:
        pass

    @property
    @abstractmethod
    def in_waiting(self):
        pass

    @property
    def type(self):
        return self.__class__.__name__

    def is_uart(self):
        return hasattr(self, "ser")

    def is_ethernet(self):
        return not self.is_uart()
