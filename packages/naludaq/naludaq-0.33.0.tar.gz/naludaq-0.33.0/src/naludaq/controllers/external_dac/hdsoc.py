import logging
import time

from naludaq.communication.i2c import sendI2cCommand
from naludaq.helpers.exceptions import DACError

from .dac7578 import DACControllerDAC7578

LOGGER = logging.getLogger("naludaq.ext_dac.dac7578_hdsoc")


class DACControllerHDSoC(DACControllerDAC7578):
    def __init__(self, board) -> None:
        """DAC controller for the HDSoCv1, which uses the DAC7578 DAC.

        Args:
            board (Board): the board object.
        """
        super().__init__(board)
        self._power_command = 0b0100
        self._channels_per_device = 8

    def set_dacs(
        self,
        value: "int | None" = None,
        channels: "list[int] | None" = None,
        set_mv: bool = False,
    ):
        """Sets the external DACs for a set of channels.

        Will raise an error if the DACs are disabled.

        Args:
            value (int): value to set the DACs to.
            channels (List[int]): channels to set.
            set_mv (bool): whether the value given is in mV.

        Raises:
            DACError if the DACs are disabled.
        """
        if any(x == "hi-z" for x in self._board.dac_values.values()):
            raise DACError("Cannot set DACs while they are disabled.")
        super().set_dacs(value, channels, set_mv)

    def set_enabled(self, enabled: bool = True):
        """Sets whether the external DAC is enabled for all channels.

        If the external DAC is powered off, the output is set to high impedance
        and the value in `board.dac_values[X]` is set to 'hi-z'.

        On the other hand, when the external DAC is powered on, the value
        is **set to zero.** If you're using this function, take care to
        write the DAC value you desire afterward.

        Args:
            enabled (bool): `True` to power on the DAC, `False` to turn it off
                and set the output to high impedance.

        Raises:
            DACError if the TIA is enabled for any of the given
                channels.
        """
        if not isinstance(enabled, bool):
            raise TypeError('"enabled" must be a boolean')
        if enabled and self._is_tia_enabled():
            raise DACError(
                "Ext. DAC cannot be used for these channels while the TIA is enabled"
            )

        channels = list(range(self._board.channels))
        self._send_power_commands(channels, enabled)
        for channel in channels:
            self.board.dac_values[channel] = 0 if enabled else "hi-z"

        if enabled:
            # Changing the DAC value to 'hi-z' loses the old value;
            # we can at least set to zero for consistent behavior
            self.set_dacs(0, channels)

    def _send_power_commands(self, channels: list[int], enabled: bool):
        """Sends commands to the DAC to enable/disable output for
        the given channels.

        Args:
            channels (List[int]): list of channels to act on
            enabled (bool): whether to enable or disable the given channels
        """
        pd_bits = {
            True: "00",  # powered on
            False: "11",  # powered off & set output to high-Z
        }[enabled]

        # Generate channel states for each device
        # Avoids writing to devices unnecessarily and preserves the state of channels not given
        device_channel_states: dict[
            int, list[str]
        ] = {}  # {device addr: [ch A state, ch B state, ...]}
        for channel in channels:
            device_addr = self._address_mapping[channel]
            bits = device_channel_states.setdefault(
                device_addr, ["0"] * self._channels_per_device
            )
            device_channel = self._channel_mapping[channel]
            bits[device_channel] = "1"

        # Send one command per device
        rw = 0
        for addr, channel_bits in device_channel_states.items():
            LOGGER.debug(
                "Setting DAC enabled: %s for device %s. Channel mask: %s",
                enabled,
                addr,
                {chr(ord("A") + i): v for i, v in enumerate(channel_bits)},
            )

            command = (
                f"{self._power_command:04b}XXXXX{pd_bits}{''.join(channel_bits)}XXXXX"
            )
            command = command.replace("X", "0")
            words = list(map("".join, zip(*[iter(command)] * 8)))  # split into bytes

            sendI2cCommand(self.board, (addr << 1) | rw, words)
            time.sleep(self._send_delay)

    def _is_tia_enabled(self) -> bool:
        """Checks if the TIA is enabled for either side."""
        left = self._board.registers["analog_registers"]["ntia_left"]
        right = self._board.registers["analog_registers"]["ntia_right"]
        if isinstance(left, list):
            left = left[0]
        if isinstance(right, list):
            right = right[0]
        return not left or not right
