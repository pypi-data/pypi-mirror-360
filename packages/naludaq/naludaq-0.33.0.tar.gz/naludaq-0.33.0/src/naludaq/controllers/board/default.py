"""
"""
import time
from logging import getLogger
from typing import Iterable

from naludaq.backend.managers.connection import ConnectionManager
from naludaq.backend.managers.io import BoardIoManager
from naludaq.backend.models.device import DeviceType
from naludaq.communication import ControlRegisters, DigitalRegisters
from naludaq.controllers.controller import Controller
from naludaq.helpers import type_name

LOGGER = getLogger("naludaq.board_controller_default")
NON_UDP = [DeviceType.SERIAL, DeviceType.D2XX, DeviceType.D3XX]


class BoardController(Controller):
    """The board control communicates with to the board.

    This class is stateless, you need to supply the board to the class to perform actions on it.
    There is no need to store the controller, it will only be used to control the board.

    It is the interface between the application and the board.
    The Analytics package or the GUI uses this class to communicate with the
    hardware. Keeps track of all registers etc.
    It doesn't receive continous data, the data acquisition module should be used for that.
    """

    def __init__(self, board):
        super().__init__(board)

    @property
    def trigger_wait_cycles(self) -> int:
        return self.board.trigger.params.get("ext_trig_cycles", 3)

    @property
    def is_reading_out(self) -> bool:
        """Return True if the board is in readout mode."""
        self.board.is_reading_out

    @is_reading_out.setter
    def is_reading_out(self, value: bool):
        self.board._is_reading_out = value

    def start_readout(
        self,
        trig="self",
        lb="trigrel",
        acq="raw",
        dig_head=False,
        ped="zero",
        readoutEn=True,
        singleEv=False,
    ):
        """Sends a readout signal to the board.

        Obstensibly reads out the chip?

        Args:
            trigger_type (str):
                'immediate', '00' - digitize whatever instantly as fast as possible.
                'ext': '01' - use the external trigger.
                'self': '10' - trigger on input RF signal.
            lbType (str):
                'forced': '00' - always reads out same set of windows, start window set by lookback
                'trig': '01' - relative to the trigger.
                'roi': '10' - complicated...
            acq_type (str):
                'raw': '00' - Can't ped-subtract. <Default output>
                'ped': '01' - sub, spits out headers, channels, and windows. <Requires firmware modification>
            dig_head (bool):
                True: reads out a "digitization" header after each sram read (only works with acq_type="ped")
                False: doesn't read out that header
            pedMode (str):
                'z': '00' - all peds = 0
                'c': '01' - peds = chan*1024, set offset per channel
                'r': '11' - peds = RAM addr
            readoutEn (bool): Enables readout to ethernet (otherwise data thrown away)
                self.readReadoutRate() is the companion to this to see the true rate
                readout rate scalar stored in FPGA reg N_GPR(32) + 5
            singleEV (bool): True - only reads one event.

        Command
        -------

        command is: BMMXXVVV
        MM = singleEvent(7) + readoutEn(6) + pedSel(5 dt 4) + modeSel(3 dt 0)
        - modeSel=x"0" analog write
        - modeSel=x"1" digital write
        - modeSel=x"2" digital read
        - modeSel=x"3" waveform read

        VVVVV = addr_sel(19 dt 12) + data_sel(11 dt 0)
        - data_sel(5 downto 4) = trig type
        - data_sel(3 downto 2) = lb type
        - data_sel(1 downto 0) = acq type

        """
        readout_params = self._validate_readout_params(
            trig, lb, acq, dig_head, ped, readoutEn, singleEv
        )
        cmd = self._generate_start_readout_cmd(readout_params)
        LOGGER.debug("READOUT command: %s", cmd)

        self._send_command(cmd)
        self.is_reading_out = True

    @staticmethod
    def _validate_readout_params(
        trig, lb, acq, dig_head, ped, readoutEn, singleEv
    ) -> dict:
        for name, in_val in {"trig": trig, "lb": lb, "acq": acq, "ped": ped}.items():
            if not isinstance(in_val, str):
                raise TypeError(f"{name} is {type(in_val)}, expected str")
        if trig[0] not in ["i", "e", "s"]:
            raise ValueError(
                f"trig not valid, got {trig}, "
                "options are 'immediate', external', 'self'"
            )
        if lb[0] not in ["f", "t", "r"]:
            raise ValueError(
                f"Invalid lbType, got {lb}, "
                "options are 'forced', 'trigrel', or 'roi'"
            )
        if acq[0] not in ["r", "p"]:
            raise ValueError(
                f"invalid acq_type, got {acq}: " "options are 'raw', or 'pedsub'"
            )
        if ped[0] not in ["z", "c", "r"]:
            raise ValueError(
                f"invalid pedestals_type, got {ped}: "
                "options are 'zero', 'chanoffset', or 'ramaddr'"
            )

        if not isinstance(readoutEn, bool):
            raise TypeError(f"readoutEn is {type(readoutEn)}, expected bool")
        if not isinstance(singleEv, bool):
            raise TypeError(f"singleEv is {type(singleEv)}, expected bool")
        if not isinstance(dig_head, bool):
            raise TypeError(f"dig_head is {type(dig_head)}, expected bool")

        # check they are all there
        # check validity
        readout_params = dict()
        readout_params["trig"] = trig
        readout_params["lb"] = lb
        readout_params["acq"] = acq
        readout_params["ped"] = ped
        readout_params["readoutEn"] = readoutEn
        readout_params["singleEv"] = singleEv
        readout_params["dig_head"] = dig_head

        return readout_params

    def _generate_start_readout_cmd(self, readout_params):
        (
            trigger_type,
            lbType,
            acq_type,
            pedestals_type,
        ) = self._convert_readout_params_to_binary(readout_params)

        readoutEn = readout_params.get("readoutEn", None)
        singleEv = readout_params.get("singleEv", None)
        dig_head = readout_params.get("dig_head", None)

        first_part = hex(
            int(str(int(singleEv)) + str(int(readoutEn)) + pedestals_type + "0011", 2)
        )[2:].zfill(2)

        second_part = hex(
            int("000000" + trigger_type + lbType + str(int(dig_head)) + acq_type, 2)
        )[2:].zfill(3)

        return f"B{first_part}00{second_part}"

    @staticmethod
    def _convert_readout_params_to_binary(readout_params):
        trig = readout_params.get("trig", None)
        lb = readout_params.get("lb", None)
        acq = readout_params.get("acq", None)
        ped = readout_params.get("ped", None)

        trigger_type = lbType = acq_type = pedestals_type = None
        try:
            trigger_type = {"i": "00", "e": "01", "s": "10"}[trig[0].lower()]
        except AttributeError:
            raise ValueError(
                f"trig not valid, got {trig}, "
                "options are 'immediate', external', 'self'"
            )

        try:
            lbType = {"f": "00", "t": "01", "r": "10"}[lb[0].lower()]
        except AttributeError:
            raise ValueError(
                f"Invalid lbType, got {lb}, "
                "options are 'forced', 'trigrel', or 'roi'"
            )

        try:
            acq_type = {"r": "0", "p": "1"}[acq[0].lower()]
        except AttributeError:
            raise ValueError(
                f"invalid acq_type, got {acq}: " "options are 'raw', or 'pedsub'"
            )

        try:
            pedestals_type = {"z": "00", "c": "01", "r": "11"}[ped[0].lower()]
        except AttributeError:
            raise ValueError(
                f"invalid pedestals_type, got {ped}: "
                "options are 'zero', 'chanoffset', or 'ramaddr'"
            )

        return trigger_type, lbType, acq_type, pedestals_type

    def stop_readout(self):
        """Toggles the "stopacq" signal on the readout module.

        It's equivalent of asking it nicely to stop reading.
        """
        self.is_reading_out = False
        cmd = "B0B00000"
        self._send_command(cmd)
        self._write_control_register("stopacq", True)
        self._write_control_register("stopacq", False)

    def toggle_trigger(self, cycles: int = None):
        """Toggles the ext trigger using software.

        Args:
            cycles (int): number of cycles to hold the trigger high for.
                If not provided, a default value is used.
        """
        if cycles is None:
            cycles = self.trigger_wait_cycles
        if not isinstance(cycles, int):
            raise TypeError('"cycles" must be an int')
        if cycles < 1:
            raise ValueError(f'"cycles" must be at least 1, got {cycles}')
        if cycles > 2**16 - 1:
            raise ValueError(
                f'"cycles" must be at most {2**16 - 1} (16-bits), got {cycles}'
            )
        self._send_command(f"C000{cycles:04X}")

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
        self._write_control_register("digrst", False)

    def clear_buffer(self):
        """Clears the UART buffer."""
        if self.board.using_new_backend:
            device = ConnectionManager(self.board).device
            if device.type in NON_UDP:
                device.clear_buffers()
        else:
            self.board.connection.reset_input_buffer()

    def sysrst(self):
        """Toggles the sysrst pin, which resets the digital portion of the chip"""
        self._write_control_register("sysrst", True)
        self._write_control_register("sysrst", False)

    #############################################################################
    # Random Stuff, may or maynot work... Below functions need to be validated.
    #############################################################################

    def read_scalers(self, channels: "Iterable[int] | None" = None) -> list[int]:
        """Reads and returns all the digital scalar registers.

        The scalar registers are in two locations, one is the scal{ch} where the lower bits are
        stored, once that register is read, the scalhigh register is populated with the high bits.

        Args:
            channels (list[int]): list of channels to read scalars for.
                If not provided, scalars for all channels are read.

        Returns:
            list[int]: list of register read results for the channels selected.
                The list will not include values for disabled channels.

        Raises:
            ValueError: if a channel number in the list is invalid.
            TypeError: if channels is not a list or channel number is not an integer.
        """
        total_channels = self._get_total_channels()

        if channels is None:
            channels = range(total_channels)
        self._validate_channels_or_raise(channels)
        self.stop_readout()

        result = self._read_scalers(channels)
        return result

    def _read_scalers(self, channels: Iterable[int]) -> list[int]:
        """Reads the scalars for the given channels, returns 0 for channels not selected."""
        result = [0 for _ in range(self.board.channels)]
        for chan in channels:
            scalar = self.read_scalar(chan)
            result[chan] = scalar
        return result

    def read_scalar(self, channel: int):
        name = self.get_scal_name(channel)
        scal = self._read_digital_register(name)
        try:
            scalhigh = self._read_digital_register("scalhigh")
        except (KeyError, AttributeError):
            scalhigh = 0
        shift_amt = DigitalRegisters(self.board).registers[name]["bitwidth"]
        scal += scalhigh << shift_amt

        return scal

    def get_scal_name(self, i):
        return f"scal{i}"

    def _get_total_channels(self) -> int:
        """Returns the total number of channels on the board."""
        return self.board.channels

    def read_firmware_version(self):
        """Read the firmware version.

        This is a control register.
        """
        result = -1
        try:
            result = ControlRegisters(self.board).read("version")["value"]
            LOGGER.debug("Firmware version: %s", result)
        except Exception:
            LOGGER.error("Can't read firmware version")
        return result

    def read_identifier(self) -> str:
        """Read the board identifier."""
        result = -1
        try:
            result = ControlRegisters(self.board).read("identifier")
        except Exception:
            LOGGER.error("Can't read board identifier")
        return result

    def enable_testmode(self, enabled: bool):
        """Enables the test-pattern output.

        Set the fpga in a mode to output a known test-pattern.
        """
        ControlRegisters(self.board).write("fake", enabled)

    def get_available_chips(self) -> list[int]:
        """Get a list of available chip numbers."""
        return list(range(self.board.params.get("num_chips", 1)))

    def set_serial_mode(self, enabled: bool):
        """Turn on or off serial mode.

        Warning: there is limited support in NaluDAQ for making sense
        of the data that comes out of a board when in serial mode, use
        at your own risk.

        Args:
            enabled (bool): True to use the serial interface, or False to
                use the parallel interface (this is the default when
                starting up a board).
        """
        if not isinstance(enabled, bool):
            raise TypeError("Argument must be bool")
        LOGGER.debug("Setting serial mode: %s", "ON" if enabled else "OFF")
        registers_to_write = {
            True: {
                "iomode1": 1,
                "iomode0": 0,
            },
            False: {
                "iomode1": 0,
                "iomode0": 1,
            },
        }[enabled]
        for name, value in registers_to_write.items():
            self._write_control_register(name, value)

    def set_loopback_enabled(self, enabled: bool):
        """Set whether serial loopback is enabled.

        Loopback can safely be disabled during most of the operations with the board.
        Loopback **must** be disabled when communicating over the serial interface.
        If serial communication with the ASIC is intended then this should run during startup and only be enabled as needed.

        Args:
            enabled (bool): True to enable loopback.

        Raises:
            TypeError if enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise TypeError("Argument must be bool")
        OFF = "B0900002"
        ON = "B0900003"
        cmd = ON if enabled else OFF
        self._send_command(cmd)

    def _write_control_register(self, register, value):
        """wrapper for the Control register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        try:
            ControlRegisters(self.board).write(register, value)
        except (ValueError, TypeError) as error_msg:
            LOGGER.error("Couldn't update control register due to: %s", error_msg)

    def _write_digital_register(self, register: str, value: int):
        """wrapper for the Control register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        try:
            DigitalRegisters(self.board).write(register, value)
        except (ValueError, TypeError) as error_msg:
            LOGGER.error("Couldn't update control register due to: %s", error_msg)

    def _read_digital_register(
        self, register: str, chips: "int | list[int] | None" = None
    ):
        """Quick access to read digital register value"""
        try:
            val = DigitalRegisters(self.board, chips).read(register)["value"]
        except (ValueError, TypeError) as error_msg:
            LOGGER.error("Couldn't read digital register due to: %s", error_msg)
        return val

    def _validate_channels_or_raise(self, channels: list[int]):
        """Raise an error if the value is not a valid list of channels"""
        if not isinstance(channels, list):
            raise TypeError(f"Channels must be a list[int], not {type_name(channels)}")
        if any(not isinstance(c, int) for c in channels):
            raise TypeError("Channels must be a list[int]")
        if any(not 0 <= c < self.board.channels for c in channels):
            raise ValueError("One or more channels is out of bounds")

    def _send_command(self, command):
        """Send the given hex command to the board.

        Args:
            command (str): hex command
        """
        if self.board.using_new_backend:
            BoardIoManager(self.board).write(command)
        else:
            self.board.connection.send(command)
