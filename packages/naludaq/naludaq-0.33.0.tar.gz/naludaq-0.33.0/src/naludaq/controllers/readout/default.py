"""Readout settings for the board.

Controls the readout channels and the readout windows.
"""
from logging import getLogger
from typing import List, Tuple

from naludaq.communication import AnalogRegisters, ControlRegisters, DigitalRegisters
from naludaq.controllers.controller import Controller

LOGGER = getLogger("naludaq.readout_controller_default")
MAX_READOUT = 65536


class ReadoutController(Controller):
    """Handles all logic for readout settings.


    Functions:
    set_read_window
    set_number_events_to_read
    set_readout_channels
    get_readout_channels

    """

    def __init__(self, board):
        super().__init__(board)

    @property
    def windows(self):
        """Get the number of windows to read."""
        reg = "readoutwindows"
        return self.board.registers["digital_registers"][reg]["value"][0]

    @property
    def lookback(self):
        """Get the number of windows to look back."""
        reg = "readoutlookback"
        return self.board.registers["digital_registers"][reg]["value"][0]

    @property
    def write_after_trig(self):
        """Get the number of windows to write after trigger."""
        reg = "writeaftertrig"
        return self.board.registers["digital_registers"][reg]["value"][0]

    def set_record_window(self, record_length: int, pre_trigger: int):
        """Set the read window for non-forced mode using the pre-trigger
        and record length.

        Args:
            pre_trigger (int): the number of windows before the trigger event
                to start reading at.
            record_length (int): the number of windows to read.
        """
        # validate
        if not isinstance(pre_trigger, int):
            raise TypeError(
                f"Horizontal position should be int, got {type(pre_trigger)}."
            )
        if not isinstance(record_length, int):
            raise TypeError(
                f"Horizontal scale should be int, got {type(record_length)}."
            )
        if not 0 <= pre_trigger <= self.board.params["windows"]:
            raise ValueError(f"Horizontal position out of bounds, got {pre_trigger}.")
        if not 1 <= record_length <= self.board.params["windows"]:
            raise ValueError(f"Horizontal scale out of bounds, got {record_length}.")

        # Logic
        window, lookback, write_after_trig = self.record_to_readout_window(
            record_length, pre_trigger
        )
        return self.set_read_window(
            windows=window,
            lookback=lookback,
            write_after_trig=write_after_trig,
        )

    def record_to_readout_window(
        self, record_length: int, pre_trigger: int
    ) -> Tuple[int, int, int]:
        """Get the read window for non-forced mode using the pre-trigger and record length."""
        wat_min = 0
        write_after_trig = max(record_length - pre_trigger, wat_min)
        lookback = pre_trigger if write_after_trig == wat_min else record_length
        windows = record_length
        return (windows, lookback, write_after_trig)

    def record_to_readout_window_forced(
        self, record_length: int, pre_trigger: int
    ) -> Tuple[int, int, int]:
        """Get the read window for non-forced mode using the pre-trigger and record length."""
        write_after_trig = self.board.params["windows"]
        lookback = pre_trigger
        windows = record_length
        return (windows, lookback, write_after_trig)

    def read_to_record_window(
        self, windows: int, lookback: int, write_after_trig: int
    ) -> Tuple[int, int]:
        """Get the read window for non-forced mode using the pre-trigger and record length.

        This function is missing the scenario where the write_after trigger is bigger than lookback.
        This is because the NaluScope logic doesn't allow for this scenario.

        Currently it will return the pre_trigger as negative.
        """
        record_length = windows
        pre_trigger = max(lookback - write_after_trig, 0)
        return (record_length, pre_trigger)

    def read_to_record_window_forced(
        self, windows: int, lookback: int, write_after_trig: int = None
    ) -> Tuple[int, int]:
        """Get the read window for forced mode using the start window and record length."""
        record_length = windows
        start_window = lookback
        return (record_length, start_window)

    def set_record_window_forced(self, record_length: int, start_window: int):
        """Set the read window for forced mode using the start window
        and record length.

        Args:
            start_window (int): the window in the sampling array to start at.
            record_length (int): the number of windows to read.
        """
        return self.set_read_window(
            windows=record_length,
            lookback=start_window,
            write_after_trig=record_length,
        )

    def set_read_window(self, windows=None, lookback=None, write_after_trig=None):
        """Setup the readwindow on the timescale.

        Args:
            windows(int): Amount of readout windows to read.
            lookback(int): How many windows to lookback after trigger, or in forced mode it's the
                actual window number.
            write_after_trigger(int): readout addresses to write after trig. ! 1 addr = 2 windows!
        """
        if windows is not None:
            if not isinstance(windows, int):
                raise TypeError(f"windows should be int or None, got {type(windows)}")
            if not 0 <= windows <= self.board.params["windows"]:
                raise ValueError(f"windows out of bounds, got {windows}")

        if lookback is not None:
            if not isinstance(lookback, (type(None), int)):
                raise TypeError(f"lookback should be int or None, got {type(lookback)}")
            if not 0 <= lookback <= self.board.params["windows"]:
                raise ValueError(f"lookback out of bounds, got {lookback}")

        if write_after_trig is not None:
            # self.max_write_after_trig
            wat_max_bit = None
            wat_max_bit = (
                self.board.params.get("registers", {})
                .get("digital_registers", {})
                .get("writeaftertrig", {})
                .get("bitwidth", 12)
            )
            if not wat_max_bit:
                wat_max_bit = 12
            wat_max = 2**wat_max_bit

            if not isinstance(write_after_trig, (type(None), int)):
                raise TypeError(
                    f"write_after_trig should be int or None, "
                    f"got {type(write_after_trig)}"
                )
            if not 0 <= write_after_trig <= wat_max:
                raise ValueError(
                    f"write_after_trig out of bounds, got {write_after_trig}"
                )

        LOGGER.debug(
            "Set readwindow to: w%s, l%s, t:%s", windows, lookback, write_after_trig
        )
        if self.board.params["model"].lower() == "siread":
            win_reg = "numwinds"
            lookback_reg = "lookback"
        else:
            win_reg = "readoutwindows"
            lookback_reg = "readoutlookback"
        write_after_trig_reg = "writeaftertrig"

        if windows is not None:
            self._write_read_window(win_reg, windows)
        if lookback is not None:
            self._write_read_window(lookback_reg, lookback)
        if write_after_trig is not None:
            write_after_trig = self._compute_write_after_trig(
                write_after_trig
            )  # Remember, readout address is 2 windows.
            self._write_read_window(write_after_trig_reg, write_after_trig)
        return (windows, lookback, write_after_trig)

    def _compute_write_after_trig(self, write_after_trig):
        """Most ASICs use 2 windows per readout address, so we need to divide by 2."""
        return write_after_trig // 2

    def _write_read_window(self, digital_register, value):
        """write read window settings to board.

        This is an adapter function since SiREAD use a different register.
        It will update the ocrrect register depending on the board used.

        Args:
            digital_register(str): register to write
            value(int): value to set.
        """
        if self.board.params["model"].lower() == "siread":
            self._write_control_register(digital_register, value)
        else:
            self._write_digital_register(digital_register, value)

    def number_events_to_read(self, amount: int) -> None:
        """Tell the board the maximum number of events to readout.

        This only works if the readout is set with singleEv is set to True.

        Args:
            amount (int): MAximum number of events to read. 16-bit register.
        """
        if not isinstance(amount, int):
            raise TypeError(f"amount must be an integer, got {type(amount)}")
        if not 0 <= amount < MAX_READOUT:
            raise ValueError("amount must be an positive integer smaller than 65536.")
        self._write_control_register("runevs", amount)

    def set_readout_channels(self, channels_to_read: list):
        """Select channels to readout.

        Update the registers and write them to the board.

        Args:
            channels_to_read(list): List of channel numbers to read
        """
        self._validate_channels_or_raise(channels_to_read)
        chansel = self._generate_channels_bits(channels_to_read)

        if self.board.params["model"].lower() == "siread":
            self._set_readout_channels_siread(chansel)
        else:
            self._set_readout_channels_generic(chansel)

    def _validate_channels_or_raise(self, channels: List[int], min_valid=1):
        """Validates a list of channels.

        Args:
            channels (List[int]): the list of channels
            min_valid (int): minimum number of channels that must
                be present in the list to be considered valid.

        Raises:
            TypeError if the list or an element in the list are the wrong type
            ValueError if the list is too large, too small, or contains a channel
                number that is out of bounds.
        """
        if not isinstance(channels, list):
            raise TypeError(f"Channels must be a list, got {type(channels)}.")
        if not (min_valid <= len(channels) <= self.board.channels):
            raise ValueError(
                f"List of channels needs to contain between {min_valid} and "
                f"{self.board.channels} channels."
            )
        if not all(isinstance(x, int) for x in channels):
            raise TypeError(f"Channel numbers must be integers.")
        if max(channels or [0]) > self.board.channels or min(channels or [0]) < 0:
            raise ValueError(f"At least one channel number is out of bounds.")

    def _generate_channels_bits(self, channels_to_read):
        """Generates the chansel bitstring from a list fo channels.

        Args:
            channels_to_read(list): List of channel numbers to read.

        Returns:
            String of '1' and '0' where position repsresents channel.
        """
        chansel = str()
        for i in range(self.board.params["channels"]):
            if i in channels_to_read:
                chansel = "1" + chansel
            else:
                chansel = "0" + chansel
        return chansel

    def _set_readout_channels_generic(self, chansel):
        """Select readout channels for all non-siread boards."""
        self._write_control_register("chansel", int(chansel, 2))

    def _set_readout_channels_siread(self, chansel):
        """Select readout channels for the siread board.
        The siread uses two 16 bit registers for the channels (32 ch -> 32 bit).
        """
        self._write_control_register("chanselb", int(chansel[0:16], 2))
        self._write_control_register("chansela", int(chansel[16:], 2))

    def get_readout_channels(self):
        """Get the current channels to read out.

        Returns:
            Sorted list of channel numbers to read out.
        """
        if self.board.params["model"].lower() == "siread":
            return self._get_readout_channels_siread()
        else:
            return self._get_readout_channels_generic()

    def _get_readout_channels_siread(self):
        """Returns the channels for siread since it uses two registers instead of one.

        Returns:
            List of channels currently set to read out in numerical order.
        """
        chansela = self.board.registers["control_registers"]["chansela"]
        chanselb = self.board.registers["control_registers"]["chanselb"]
        result = list()
        result.extend(
            [
                (x)
                for x, val in enumerate(reversed(list(bin(chanselb[0])[2:])))
                if int(val) == 1
            ]
        )
        result.extend(
            [
                (x)
                for x, val in enumerate(reversed(list(bin(chansela[0])[2:])))
                if int(val) == 1
            ]
        )
        return result

    def _get_readout_channels_generic(self):
        chansel = self.board.registers["control_registers"]["chansel"]
        return [
            (x)
            for x, val in enumerate(reversed(list(bin(chansel["value"])[2:])))
            if int(val) == 1
        ]

    def _write_analog_register(
        self,
        register: str,
        value: int,
        chips: "int | list[int] | None" = None,
    ):
        """Helper function for writing analog registers.

        Args:
            register (str): register name
            value (int): value to write.
        """
        AnalogRegisters(self.board, chips).write(register, value)

    def _write_control_register(self, register: str, value: int):
        """Helper function for writing control registers.

        Args:
            register (str): register name
            value (int): value to write.
        """
        ControlRegisters(self.board).write(register, value)

    def _write_digital_register(self, register: str, value: int):
        """Helper function for writing digital registers.

        Args:
            register (str): register name
            value (int): value to write.
        """
        DigitalRegisters(self.board).write(register, value)
