"""Driver for the LTC2990 I2C voltage/current/temperature monitor.

Datasheet:
    https://www.analog.com/media/en/technical-documentation/data-sheets/ltc2990.pdf

Mitchell Matsumori-Kelly
"""
import logging
import time
from functools import partial

from naludaq.helpers.exceptions import BadDataError, I2CError
from naludaq.helpers.helper_functions import type_name

from .i2c_device import I2CDevice

logger = logging.getLogger("naludaq.ltc2990")


class LTC2990(I2CDevice):
    # bitmasks
    CONTROL_MEASURE_ALL = 0b000_11_000
    CONTROL_VOLTAGE_ALL = 0b000_00_111

    # register map
    REGISTER_STATUS = 0x00
    REGISTER_CONTROL = 0x01
    REGISTER_TRIGGER = 0x02
    REGISTER_V1_MSB = 0x06
    REGISTER_V2_MSB = 0x08
    REGISTER_V3_MSB = 0x0A
    REGISTER_V4_MSB = 0x0C
    REGISTER_VCC_MSB = 0x0E
    VOLTAGE_REGISTER_MAP = {
        1: REGISTER_V1_MSB,
        2: REGISTER_V2_MSB,
        3: REGISTER_V3_MSB,
        4: REGISTER_V4_MSB,
    }

    # values relevant to calculations
    SE_VOLTAGE_FACTOR = 305.18e-6

    def __init__(self, board, addr: int):
        """Driver for the LTC2990 I2C voltage/current/temperature
        monitor.

        On instantiation will reset the operating mode to the default
        MEASURE_ALL and CONTROL_ALL.

        Attributes:
            board (Board): The board object. Must have an open connection.
            addr (int): Address of the device.

        Raises:
            I2CError: if the device could not be initialized.
        """
        super().__init__(board, addr)
        self._log_prefix = f"[LTC2990 at {addr:02X}]"

        try:
            self.set_mode()  # Reset to default mode on initialization.
        except I2CError as e:
            raise I2CError("Could not initialize the device") from e

    def set_mode(self, mode=CONTROL_MEASURE_ALL | CONTROL_VOLTAGE_ALL):
        """Sets the mode of operation for the device.

        Args:
            mode (int): the mode, bits [4:0] of the control register.
                See page 16 of the datasheet.

        Raises:
            I2CError: if the deivce did not acknowledge the command
        """
        logging.debug(f"{self._log_prefix} - setting mode to {mode:08b}")
        self.write_register(LTC2990.REGISTER_CONTROL, bytes([mode]))

    def trigger_conversion(self):
        """Triggers a conversion operation in the device.

        It is necessary to call this method:
            - Before _every_ read of a measurement if in single-shot mode
            - Once initially if in continuous mode.

        Raises:
            I2CError: if the deivce did not acknowledge the command
        """
        logging.debug(f"{self._log_prefix} - triggering conversion")
        self.write_register(LTC2990.REGISTER_TRIGGER, bytes([1]))
        time.sleep(0.01)

    def read_voltage(self, channel: int) -> float:
        """Reads the voltage for a particular channel on the device.

        This function WILL fail if the conversion has not been properly
        triggered.

        Args:
            channel (int): the channel number, must be 1-4.

        Returns:
            The voltage in volts.

        Raises:
            BadDataError if the device has not stored a converted value.
        """
        register = LTC2990.VOLTAGE_REGISTER_MAP.get(channel, None)
        if register is None:
            raise ValueError(f"Channel must be 1-4, not {channel}")
        try:
            voltage_reg = self._read_voltage_register(register)
        except BadDataError:
            raise
        voltage = self._convert_register_to_voltage(voltage_reg)
        logging.debug(
            f"{self._log_prefix} - channel {channel} read back as {voltage} V"
        )
        return voltage

    def read_vcc(self) -> float:
        """Reads the VCC supply voltage of the device.

        This function WILL fail if the conversion has not been properly
        triggered.

        Returns:
            The voltage in volts.

        Raises:
            BadDataError if the device has not stored a converted value.
        """
        try:
            register = LTC2990.REGISTER_VCC_MSB
            voltage_reg = self._read_voltage_register(register)
        except BadDataError:
            raise
        self._fix_device_state()  # weird stuff happens when the register pointer rolls over?

        voltage = self._convert_vcc_register_to_voltage(voltage_reg)
        logging.debug(f"{self._log_prefix} - VCC read back as {voltage} V")
        return voltage

    def _read_voltage_register(self, register) -> int:
        """Reads the voltage register for the given channel.
        Make sure a conversion has been triggered before reading!

        Args:
            channel (int): the channel to read from

        Returns:
            int: The value of the register.

        Raises:
            BadDataError: if the read operation failed.
        """
        try:
            # Reading one 1-byte wide register results in two bytes thrown back...
            msb, lsb = self.read_register(register, width=2)[0:2]
        except:
            raise BadDataError("No valid data returned from LTC2990")
        data_valid = bool(msb >> 7)
        if not data_valid:
            raise BadDataError("No valid data returned from LTC2990")
        return (msb << 8) | lsb

    def _fix_device_state(self):
        """For whatever reason the device gets into an invalid state after reading
        the VCC registers. Right after the VCC registers are read, no write operation
        will be acknowledged by the device.

        This function performs a dummy writes to the status register (ignored because
        it's read-only) which seems to fix the issue.
        """
        time.sleep(0.05)
        for _ in range(2):
            try:
                self.write_register(LTC2990.REGISTER_STATUS, bytes([0]))
            except:
                pass

    @staticmethod
    def _convert_vcc_register_to_voltage(register_value: int):
        """Converts the value held in the VCC voltage register to
        the actual voltage.

        Args:
            register_value (int): the value of the register.

        Returns:
            The value in Volts.

        Raises:
            TypeError if the value is not an `int`.
            ValueError if the value is out of bounds for a two-byte unsigned int.
        """
        try:
            return 2.5 + LTC2990._convert_register_to_voltage(register_value)
        except (ValueError, TypeError):
            raise

    @staticmethod
    def _convert_register_to_voltage(register_value: int):
        """Converts the value held in a pair of voltage registers to
        the actual voltage.

        Args:
            register_value (int): the value of the register
                including the MSB and LSB.

        Returns:
            The value in Volts.

        Raises:
            TypeError if the value is not an `int`.
            ValueError if the value is out of bounds for a two-byte unsigned int.
        """
        if not isinstance(register_value, int):
            raise TypeError(
                f"Register value must be an int, not {type_name(register_value)}"
            )
        if not 0 <= register_value <= 0xFFFF:  # voltage registers are 2 bytes
            raise ValueError(
                f"Register value {register_value:X} is out of bounds (0-0xFFFF)"
            )

        data_mask = 0x3FFF
        data_bits = register_value & data_mask
        sign_bit = (register_value >> 14) & 1

        factor = LTC2990.SE_VOLTAGE_FACTOR
        if sign_bit == 1:
            data_bits = -(
                (data_mask ^ data_bits) + 1
            )  # register is stored in two's complement
        voltage = data_bits * factor
        return voltage


def read_ltc2990_voltage(board, addr: int, chan: int, samples: int = 1) -> float:
    """Read a voltage from an LTC2990 chip.

    Args:
        board (_type_): board the LTC2990 is on
        addr (int): 7-bit address of the device
        samples (int): number of readings to average. Default is 1.

    Returns:
        float: the averaged voltage.
    """
    _validate_ltc2990_params_or_raise(addr, chan, samples)

    device = LTC2990(board, addr)
    reader = partial(device.read_voltage, chan)
    if isinstance(chan, str) and chan.lower() == "vcc":
        reader = device.read_vcc

    voltages = []
    for _ in range(samples):
        device.trigger_conversion()
        voltages.append(reader())

    return sum(voltages) / samples


def _validate_ltc2990_params_or_raise(addr: int, chan: int, samples: int):
    """Validate params for the reader helper function"""
    if not isinstance(addr, int):
        raise TypeError(f"Address must be int, not {type_name(addr)}")
    if not isinstance(chan, int):
        raise TypeError(f"Channel must be int, not {type_name(addr)}")
    if not isinstance(samples, int):
        raise TypeError(f"Samples must be int, not {type_name(addr)}")
    if not 0 <= addr < 128:
        raise ValueError(f"Address {addr} is out of bounds")
    if not chan in [*range(4), "vcc"]:
        raise ValueError(f'Channel must be 0-4 or "vcc", not {chan}')
    if samples <= 0:
        raise ValueError(f"Samples must be positive, not {samples}")
