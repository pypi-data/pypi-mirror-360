from abc import ABC, abstractmethod


class SPIDevice(ABC):
    def __init__(self, daisy_chained: bool = True):
        self.daisy_chain_en = daisy_chained
        # self._chain_address

    @property
    def daisy_chain_en(self):
        return self._daisy_chained

    @daisy_chain_en.setter
    def daisy_chain_en(self, enabled: bool):
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool.")

        self._daisy_chained = enabled

    @abstractmethod
    def init_cmd(self):
        """Generate the initialization command for the device."""
        pass

    @abstractmethod
    def init(self):
        """Initialize the device."""
        pass

    @abstractmethod
    def _write(self, message):
        """Write a message to the device."""
        pass

    @abstractmethod
    def no_op(self):
        """Send a no-op command to the device."""
        pass
