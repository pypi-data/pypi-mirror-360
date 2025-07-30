"""
"""
import time
from logging import getLogger

from naludaq.backend.managers.connection import ConnectionManager
from naludaq.backend.managers.io import BoardIoManager
from naludaq.backend.models.device import DeviceType
from naludaq.communication import ControlRegisters
from naludaq.controllers.controller import Controller
from naludaq.helpers.helper_functions import type_name

LOGGER = getLogger("naludaq.board_controller_upac96")
NON_UDP = [DeviceType.SERIAL, DeviceType.D2XX, DeviceType.D3XX]


class UPAC96BoardController(Controller):
    """Board controller for the specific UPAC96 functionality."""

    def __init__(self, board):
        super().__init__(board)

    def start_readout(self, trigger_mode: str):
        """Start a readout.

        Args:
            trigger_mode (str): the trigger mode to set as specified
                in the documentation for ``set_trigger_mode``. If the
                argument is not provided the trigger type is not set.
        """
        self.set_trigger_mode(trigger_mode)
        self.arm_board()
        self.is_reading_out = True

    def stop_readout(self):
        """Not sure if this is the way the board operates anymore, but this should stop the readout."""
        self.set_trigger_mode("software")
        self.set_continuous_mode(False)
        self.is_reading_out = False

    def set_trigger_mode(self, mode: str):
        """Select the trigger mode for the board.

        Possible trigger modes are:
        - 'software' (power-on default)
        - 'self' (UDC self trigger)
        - 'auto' (FPGA auto trigger 1 Hz)
        - 'external' (external trigger)

        Args:
            mode (str): the trigger mode string as specified above, or
                a portion of it (e.g. 'ext' is interpreted as 'external')

        Raises:
            ValueError: if the mode string is ambiguous ('s').
        """
        if not isinstance(mode, str):
            raise TypeError(f"Trigger mode must be str, not {type_name(mode)}")

        available_modes = {
            "software": 0b00,
            "self": 0b01,
            "auto": 0b10,
            "external": 0b11,
        }

        # An 's' string is ambiguous...
        mode = mode.lower()
        mode_values = [
            (long_name, value)
            for long_name, value in available_modes.items()
            if long_name.startswith(mode)
        ]
        if len(mode_values) == 0:
            raise ValueError(f'Invalid trigger mode "{mode}"')
        if len(mode_values) > 1:
            disambiguation = [x[0] for x in mode_values]
            raise ValueError(
                f'Trigger mode "{mode}" is ambiguous. It could mean '
                f'{", ".join(disambiguation[:-1])}, or {disambiguation[-1]}. '
                f"Please provide a longer string."
            )

        name, value = mode_values[0]
        LOGGER.debug("Setting trigger mode to %s (%s)", value, name)
        self._write_control_register("trigger_select", value)

    def arm_board(self):
        """Arm the board for readout."""
        LOGGER.debug("Arming board")
        self._write_control_register("arm", 1)
        self._write_control_register("arm", 0)

    def set_continuous_mode(self, continuous: bool):
        """Turns on/off continuous mode.

        If continuous mode is turned off (default) while in software mode,
        the board needs to be rearmed after every trigger event.
        """
        if continuous not in [True, False]:  # also allows 0 or 1
            raise TypeError(f"Argument must be bool, not {type_name(continuous)}")
        LOGGER.debug("Set continuous mode: %s", continuous)
        self._write_control_register("continuousmode", continuous)

    def toggle_trigger(self, cycles: int = 3):
        """Toggle the trigger signal."""
        if not isinstance(cycles, int):
            raise TypeError(f'"cycles" must be an int, not {type_name(cycles)}')
        if cycles < 1:
            raise ValueError(f'"cycles" must be at least 1, got {cycles}')
        if cycles > 2**16 - 1:
            raise ValueError(
                f'"cycles" must be at most {2**16 - 1} (16-bits), got {cycles}'
            )
        self.arm_board()

        LOGGER.debug("Sending software trigger")
        self._send_command(f"C000{cycles:04X}")

    def toggle_reread(self):
        """Re-read the last event.

        This will disable continuous mode.
        """
        LOGGER.debug("Toggling reread")

        # Reread cannot start in continuous mode
        cr = ControlRegisters(self.board)
        prev_continuous_mode = cr.registers["continuousmode"]["value"]
        self.set_continuous_mode(False)

        # Sleep time allows the state machine to return to "IDLE" state
        # after disabling continuous mode. Makes re-read waaay more stable.
        time.sleep(0.05)
        self._write_control_register("reread_data", True)
        self._write_control_register("reread_data", False)
        time.sleep(0.01)
        self.set_continuous_mode(prev_continuous_mode)

    def read_firmware_version(self):
        """Read the firmware version.

        This is a control register.
        """
        result = 0
        try:
            result = self._read_control_register("version")
        except Exception:
            LOGGER.error("Can't read firmware version")
        return result

    def clear_buffer(self):
        """Clears the UART buffer on both CPU and FPGA side."""
        self._clear_fpga_buffer()
        self._clear_uart_buffer()

    def _clear_uart_buffer(self):
        """Clears the UART buffer on the"""
        if self.board.using_new_backend:
            device = ConnectionManager(self.board).device
            if device.type in NON_UDP:
                device.clear_buffers()
        else:
            self.board.connection.reset_input_buffer()

    def _clear_fpga_buffer(self):
        """Clear the FPGA FIFOs for both UART and USB data"""
        original_usb = self.board.registers["control_registers"]["usb_fifo_disable"][
            "value"
        ]
        original_uart = self.board.registers["control_registers"]["uart_fifo_disable"][
            "value"
        ]
        self._write_control_register("usb_fifo_disable", 1)
        self._write_control_register("uart_fifo_disable", 1)
        time.sleep(0.2)
        self._write_control_register("usb_fifo_disable", original_usb)
        self._write_control_register("uart_fifo_disable", original_uart)
        time.sleep(0.2)

    def enable_usb(self):
        """Enable the USB interface on the board while disabling the UART interface."""

        usb = True
        uart = False
        self.enable_communication_interfaces(usb, uart)

    def enable_uart(self):
        """Enable the UART interface on the board while disabling the USB interface."""
        usb = False
        uart = True
        self.enable_communication_interfaces(usb, uart)

    def enable_communication_interfaces(self, usb: bool, uart: bool):
        """Independently control the USB and UART interfaces.

        Args:
            usb (bool): enable/disable the USB interface
            uart (bool): enable/disable the UART interface

        Raises:
            TypeError: if the arguments are not bools.
        """
        if not isinstance(usb, bool):
            raise TypeError(f"Argument usb must be bool, not {type_name(usb)}")
        if not isinstance(uart, bool):
            raise TypeError(f"Argument uart must be bool, not {type_name(uart)}")

        self._write_control_register("usb_fifo_disable", True)
        self._write_control_register("uart_fifo_disable", True)
        time.sleep(0.2)
        self._write_control_register("usb_fifo_disable", not usb)
        self._write_control_register("uart_fifo_disable", not uart)
        time.sleep(0.2)

    def power_on_rails(self, rail1: bool = True, rail2: bool = True):
        """Power on the chips on the board.

        Args:
            rail1 enables chips 0-2,
            rail2 enables chips 3-5.
        """
        self._write_control_register("pwr_udc1_en", rail1)
        self._write_control_register("pwr_udc2_en", rail2)

    def reset_board(self):
        """Try and reset the board.

        In case the FPGA get stuck this can help reset the state.
        """
        time.sleep(0.02)
        self.digital_reset()
        time.sleep(0.02)
        self.sysrst()

    def digital_reset(self):
        """Toggles the "reset" port on the readout module.

        Forcibly returns the chip to default state.
        """
        self._write_control_register("digrst", True)
        time.sleep(0.02)
        self._write_control_register("digrst", False)

    def sysrst(self):
        """Toggles the sysrst pin, which resets the digital portion of the chip"""
        self._write_control_register("sysrst", True)
        time.sleep(0.02)
        self._write_control_register("sysrst", False)

    def get_available_chips(self) -> list[int]:
        """Get a list of available chip numbers."""
        lock_bits = self._read_control_register("udc_rxout_locked")
        num_chips = self.board.params.get("num_chips", 6)
        chips = [c for c in range(num_chips) if (lock_bits >> c) & 1]
        return chips

    def set_pd_bias_enabled(self, enabled: bool):
        """Set whether photodiode bias is enabled"""
        if enabled not in [0, 1]:
            raise TypeError("Enable flag must be a bool")
        self._write_control_register("pd_bias_en", enabled)

    def pd_bias_enabled(self) -> bool:
        """Get whether photodiode bias is enabled"""
        return bool(self.board.registers["control_registers"]["pd_bias_en"]["value"])

    def set_trigger_monitoring_disabled(self, disabled: bool = True):
        """Disable monitoring of the trigger signal."""
        self._write_control_register("trigger_monitor_disable", disabled)

    def set_trigger_monitor_acquisition(self):
        """Monitor the acquisition signal sent to the UDC chip"""
        self._write_control_register("trigger_monitor_select", 0)

    def set_trigger_monitor_external(self):
        """Monitor the raw external trigger signal on CH 80"""
        self._write_control_register("trigger_monitor_select", 1)

    def _read_control_register(self, register: str) -> int:
        """Reads a control register"""
        return ControlRegisters(self.board).read(register)["value"]

    def _write_control_register(self, register, value):
        """Writes a control register"""
        ControlRegisters(self.board).write(register, value)  # pragma: no cover

    def _send_command(self, command):
        """Send the given hex command to the board.

        Args:
            command (str): hex command
        """
        if self.board.using_new_backend:
            BoardIoManager(self.board).write(command)
        else:
            self.board.connection.send(command)
