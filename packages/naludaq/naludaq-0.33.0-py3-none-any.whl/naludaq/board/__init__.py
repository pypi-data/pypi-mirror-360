"""Create a board object.

Create a board object from the board class to keep track of all parameters for the board.
The board object will hold the open connection to the hardware, this is useful since it
will make sure there is only one connection and it's through the board.

By keeping all the parameters stored with a board it open up to use multiple boards and
to switch board during operation.

Example:
--------

.. code-block:: python

    brd = Board('asocv3')
    brd.load_registers()
    brd.load_clockfile()
    brd.get_uart_connection(comport="COM99", baud=115200)

"""
import pathlib
from logging import getLogger
import naluconfigs
import naluconfigs.exceptions

from naludaq.backend.context import Context
from naludaq.backend.exceptions import BackendError
from naludaq.backend.managers.config import ConfigManager
from naludaq.backend.managers.connection import ConnectionManager
from naludaq.board.board_inits import BoardInits
from naludaq.board.connections import get_connection
from naludaq.board.params import (
    add_config_to_board_from_file,
    add_default_config_to_board,
)
from naludaq.communication.control_registers import ControlRegisters
from naludaq.controllers.board import get_board_controller
from naludaq.controllers.trigger import get_trigger_controller
from naludaq.controllers.trigger.default import BaseTriggerController
from naludaq.controllers.connection import get_connection_controller
from naludaq.controllers.external_dac import get_dac_controller
from naludaq.controllers.peripherals import get_peripherals_controller
from naludaq.controllers.readout import get_readout_controller
from naludaq.controllers.clock import get_clock_controller
from naludaq.helpers.exceptions import VersionError
from naludaq.helpers.helper_functions import get_available_port
from naludaq.helpers.validations import validate_dir_or_raise
from naludaq.io.io_manager import load_clockfile

LOGGER = getLogger(__name__)

try:
    import naludaq_rs
except ImportError:
    LOGGER.info("Could not import naludaq_rs, automatic start of backend not available")
    naludaq_rs = None


class Board:
    """Representation of the hardware.

    The board object is the software representation of the physical board.
    It should be created first since it's used by all other modules.
    The purpose of the board object is to mirror the hardware state.

    Once instantiated it holds a mirror of all the parameters on the physical unit,
    it holds the connection to the unit and stores the registers mapping.
    The connection and parameters can be accessed directly if needed:

        board.params is a dictionary with the board parameters.
            {param_name": value,
            ....
            }

        board.connection
            send() will send data to the board. Takes a 32-bit word (4 bytes or 8 hex chars).
            read() listens for data from the board.

        board.register is a dictionary
            {"register_type": {
                "name": [value, address, position, width, r/w],
                ...
            }}

    Example:
        ```
        brd = Board('asocv3');
        brd.get_uart_connection(comport="COM99", baud=115200);
        ```
        Will create a board object with the parameters for the asocv3 board.

    Args:
        model(str): model name of the board
        registers(Path): optional path to the registers file, loads default if not supplied.
        clock(Path): optional path to the clock file, loads default if not supplied.


    Raises:
        InvalidBoardModelError if the supplied board model doesn't exist.
    """

    def __init__(
        self,
        model: str = "default",
        registers: "str | pathlib.Path | None" = None,
        clock: "str | pathlib.Path | None" = None,
    ):
        self._is_reading_out: "bool | None" = False
        self.model: str = model
        self.server = None
        # Params are needed for default model
        self.params = {
            "model": model,
            "channels": 4,
        }
        self.features: dict = {}
        self.registers: dict = {}
        self.registers_cache: dict = {}

        # Connection
        self._using_new_backend: bool = False
        self._last_server_address: tuple[str, int] | None = None
        self.connection_info: "dict | None" = None
        self.connection = None
        self.spi_connection = None

        # Calibration
        self.pedestals: "dict | None" = None
        self.caldata: "dict | None" = None
        self.timingcal: "list | None" = None
        self.tuning: dict = {}

        self.trigger = None
        self.readout = None
        self.control = None
        self.ext_bias = None
        self.peripherals = None
        self.clock = None

        # Hardware
        if model not in ["default"]:
            self.load_registers(registers)
            self.load_clockfile(clock)

            self.trigger: BaseTriggerController = get_trigger_controller(self)
            self.readout = get_readout_controller(self)
            self.control = get_board_controller(self)
            self.ext_bias = get_dac_controller(self)
            self.peripherals = get_peripherals_controller(self)
            try:
                self.clock = get_clock_controller(self)
            except Exception:
                LOGGER.warning("No clock file found for %s", model)

    def __del__(self):
        """Cleanup the server if it's running."""
        self.stop_server()

    @property
    def context(self) -> "Context | None":
        """Get the backend context."""
        return getattr(self, "_context", None)

    @property
    def using_new_backend(self) -> bool:
        return self._using_new_backend

    @property
    def dac_values(self):
        """Get/Set the DAC values for the channels

        Simple pass thru to the correct spot in the params structure.
        Doesn't have any validation, is used both to set and get values.
        To set, simply run board.dac_values[chan] = value
        NO validations!
        """
        return self.params["ext_dac"]["channels"]

    @property
    def available_chips(self) -> int:
        """Get the number of chips on this board"""
        return len(self.params.get("chips", [0]))

    @property
    def selected_chips(self) -> list[int]:
        """Get/set the selected chips for this board.

        This is a pass through for the communication layer's select_chips / selected_chips functions.
        Selecting chips is done by toggling control registers to mask I/O from the chips that aren't selected.
        Make sure to restore the selected chips after you're finished with what you're doing.
        """
        from naludaq.communication import selected_chips

        return selected_chips(self)

    @selected_chips.setter
    def selected_chips(self, chips: list[int]):
        from naludaq.communication.chip_selection import select_chips

        select_chips(self, chips)

    @property
    def is_reading_out(self) -> bool:
        """Get boards readout status."""
        return self._is_reading_out

    @property
    def channels(self):
        """Get the channels from the params."""
        return self.params["channels"]

    def __enter__(self):
        """Connect to the board"""
        LOGGER.debug('Entering board context ("with" block); opening connection...')
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # Handy debug logging to help users who break their code by using nested `with` blocks
        LOGGER.debug('Exiting board context ("with" block); closing connection...')
        self._in_context = False
        self.disconnect()

    def load_registers(self, registers_file=None, safe: bool = True):
        """Loads the configuration for the board, including:
        - `board.features`,
        - `board.params`,
        - and `board.registers`.

        If no file is supplied, then the defaults are used instead.

        Args:
            registers_file(str): Load from a YAML file, or from the defaults if None.
            safe (bool): whether to perform validation checks on the configuration.

        Raises:
            OSError: if the file could not be opened.
            InvalidParameterFile: if the configuration could not
                be loaded from the file or is otherwise invalid.
            InvalidRegisterFile: if the registers are invalid.
        """
        if registers_file is None:
            add_default_config_to_board(self, safe=safe)
        else:
            add_config_to_board_from_file(self, registers_file, safe=safe)

    def is_feature_enabled(self, name: str) -> bool:
        """Check whether the given feature is marked as enabled
        for this board.

        Args:
            name (str): the name of the feature (case sensitive).

        Returns:
            True if the feature is enabled, or False otherwise.
        """
        return self.features.get(name, False)

    def connect_serial(
        self, port: str, baud: int, backend_addr: tuple[str, int] = None
    ):
        """Connect to the board using a serial port. [BETA]

        Args:
            port (str): name of the comport (Windows) or device path (Linux)
            baud (int): preferred baud rate
            backend_addr: (tuple[str, int]): address of the backend,
                or None to use the previous backend
        """
        if baud is None:
            baud = max(self.params["possible_bauds"].keys())
        LOGGER.info(
            "Connecting serial with port=%s, baud_rate=%s, backend_addr=%s",
            port,
            baud,
            backend_addr,
        )
        self.connect_server(backend_addr)
        device = ConnectionManager(self).connect_serial(port, baud)
        self.connection_info = device.info
        get_connection_controller(self).configure_connection()

    def connect_d2xx(
        self, serial_number: str, baud: int, backend_addr: tuple[str, int] = None
    ):
        """Connect to the board using D2XX. [BETA]

        Args:
            serial_number (str): serial number of the board as a string
            baud (int): preferred baud rate
            backend_addr: (tuple[str, int]): address of the backend,
                or None to use the previous backend
        """
        if baud is None:
            baud = max(self.params["possible_bauds"].keys())
        LOGGER.info(
            "Connecting D2XX with serial_number=%s, baud_rate=%s, backend_addr=%s",
            serial_number,
            baud,
            backend_addr,
        )
        self.connect_server(backend_addr)
        device = ConnectionManager(self).connect_d2xx(serial_number, baud)
        self.connection_info = device.info
        get_connection_controller(self).configure_connection()

    def connect_d3xx(self, serial_number: str, backend_addr: tuple[str, int] = None):
        """Connect to the board using D3XX

        Args:
            serial_number (str): serial number of the board as a string
        """
        LOGGER.info("Connecting D3XX with serial_number=%s", serial_number)
        self.connect_server(backend_addr)
        device = ConnectionManager(self).connect_d3xx(serial_number)
        self.connection_info = device.info
        get_connection_controller(self).configure_connection()

    def connect_udp(
        self,
        board_addr: tuple[str, int],
        receiver_addr: tuple[str, int],
        backend_addr: tuple[str, int] = None,
    ):
        """Connect to the board using UDP. [BETA]

        Args:
            board_addr (tuple[str, int]): board socket address
            receiver_addr (tuple[str, int]): receiver socket address
            backend_addr: (tuple[str, int]): address of the backend,
                or None to use the previous backend
        """
        LOGGER.info(
            "Connecting UDP with board_addr=%s, receiver_addr=%s, backend_addr=%s",
            board_addr,
            receiver_addr,
            backend_addr,
        )
        self.connect_server(backend_addr)
        device = ConnectionManager(self).connect_udp(board_addr, receiver_addr)
        self.connection_info = device.info
        get_connection_controller(self).configure_connection()

    def _set_context_or_raise(self, backend_addr: tuple[str, int]):
        """Initialize a context for a backend with the given address.

        Args:
            backend_addr (tuple[str, int]): address of the backend.

        Raises:
            BackendError: if the server could not be reached
        """
        try:
            self._context = Context(backend_addr)
        except BackendError:
            raise
        self._last_server_address = backend_addr
        event_stop_word = self.params["stop_word"]
        answer_stop_word = self.params.get("register_stop_word", event_stop_word)
        ConfigManager(self).configure_packaging(
            events=event_stop_word, answers=answer_stop_word
        )
        self._using_new_backend = True

    def get_uart_connection(self, comport=None, serial_number=None, baud=None):
        """Connect to the board using UART.

        Test connecting either using comport or using serial
        sets up a connection as `self.connection`

        Args:
            comport (str): name of the comport
            serial_number(str): serial number of the board as a string
            baud (int): preferred baudrate
        """
        self.connection_info = {
            "type": "uart",
            "stop_word": self.params["stop_word"],
            "model": self.model,
            "usb_addr": comport,
            "speed": baud,
            "serial_number": serial_number,
            "new_firmware": self.params.get("new_firmware", False),
        }

        try:
            self.connection = get_connection(self.connection_info)
        except ConnectionError as e:
            raise ConnectionError(f"Failed to open connection: {e}") from e
        else:
            self._context = None
            self._using_new_backend = False
            get_connection_controller(self).configure_connection()

    def get_ftdi_connection(
        self, board_number=None, comport=None, serial_number=None, baud=None
    ):
        """Connect to the board using FTDI.

        Test connecting either using comport or using serial
        sets up a connection as `self.connection`

        Args:
            board_number (int): number of the FTDI index.
            serial_number(str): serial number of the board as a string
            baud (int): preferred baudrate
        """
        if baud is None:
            baud = self.params.get("default_baudrate", 2_000_000)

        self.connection_info = {
            "type": "ftdi",
            "stop_word": self.params["stop_word"],
            "model": self.model,
            "usb_addr": comport,
            "board_number": board_number,
            "speed": baud,
            "serial_number": serial_number,
        }

        try:
            self.connection = get_connection(self.connection_info)
        except ConnectionError as e:
            raise ConnectionError(f"Failed to open connection: {e}") from e
        else:
            self._context = None
            self._using_new_backend = False
            get_connection_controller(self).configure_connection()

    def get_ft60x_connection(
        self,
        *args,
        serial_number=None,
        **kwargs,
    ):
        """Connect to the board using FTDI.

        Test connecting either using comport or using serial
        sets up a connection as `self.connection`

        Args:
            board_number (int): number of the FTDI index.
            serial_number(str): serial number of the board as a string
            baud (int): preferred baudrate
        """
        self.connection_info = {
            "type": "ft60x",
            "stop_word": self.params["stop_word"],
            "model": self.model,
            "speed": 200_000_000,
            "serial_number": serial_number,
        }

        try:
            self.connection = get_connection(self.connection_info)
        except ConnectionError as e:
            raise ConnectionError(f"Failed to open connection: {e}") from e
        else:
            self._context = None
            self._using_new_backend = False
            get_connection_controller(self).configure_connection()

    def get_tcp_connection(self, ip: str, port: int):
        """Open a TCP connection."""
        self.connection_info = {
            "type": "tcp",
            "model": self.model,
            "stop_word": self.params["stop_word"],
            "ip": ip,
            "port": port,
            "speed": int(200e6),  # gigabit!
        }

        try:
            self.connection = get_connection(self.connection_info)
            self.connection.open()
        except ConnectionError as error_msg:
            self.connection = None
            raise ConnectionError("No connection established due to: %s", error_msg)
        else:
            self._context = None
            self._using_new_backend = False
            get_connection_controller(self).configure_connection()

    def get_udp_connection(self, board_addr: tuple, receiver_addr: tuple):
        """Open a UDP connection."""
        self.connection_info = {
            "type": "udp",
            "model": self.model,
            "stop_word": self.params["stop_word"],
            "board_addr": board_addr,
            "receiver_addr": receiver_addr,
            "speed": int(200e6),  # gigabit!
        }

        try:
            self.connection = get_connection(self.connection_info)
            self.connection.open()
        except ConnectionError as error_msg:
            self.connection = None
            raise ConnectionError("No connection established due to: %s", error_msg)
        else:
            self._context = None
            self._using_new_backend = False
            get_connection_controller(self).configure_connection()

    def get_mock_uart_connection(self, user_port, board_port, ip="127.0.0.1"):
        """Connect to a mock board.

        Args:
            user_port (tuple): the port of the user
            board_port (tuple): the port of the board
            ip (str): the ip address

        Raises:
            ConnectionError if a problem occurred
        """
        self.connection_info = {
            "ip": ip,
            "user_port": user_port,
            "board_port": board_port,
            "type": "uart",
            "mock": True,
            "stop_word": self.params["stop_word"],
            "model": self.model,
            "usb_addr": 0,
            "speed": 100,
        }

        try:
            self.connection = get_connection(self.connection_info)
        except ConnectionError as error_msg:
            raise ConnectionError("No connection established due to: %s", error_msg)
        else:
            self._context = None
            self._using_new_backend = False
            get_connection_controller(self).configure_connection()

    def load_clockfile(self, filepath=None):
        """
        Changes the clock_file parameter to filepath
        Loads the clock file into a list that is returned

        Args:
            filepath: full filepath to the clock file, or None to
                load the default clock file
        """
        if filepath is None:
            try:
                clock_data, clock_file = naluconfigs.get_clock(self.model)
            except Exception:
                raise
        else:
            try:
                if not pathlib.Path(filepath).exists():
                    raise FileNotFoundError(f"{filepath} not found")
            except Exception:
                raise
            try:
                clock_data = load_clockfile(filepath)
                clock_file = filepath

            except Exception:
                raise

        self.clock_data = clock_data
        self.params["clock_file"] = str(clock_file)
        # return self.params['clock_file']

    def connect(self):
        """Open the connection to the board. Must be called after
        using one of the ``get_XXX_connection()`` methods.

        Raises:
            ConnectionError: if the board could not be connected
        """
        if getattr(self, "connection", None) is None and self.connection_info is None:
            raise ConnectionError(
                "Cannot reconnect without a known connection. One of the get_XXX_connection() "
                "methods must be called before the connect() method. "
            )
        if self.is_connected:
            LOGGER.info("Already connected.")
            return

        if self.using_new_backend:
            ConnectionManager(self).connect_from_info(self.connection_info)
        else:
            self.connection.open()
        if not self.is_connected:
            raise ConnectionError(
                "Connection failed to open. The information used to connect to the board may "
                "be incorrect, or the board may be disconnected or powered off."
            )

    def disconnect(self):
        """Close the connection, leaving it ready for future use."""
        if self.using_new_backend:
            ConnectionManager(self).disconnect()
        else:
            try:
                self.connection.close()
            except Exception:  # pragma: no cover
                pass

    @property
    def is_connected(self) -> bool:
        """``True`` if the board is currently connected and accessible, or ``False`` otherwise."""
        connected = False
        if self.using_new_backend:
            try:
                connected = ConnectionManager(self).is_connected
            except Exception:
                pass
        else:
            connection = getattr(self, "connection", None)
            connected = connection is not None and connection.is_open
        return connected

    def connect_server(self, backend_addr: tuple[str, int] = None):
        """Connect to the backend server.

        Args:
            backend_addr (tuple[str, int]): the address of the backend server.
                If None, will attempt to connect to the previous server.

        Raises:
            BackendError: if the backend could not be reached, or attempted to
                reconnect without a prior connection.
        """
        if backend_addr is None and self._last_server_address is None:
            if naludaq_rs is None:
                raise BackendError(
                    "Cannot connect to server without the backend server started. Run `board.start_server()` first."
                )
        if backend_addr is None:
            backend_addr = self._last_server_address
        try:
            self._set_context_or_raise(backend_addr)
        except BackendError:
            raise
        try:
            self.connection_info = ConnectionManager(self).device.info
        except Exception:
            # not an error, just means it wasn't previously connected.
            # we don't really want to reset connection_info either,
            # since that means we can't use connect() to reconnect.
            pass

    def disconnect_server(self):
        """Disconnect from the server"""
        if self.using_new_backend:
            self._context = None

    @property
    def server_connected(self) -> bool:
        """Checks if the server is connected."""
        connected = False
        if self.context is not None:
            connected = self.context.is_alive
        return connected

    def start_server(
        self,
        output_dir: str,
    ):
        """Start the backend server.

        Args:
            backend_addr (tuple[str, int]): the address of the backend server.
            output_dir (str): the directory to save the output data.

        Raises:
            BackendError: if the backend could not be reached, or attempted to
                reconnect without a prior connection.
        """
        LOGGER.debug("Starting backend server")
        if naludaq_rs is None:
            raise BackendError(
                "Cannot start server without the backend server installed."
            )
        if self.server_connected:
            raise BackendError("Cannot start server while already connected.")
        validate_dir_or_raise(output_dir, "Output directory")

        port = get_available_port()
        backend_addr = ("127.0.0.1", port)

        try:
            self.server = naludaq_rs.Server(
                backend_addr,
                output_dir,
            )
            self.server.start()
        except Exception:
            self.stop_server()
            raise BackendError("Could not start backend server.")

        try:
            self.connect_server(backend_addr)
        except Exception:
            self.stop_server()
            raise BackendError("Could not connect to backend server.")

        LOGGER.debug("Backend server started using address: %s", backend_addr)

    def stop_server(self):
        """Stop the backend server."""
        if self.server:
            self.server.stop()
            self.server = None

    def initialize(self, init_start: bool = True, stat: "list | None" = None) -> bool:
        """Initialize the board.

        This will run the init sequence for the board and set up the registers.

        Args:
            init_start (bool): If True, initialize the board. If False, read values from hardware.

        Returns:
            bool: True if the board was successfully initialized.
        """
        if stat is None:
            stat = []
        if not self.is_connected:
            raise ConnectionError(
                "Cannot initialize board without a connection. Connect to the board first."
            )
        # Determine if connection is UART
        if self.using_new_backend:
            is_uart = ConnectionManager(self).is_uart_based
        else:
            is_uart = self.connection.is_uart()

        if (
            self.params["model"] in ["upac32", "upaci", "zdigitizer"] and is_uart
        ):  # , "hdsocv1", "hdsocv1_evalr1", "hdsocv1_evalr2"]
            # init_board
            if init_hardware(self, init_start):
                status = "Hardware succesfully initialized."
                stat.append((100, status))
                LOGGER.debug(status)
            else:
                status = "Hardware NOT initialized."
                stat.append((0, status))
                LOGGER.debug(status)
                self.connection = None
                return False
            return True

        cc = get_connection_controller(self)

        # Match and Reset speed
        if is_uart:
            if cc.reset_connection():
                status = "Connection is reset to default."
                stat.append((20, "Resetting connection."))
                LOGGER.debug(status)
            else:
                status = "Connection failed to reset."
                stat.append((0, status))
                LOGGER.debug(status)
                return False

        # Verify connection?
        if cc.verify_connection():
            stat.append((40, "Verifying connection."))
            status = "Connection is verified and fully functional."
            LOGGER.debug(status)
        else:
            status = "Connection NOT verified."
            stat.append((0, status))
            LOGGER.debug(status)
            return False

        # init_board? is this really not what startup should be?
        if not init_hardware(self, init_start):
            status = "Hardware NOT initialized."
            stat.append((0, status))
            LOGGER.debug(status)
            self.connection = None
            return False
        else:
            status = "Hardware succesfully initialized."
            stat.append((60, status))
            LOGGER.debug(status)

        # set_speed
        if is_uart:
            try:
                status = "Changing speed"
                stat.append((80, status))
                cc.set_speed_or_revert_to_default()
            except ConnectionError as error_msg:
                status = f"Changing baudrate failed due to: {error_msg}"
                stat.append((0, status))
                LOGGER.error(status)
                self.connection = None

        # Connections shouldn't touch this flag.
        if self.is_connected:
            status = "Board successfully started."
            stat.append((100, status))
            return True

        self.connection = None
        return False


def startup_board(
    board: Board, init_start: bool = True, stat: "list|None" = None
) -> bool:
    """Setup connection and transfer startup settings.

    The board needs to be booted to startup.
    Run the startup sequence to connect, validate connection and
    transfer all initial settings to the board.

    Args:
        board
        init_start: If False, load the init settings from the board else transfer from computer.

    Returns:
        True if board is ready to use, False if init failed.
    """
    return board.initialize(init_start, stat)


def init_hardware(board: Board, init_start=True):
    """Try to init the hardware.

    Every board has a specific set of instructions to start, initialize and
    configure the board. This runs the init function for the board in use
    and without the need to specify the board model.

    Args:
        board (board): The board object representing the physical board to
        initialize.
        init_start(bool): Init board if True or read values from hw if False.

    Returns:
        True if successfully initialized.
    """
    # Determine if connection is UART
    if board.using_new_backend:
        is_uart = ConnectionManager(board).is_uart_based
    else:
        is_uart = board.connection.is_uart()

    # Init should run at lowest speed.
    if is_uart:
        get_connection_controller(board).reset_speed()

    _read_firmware_version(board)
    _validate_firmware_version_or_raise(board)

    if init_start:
        LOGGER.debug("Trying to init board...")
        if not _init_board(board):
            LOGGER.error("Board init failed...")
            return False
        else:
            LOGGER.debug("Board successfully initalized.")
    else:
        ControlRegisters(board).read_all(True)

    if is_uart:
        get_connection_controller(board).set_speed_or_revert_to_default()

    return True


def _read_firmware_version(board):
    """Update the firmware version on the software board with the hardware firmware number."""
    try:
        board.params["firmware_version"] = get_board_controller(
            board
        ).read_firmware_version()
    except Exception as error_msg:
        LOGGER.error("Failed to read firmware version due to: %s", error_msg)
        board.params["firmware_version"] = "Unknown"


def _validate_firmware_version_or_raise(board: Board):
    """Raise an error if the firmware version on the board is too old to
    be compatible with NaluDAQ.

    Uses the "minimum_firmware_version" field in the params. If this field
    is not present, or the firmware version was not determined, no
    error is raised.

    Args:
        board (Board): board object

    Raises:
        VersionError: if the firmware version is too old.
    """
    version = board.params.get("firmware_version", None)
    minimum_version = board.params.get("minimum_firmware_version", None)
    can_compare = None not in (version, minimum_version) and version > 0
    if can_compare and version < minimum_version:
        raise VersionError(
            "The board is programmed with a deprecated firmware version.\n"
            f"The current firmware version is v{version}, while the minimum\n"
            f"required version is v{minimum_version}.\n\n"
            "Please update the firmware or use an older software version."
        )


def _init_board(board) -> bool:
    """This will run the boardspecific initialization.

    The BoardInits is a factory getting the board init sequence based on the model.
    """
    return BoardInits(board).run_init_function()
