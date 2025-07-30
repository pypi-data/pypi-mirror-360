"""Controlls parameters of the communication.

Collection of tools to change the paramters of the communication.
Can be stateless.
"""
import time
from logging import getLogger

from naludaq.backend.managers.connection import ConnectionManager
from naludaq.backend.managers.io import BoardIoManager
from naludaq.backend.models.device import DeviceType
from naludaq.communication import ControlRegisters
from naludaq.controllers.board import BoardController
from naludaq.controllers.controller import Controller

LOGGER = getLogger(__name__)


class ConnectionController(Controller):
    """Controls connection settings.

    Used to alter the connection in any way.
    Change speed, ports, reset connection to a known start.

    TODO: Separate UART only functionality.

    """

    def change_speed(self, sync_int, rate, divider, sync_addr=0x00):
        """
        Attempts to change the baudrate!

        Divider sets it so: (25MHz clock / 16clks/bit)/(divider+1) = baudrate

        NOTE: It is a 100MHz clock now, so the math changes accordingly
            Also it looks like the baud gets quantized on the CPU side at higher rates, so keep that in mind

        Command is DDDDVVVV where V is the divider value (max 256)

        Args:
            sync_int (int): expected integer return when syncing with the board.
            rate (int): valid baudrate
            divider (int): baud divider
        """
        if self.board.using_new_backend:
            return self._change_speed_new(rate, divider)
        if not self.board.connection.is_uart():
            raise ConnectionError
        divider_val = f"{divider:04X}"
        cmd = "DDDD" + divider_val
        self.board.connection.send(cmd)
        time.sleep(
            0.1
        )  # It's essential to let the board update the baudrate, or it'll get stuck.
        self.board.connection.baud = rate

        # Resyncing the connection.
        for _ in range(3):
            if self.board.connection.resync(sync_int, sync_addr):
                LOGGER.debug(
                    "Baudrate synced successfully, divider: %s, baud: %s", divider, rate
                )
                break
        else:
            LOGGER.debug("Sync failed.")

    def set_speed_or_revert_to_default(self, speed=None):
        if self.board.using_new_backend:
            return self._set_speed_or_revert_to_default_new(speed)
        # Since the baud has been reset to default, set the baud to user settings.
        LOGGER.debug("SET SPEED: %s", self.board.connection_info["speed"])
        if not speed:
            speed = self.board.connection_info["speed"]

        if not self._validate_baud(speed):
            LOGGER.warning("Baudrate %s wasn't validated.", speed)
            baudparam = self.board.params["default_baud"]
        else:
            baudparam = [
                (name, divider)
                for name, divider in self.board.params["possible_bauds"].items()
                if int(name) == int(speed)
            ][0]

        LOGGER.debug("Setting baudrate to %s", baudparam)

        sync_int = self._get_sync_int()

        try:
            self.change_speed(sync_int, baudparam[0], baudparam[1])
            if self.board.model in ["upac32", "upaci", "zdigitizer"]:
                ControlRegisters(self.board)._update_software_register(
                    "baud_rate_divisor", baudparam[1]
                )
        except Exception as error_msg:
            raise ConnectionError(error_msg)

    def _validate_baud(self, baud: int):
        """Check if supplied baud is in boardparams.

        Args:
            baud(int): Baudrate

        Returns:
            (list) True if baudrate is valid for the selected board.
        """
        LOGGER.debug(
            "Validating using %s",
            [
                x == int(baud)
                for x, divider in self.board.params["possible_bauds"].items()
            ],
        )
        return any(
            [
                x == int(baud)
                for x, divider in self.board.params["possible_bauds"].items()
            ]
        )

    def reset_connection(self):
        """Matches the board baudrate and resets it to the default.

        This is useful if the application crashes or is in anyway
        not stopping as intended and the baudrate is not reset.
        This way it tries all baudrates available to the board
        if it works it resets the baudrate back to default.

        Returns:
            True if baudrate is reset to default.
        """
        if self.board.using_new_backend:
            return self._reset_connection_new()
        matched = False
        try:
            matched = self._match_baudrate()
        except Exception as error_msg:
            LOGGER.exception("Couldn't match the baudrate! Because: %s", error_msg)

        if matched:
            try:
                self.reset_speed()
            except ConnectionError as error_msg:
                LOGGER.exception("Baudrate not matched due to: %s", error_msg)
                return False
            else:
                return True
        return False

    def _get_sync_int(self):
        return self.board.registers["control_registers"]["identifier"]["value"]

    def _get_sync_addr(self):
        return self.board.registers["control_registers"]["identifier"]["address"]

    def _match_baudrate(self) -> bool:
        """Matches baudrate if the board is set different than program.

        IF the baord i set at a higher baudrate the program can't communicate.
        The only way around it is to guess and then try to lower the baudrate .
        Once the rate is lowered the init script can run and the speed can be increased.

        Returns:
            True if the baudrate is matched else False.
        """
        if self.board.using_new_backend:
            return self._match_baudrate_new()

        board = self.board
        LOGGER.info("Matching baudrate")
        possible_bauds = board.params["possible_bauds"]
        print(f"Trying {[x for x in possible_bauds.keys()]}")
        sync_int = self._get_sync_int()  # TODO: replace the speed selection system
        sync_addr = self._get_sync_addr()

        # early stop
        identifier = self._get_sync_response()
        if identifier == sync_int:
            # if self.board.connection.readReg(0) == sync_int:
            LOGGER.info("Baudrate already matched")
            return True

        LOGGER.debug(
            f"Identifier mismatch, hardware returned: {identifier} - expected: {sync_int}"
        )

        for _ in range(3):
            for baudrate, divider in possible_bauds.items():
                self.change_speed(sync_int, baudrate, divider, sync_addr)
                if board.model not in ["upac32", "upaci", "zdigitizer"]:
                    BoardController(board).reset_board()

                # Clear buffer
                time.sleep(0.05)
                identifier = self._get_sync_response()
                print(f"ident: {identifier} - {sync_int}")
                if identifier == sync_int:
                    # if self.board.connection.readReg(0) == sync_int:
                    LOGGER.info("Rate: %s locked", baudrate)
                    return True
                LOGGER.info("Rate: %s didn't lock, updating settings.", baudrate)
                time.sleep(0.1)
            time.sleep(1)
        return False

    def _get_sync_response(self):
        """Return a pre-defined identifier from the hardware."""
        self.configure_connection()
        identifier = -1
        try:
            identifier = ControlRegisters(self.board).read("identifier")["value"]
        except Exception as error_msg:
            LOGGER.debug("sync response failed due to: %s", error_msg)

        return identifier

    def reset_speed(self):
        """Set the baudrate to the default of the board.

        The default baudrate is stored with the default parameters for the board.
        The conversion between the divider and the baudrate is:
        int((clockrate / 16) / (baudrate) -1)

        Raises:
            ConnectionError if baudrate can't be set.
        """
        if self.board.using_new_backend:
            return self._reset_speed_new()
        board = self.board

        default_baud, divider = [
            (key, val) for key, val in board.params["default_baud"].items()
        ][0]
        sync_int = self._get_sync_int()

        try:
            self.change_speed(sync_int, default_baud, divider)
        except Exception as error_msg:
            raise ConnectionError(
                "Can't change baudrate on the selected connection: %s", error_msg
            )

    def verify_connection(self) -> bool:
        """Verify the connection to the hardware returns a valid response.

        Checks the first register on the board and checks if the response matches the expected.
        If it doesn't respond with the expected value the connection is likely not properly setup
        and/or there is garbage in the buffer.

        Returns:
            True if the response matches the expected response.
            False if any other value is returned.
        """
        return self.is_synced

    def reset_baud_rate(self, attempts: int = 2, num_null_commands: int = 20):
        """Sends a series of zeros ("null" commands) to reset the baud rate
        of the board

        This will only work for boards running firmware which supports this
        method of resetting the baud rate. Make sure a UART connection is open
        before running this method.

        Args:
            attempts (int): The number of times to attempt resetting
                the baud rate
            num_null_commands (int): The number of null/invalid commands to send

        Returns:
            True if the baud rate was successfully reset, or false otherwise
        """
        if self.board.using_new_backend:
            return self._reset_baud_rate_new(attempts, num_null_commands)
        try:
            ser = self.board.connection.ser
        except:
            raise ConnectionError(
                "Cannot reset the baud rate without a UART connection"
            )

        if not self.board.connection.is_open:
            raise ConnectionError(
                "Cannot reset the baud rate without a UART connection"
            )

        # Set the serial baud rate to the default value
        ser.baudrate = int(self.board.params["default_baudrate"])
        sync_int = self._get_sync_int()

        for i in range(attempts):
            LOGGER.debug("Trying to reset baud rate, attempt %d/%d", i + 1, attempts)

            # Send a bunch of zeros to reset the board's baud rate
            self.board.connection.send("00000000" * num_null_commands)
            time.sleep(0.05)

            # Check if the board is responsive
            identifier = self._get_sync_response()
            if identifier == sync_int:
                LOGGER.debug("Successfully reset baud rate")
                return True

        LOGGER.debug("Failed to reset baud rate")
        return False

    # =======================================================================
    # new stuff
    # =======================================================================
    @property
    def expected_sync_response(self) -> int:
        return ControlRegisters(self.board).registers["identifier"]["value"]

    @property
    def is_synced(self) -> bool:
        try:
            return self._get_sync_response() == self.expected_sync_response
        except:
            return False

    def configure_connection(self):
        """Set the appropriate registers so we can communicate with the
        board using the current connection.

        - For ethernet, this means setting tx_mode to ETH and updating the receiver address registers.
        - For non-ethernet, this means setting tx_mode to UART.
        """
        if (
            self.board.using_new_backend
            and ConnectionManager(self.board).device.type == DeviceType.UDP
            or self.board.connection_info.get("type", "") == "udp"
        ):
            self._configure_ethernet()
        else:
            self._configure_non_ethernet()

    def _configure_non_ethernet(self):
        """Configure non-ethernet based (UART/FTDI/USB3) connections."""
        try:
            # enable UART, disable UDP
            self._write_control("tx_mode", 0)
            time.sleep(0.01)
        except:
            LOGGER.debug("Board does not have ethernet capabilities")
        usb_params = self.board.params.get("uart", {})
        bundle_mode = usb_params.get("bundle_mode", False)
        tx_pause = usb_params.get("tx_pause", 0.02)
        self.set_bundle_mode(bundle_mode)
        self.set_tx_pause(tx_pause)

    def set_bundle_mode(self, bundle_mode: bool):
        """Sets the bundle mode on the board."""
        try:
            self.board.connection.bundle_mode = bundle_mode
        except AttributeError:
            LOGGER.warning("Bundle mode not supported on this connection.")
        uart = self.board.params.get("uart", {})
        uart["bundle_mode"] = bundle_mode
        self.board.params["uart"] = uart

    def set_tx_pause(self, tx_pause: float):
        """Sets the transmission pause on the board."""
        try:
            self.board.connection.tx_pause = tx_pause
        except AttributeError:
            LOGGER.warning("TX pause not supported on this connection.")
        uart = self.board.params.get("uart", {})
        uart["tx_pause"] = tx_pause
        self.board.params["uart"] = uart

    def _configure_ethernet(self):
        """Configure an ethernet-based connection"""
        recv_ip, recv_port = self.board.connection_info["receiver_addr"]
        recv_octets = self._get_octets_or_raise(recv_ip)

        # enable UDP, disable UART
        self._write_control("tx_mode", 1)

        # set destination address
        self._write_control(
            "eth_dest_addr31_16", (recv_octets[0] << 8) | recv_octets[1]
        )
        self._write_control("eth_dest_addr15_0", (recv_octets[2] << 8) | recv_octets[3])
        self._write_control("eth_dest_port", recv_port)

        # select user destination address
        self._write_control("eth_addr_sel", 0b01)
        self._write_control("eth_port_sel", 0b01)

    def _change_speed_new(self, rate: int, divider: int):
        """New version of the same function"""
        self._validate_connection_or_raise()

        # It's essential to let the board update the baudrate, or it'll get stuck.
        BoardIoManager(self.board).write(f"DDDD{divider:04X}")
        time.sleep(0.1)
        ConnectionManager(self.board).device.baud_rate = rate

        # Resyncing the connection.
        for _ in range(3):
            if self._resync_new():
                LOGGER.debug(
                    "Baudrate synced successfully, divider: %s, baud: %s", divider, rate
                )
                break
        else:
            LOGGER.debug("Sync failed.")

    def _resync_new(self):
        """New version of the same function"""
        self._validate_connection_or_raise()
        LOGGER.debug("Syncing board...")
        ConnectionManager(self.board).device.clear_buffers()

        for i in range(0, 8):
            if self.is_synced:
                LOGGER.debug("synced, was off %s chars", i)
                return True

            LOGGER.debug("resync(): sending single character")
            BoardIoManager(self.board).write("FF")
            time.sleep(0.1)

        LOGGER.debug("Couldn't sync")
        return False

    def _set_speed_or_revert_to_default_new(self, speed: int = None):
        """New version of the same function"""
        self._validate_connection_or_raise()

        # Since the baud has been reset to default, set the baud to user settings.
        if not speed:
            speed = self.board.connection_info["baud_rate"]
        LOGGER.debug("SET SPEED: %s", speed)

        if not self._validate_baud(speed):
            LOGGER.warning("Baudrate %s wasn't validated.", speed)
            baudparam = self.board.params["default_baud"]
        else:
            divisor = {
                int(b): int(d) for b, d in self.board.params["possible_bauds"].items()
            }[int(speed)]
            baudparam = (int(speed), divisor)

        LOGGER.debug("Setting baudrate to %s", baudparam)

        try:
            self._change_speed_new(baudparam[0], baudparam[1])
        except Exception as error_msg:
            raise ConnectionError(error_msg)

    def _reset_connection_new(self):
        """Matches the board baudrate and resets it to the default.

        This is useful if the application crashes or is in anyway
        not stopping as intended and the baudrate is not reset.
        This way it tries all baudrates available to the board
        if it works it resets the baudrate back to default.

        Returns:
            True if baudrate is reset to default.
        """
        self._validate_connection_or_raise()
        matched = False
        try:
            matched = self._match_baudrate_new()
        except Exception as error_msg:
            LOGGER.exception("Couldn't match the baudrate! Because: %s", error_msg)

        if matched:
            try:
                self._reset_speed_new()
            except ConnectionError as error_msg:
                LOGGER.exception("Baudrate not matched due to: %s", error_msg)
                return False
            else:
                return True
        return False

    def _match_baudrate_new(self) -> bool:
        """Matches baudrate if the board is set different than program.

        IF the baord i set at a higher baudrate the program can't communicate.
        The only way around it is to guess and then try to lower the baudrate .
        Once the rate is lowered the init script can run and the speed can be increased.

        Returns:
            True if the baudrate is matched else False.
        """
        board = self.board
        LOGGER.info("Matching baudrate")
        possible_bauds = board.params["possible_bauds"]
        LOGGER.info(f"Trying {[x for x in possible_bauds.keys()]}")

        # early stop
        sync_response = self._get_sync_response()
        if sync_response == self.expected_sync_response:
            LOGGER.info("Baudrate already matched")
            return True

        LOGGER.debug(
            f"Identifier mismatch, hardware returned: {sync_response} - expected: {self.expected_sync_response}"
        )

        for _ in range(3):
            for baudrate, divider in possible_bauds.items():
                self._change_speed_new(baudrate, divider)
                BoardController(board).reset_board()

                # Clear buffer
                time.sleep(0.05)
                ConnectionManager(board).device.clear_buffers()

                sync_response = self._get_sync_response()
                LOGGER.info(
                    f"Sync response: 0x{sync_response:04X}, need: 0x{self.expected_sync_response:04X}"
                )
                if sync_response == self.expected_sync_response:
                    LOGGER.info("Rate: %s locked", baudrate)
                    return True
                LOGGER.info("Rate: %s didn't lock, updating settings.", baudrate)
                time.sleep(0.1)
            time.sleep(1)
        return False

    def _reset_speed_new(self):
        """New version of the same function"""
        self._validate_connection_or_raise()
        board = self.board

        default_baud, divider = [
            (key, val) for key, val in board.params["default_baud"].items()
        ][0]

        try:
            self._change_speed_new(default_baud, divider)
        except Exception as error_msg:
            raise ConnectionError(
                "Can't change baudrate on the selected connection: %s", error_msg
            )

    def _reset_baud_rate_new(self, attempts: int, num_null_commands: int):
        """New version of the same function"""
        self._validate_connection_or_raise()

        # Set the serial baud rate to the default value
        baud_rate = int(self.board.params["default_baudrate"])
        ConnectionManager(self.board).device.baud_rate = baud_rate

        for i in range(attempts):
            LOGGER.debug("Trying to reset baud rate, attempt %d/%d", i + 1, attempts)

            # Send a bunch of zeros to reset the board's baud rate
            BoardIoManager(self.board).write("00000000" * num_null_commands)
            time.sleep(0.05)

            # Check if the board is responsive
            if self.is_synced:
                LOGGER.debug("Successfully reset baud rate")
                return True

        LOGGER.debug("Failed to reset baud rate")
        return False

    def _validate_connection_or_raise(self):
        if not self.board.is_connected:
            raise ConnectionError("A connection is required")
        if (
            self.board.using_new_backend
            and not ConnectionManager(self.board).is_uart_based
        ):
            raise ConnectionError("Invalid connection type")
        if self.board.connection is not None and not self.board.connection.is_uart():
            raise ConnectionError("Invalid connection type")

    def _write_control(self, name: str, value: int):
        """Write a control register."""
        try:
            ControlRegisters(self.board).write(name, value)
        except ValueError as e:
            LOGGER.error("Failed to update control register due to: %s", e)

    def _get_octets_or_raise(self, ip: str) -> list[int]:
        """Try to parse the octets from an IPv4 address or raise an error.

        Args:
            ip (str): IPv4 address

        Returns:
            list[int]: list of ordered integer octets
        """
        if not isinstance(ip, str):
            raise TypeError("IP must be a string")
        try:
            octets = [int(o) for o in ip.split(".")]
        except:
            raise ValueError("Invalid IP address")
        if len(octets) != 4 or any(not 0 <= o <= 255 for o in octets):
            raise ValueError("Invalid IP address")
        return octets
