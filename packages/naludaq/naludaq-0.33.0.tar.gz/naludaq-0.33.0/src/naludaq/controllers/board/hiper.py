import logging
import time

from naludaq.communication import AnalogRegisters, ControlRegisters, DigitalRegisters

from .default import BoardController

logger = logging.getLogger("naludaq.board_controller.hiper")


class BoardControllerHiper(BoardController):
    def read_scalar(self, channel: int):
        raise NotImplementedError("Not yet supported")

    def reset_board(self):
        self._write_control_register("txin_en", 0)
        self._write_control_register("rxout_en", 0)
        time.sleep(0.02)
        self.sysrst()
        time.sleep(0.02)
        self._write_control_register("rxout_en", self.chip_mask())

    def chip_mask(self, chips=None):
        if chips is None:
            chips = self.board.params["installed_chips"]
        return sum([1 << chip for chip in chips])

    def start_readout(
        self,
        trig="ext",
        lb="trigrel",
        acq="raw",  # "pedsub",
        dig_head=False,
        ped="zero",
        readoutEn=True,
        singleEv=False,
    ):
        mask = self.chip_mask()
        logger.debug("Start readout of chips: %s", self.board.params["installed_chips"])
        self._write_control_register("rxout_en", mask)

        # self._write_digital_register("miscreg", 2)
        # self._write_digital_register("pllmisc", 0)
        # self._write_digital_register("txspeed", 2)
        # self._write_digital_register("waitread", 1)

        self._write_control_register("exttrig_en", mask)
        self._write_control_register("txin_en", mask)

        super().start_readout(
            trig=trig,
            lb=lb,
            acq=acq,
            dig_head=dig_head,
            ped=ped,
            readoutEn=readoutEn,
            singleEv=singleEv,
        )

    def _generate_start_readout_cmd(self, readout_params, *args, **kwargs):
        (
            trigger_type,
            lbType,
            acq_type,
            pedestals_type,
        ) = self._convert_readout_params_to_binary(readout_params)

        readoutEn = readout_params.get("readoutEn", 1)
        singleEv = readout_params.get("singleEv", 0)
        dig_head = readout_params.get("dig_head", 0)

        first_part = hex(
            int(str(int(singleEv)) + str(int(readoutEn)) + pedestals_type + "0011", 2)
        )[2:].zfill(2)

        second_part = hex(
            int("000000" + trigger_type + str(int(dig_head)) + acq_type + lbType, 2)
        )[2:].zfill(3)

        return f"B{first_part}00{second_part}"

    def stop_readout(self):
        """Upated stop command.

        All Txin_en OFF
        All Rxout_en OFF
        ASIC Sysrst
        ASIC RegClr
        All RxIn_en ON
        Verify Busy_locked
        Load default ASIC Digital Registers
        Load default ASIC Analog Registers.
        """
        self.is_reading_out = False
        cmd = "B0B00000"
        self._send_command(cmd)
        self._write_control_register("rxout_en", self.chip_mask())
        self._write_control_register("txin_en", 0)

    def toggle_trigger(self):
        self.arm_trigger()
        cmd = "AF040440" + "AF040040"
        self._send_command(cmd)

    def regclr(self):
        self._write_control_register("regclr", True)
        self._write_control_register("regclr", False)

    def _sync_tx_pol(self):
        """Set ASIC txin polarity and check if locked

        SET POLARITY TO ASIC TXIN
        IF POLAROITY AND BAUD IS NOT CORRECT IDLE_DETECT WILL BE 0
        IF POLARITY AND BAUD ARE CORRECT IDLE_DETETCT WILL BE 1
        """
        for _ in range(5):
            # ControlRegisters(self.board).write('txin_pol', 0)  # 1900 hex
            if ControlRegisters(self.board).read("idle_det")["value"] == 1:
                return True
            time.sleep(0.05)
        return False

    def _sync_rx_pol(self):
        """Set ASIC rxout pol and make sure it's locked

        SET POLARITY TO ASIC RXOUT
        IF POLAROITY AND BAUD IS NOT CORRECT BUSY_LOCKED WILL BE 0
        IF POLARITY AND BAUD ARE CORRECT BUSY_LOCKED WILL BE 1
        """
        # ControlRegisters(self.board).write("txin_en", self.chip_mask())
        for _ in range(2):
            # ControlRegisters(self.board).write('rxout_pol', 0)  # 113C hex
            busy_locked = ControlRegisters(self.board).read("busy_locked")["value"]
            if busy_locked == 1:
                return True
            logger.debug("Busy locked returned: %s", busy_locked)
            time.sleep(0.05)
        return False

    def get_available_chips(self):
        """Get a list of available chip numbers."""
        idl = ControlRegisters(self.board).read("idle_det")["value"]
        idl_str = str(bin(idl))[2:]
        available_chips = []
        for chip_num, i in enumerate(range(len(idl_str), 0, -1)):
            if int(idl_str[i - 1]):
                available_chips.append(chip_num)

        return available_chips

    def arm_trigger(self):
        """Reset the trigger counter, allowing for more triggered readouts."""
        ControlRegisters(self.board).write("trig_count_reset", True)
        ControlRegisters(self.board).write("trig_count_reset", False)

    def _write_digital_register(self, name: str, value: int):
        DigitalRegisters(self.board).write(name, value)

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

    def enable_chip(self, chips: "list[int] | int"):
        """Enable the chip for readout.

        Will turn on the chip from a disabled state.
        Only turn on the one chip that is needed for readout.

        Args:
            chip (int): The chip number to enable.
        """
        # mask = self.chip_mask([chip])
        # self._write_control_register("rxout_en", mask)
        if isinstance(chips, int):
            chips = [chips]
        self.analog_startup(chips)
        self.digital_startup(chips)
        self._write_control_register("rxout_en", self.chip_mask())

    def disable_chip(self, chips: "list[int] | int"):
        """Disable the chip for readout.

        Will turn off the chip and it will not work properly without re-enabling it.

        Args:
            chip (int): The chip number to disable.
        """
        if isinstance(chips, int):
            chips = [chips]
        mask = self.chip_mask(chips)
        ControlRegisters(self.board).write("chip_sysrst", mask)
        ControlRegisters(self.board).write("chip_sysrst", 0)
        ControlRegisters(self.board).write("chip_regclr", mask)
        ControlRegisters(self.board).write("chip_regclr", 0)
        self._write_control_register("rxout_en", self.chip_mask())

    # def write_commands(self, commands):
    #     for cmd in commands:
    #         self.board.connection.send(cmd)
    #         time.sleep(0.01)

    def digital_startup(self, chips: "list[int] | int | None" = None):
        """Start the digital side of the chip by programming all registers."""
        DigitalRegisters(self.board, chips=chips).write_all()

    def analog_startup(self, chips: "list[int] | int | None" = None):
        """Start the analog side of the chip by programming all registers."""
        AnalogRegisters(self.board, chips=chips).write_all()
        time.sleep(0.1)
        self.dll_startup(chips=chips)

    def dll_startup(self, chips: "list[int] | int | None" = None):
        """Starting the delay line on the analog side.

        Sets and unsets vanbuff to get the dll going and
        changes the vadjp values to ensure proper SST duty cycle once locked.
        """
        AnalogRegisters(self.board, chips=chips).write("qbias", 0)
        AnalogRegisters(self.board, chips=chips).write("vadjn_sw", True)
        time.sleep(1)
        AnalogRegisters(self.board, chips=chips).write("qbias", 2048)
        AnalogRegisters(self.board, chips=chips).write("vadjn_sw", False)
