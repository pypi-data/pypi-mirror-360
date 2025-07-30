"""
The si5341 is a good clock that we use a lot

This is all the functions that can be used to control its features

Ben Rotter
"""
import logging
import time

import naludaq.communication.i2c as i2c
from naludaq.controllers.controller import Controller
from naludaq.helpers.exceptions import ClockFileError, RegisterFileError
from naludaq.io.io_manager import load_clockfile

logger = logging.getLogger(__name__)


class Si5341Controller(Controller):
    """Clock controller/programmer

    Program the Si5341 clockchip which is used on all Nalu boards.
    The prorgrammer class doesn't have any public attributes and
    thus doesn't have to be instantiated.

    Example:
    ```
    Si5341Controller(board).program()

    ```

    The board object should contain the command string to program the clock.
    It's also possible to supply the clockfile name when running.

    Example:
    ```
    Si5341Controller(board).program(filename)
    ```

    """

    def __init__(self, board):
        super().__init__(board)

        if board.params.get("si5341_address", None) is None:
            raise RegisterFileError(
                "The loaded Register file doesn't have a si5341_address specified."
            )
        self._address = board.params["si5341_address"]

    def program(self, filename=None, safe_mode=True, verbose=False):
        """Setup the clockspeed of the si5341.

        Can read the commands from a .txt file
        Loads the list of commands given by the ClockBuilder Pro program
        Sent as three words: i2cAddr -> address -> value
        If moving to new page (first byte of addr), need to send an additional "change page" command

        > This function turns off UART logging while running due to the amount of commands sent.

        Args:
            filename: full filepath to the file form Clockbuilder Pro.

        Raises:
            Errors in case the filename is invalid or the clockfile is invalid.
        """
        # if not os.path.isfile(filename):
        #     raise FileNotFoundError(f"File {filename} doesn't exist")

        if filename is None and self.board.clock_data is None:
            raise ClockFileError("No clock file loaded!")

        if filename is None and self.board.clock_data is not None:
            commands = self.board.clock_data

        if filename is not None:
            try:
                commands = load_clockfile(filename)
            except:
                raise

        if isinstance(self._address, int):
            devAddr = hex(self._address)[
                2:
            ]  # what will be seen in the logic analyzer (7 bits + 0)
        else:
            devAddr = self._address

        prevPage = "00"

        logger.info("Using si5341 config file %s", filename)
        logger.debug("Sending command to si5341...")

        uart_logger = logging.getLogger("naludaq.board.connections._UART")
        uart_logger_orig = uart_logger.level
        lvl = logging.DEBUG if verbose else logging.ERROR
        uart_logger.setLevel(lvl)

        for command in commands[1:]:
            if command[0] == "sleep":
                time.sleep(float(command[1]) / 1000.0)
                continue
            fullAddr = command[0][2:]
            page = fullAddr[:2]
            addr = fullAddr[2:]
            hexVal = command[1][2:]
            if safe_mode:
                time.sleep(0.01)

            # logger.debug("fullAddr: %s, page: %s, addr: %s, hexVal: %s", fullAddr, page, addr, hexVal)

            if prevPage != page:
                words = ["01", page]
                if not i2c.sendI2cCommand(self.board, devAddr, words, check_ack=False):
                    logger.info("No ACK recieved from Si5341")
                    return False
                logger.debug("words: %s", words)
                prevPage = page
                if safe_mode:
                    time.sleep(0.01)

            words = [addr, hexVal]

            # logger.debug("words: %s", words)
            if not i2c.sendI2cCommand(self.board, devAddr, words, check_ack=False):
                logger.info("No ACK recieved from Si5341")
                return False

        uart_logger.setLevel(uart_logger_orig)
        logger.info("si5341 init complete.")


def program(board, filename=None):
    """Program the Si5341 clockchip

    The board needs to have registers file loaded
    and preferable a clockfile loaded.

    Args:
        board: good old board
        filename (filepath): Full filepath to the clockfile, optional

    """
    Si5341Controller(board).program(filename)
