"""SerialRead is the first piece in a multithread double buffer.

OVERVIEW:
By reading the OS serial buffer with a certain polling speed and storing it in
an internal queue buffer overflows can be avoided if readout is fast.

This serial reader extends the QThread from pyside2.
Start the serial reader together with the package creator since the
serial buffer is raw bytes and not useful for the application before
the data has been packetized.

    Functions:
         run: starts the thread
         stop: stop the thread.

"""
import logging
from collections import deque
from threading import Thread

import serial

# Create logger for application
LOGGER = logging.getLogger(__name__)


class SerialReader(Thread):
    """Thread worker to read external serial buffer.

    Moves data from the OS serial buffer to the applications
    internal serial buffer. The internal buffer is a deque.

    Args:
        ser_con (serial): Serial connection.
        serial_buffer (deque): Threadsafe external buffer to write to.
        frequency (float): Deprecated, no need to supply anymore.

    Functions:
         start: starts the thread
         stop: stop the thread.

    """

    def __init__(self, connection, serial_buffer, frequency=None):
        super().__init__()
        self._interval = 0
        self._running = True
        self.daemon = True
        self._ctrl = connection
        self._serial_buffer = serial_buffer

    @property
    def serial_buffer(self):
        """Set the serial buffer.

        Serial buffer must be deque.

        Raises:
            TypeError if input is not an deque.
        """
        return self._serial_buffer

    @serial_buffer.setter
    def serial_buffer(self, value):
        if not isinstance(value, deque):
            raise TypeError("The serial_buffer must be a deque.")

        self._serial_buffer = value

    def read_serial_worker(self):
        """Worker takes raw serial data from driver buffer and stores in internal buffer.

        This solves issues with buffer overruns on higher UART baud rates.
        Runs with the polling frequency set, if to high it draws a lot of CPU power.
        If too low you get buffer overflow.

        Returns:
            appends finished packages to the package_buffer.

        """
        # Before starting to read an event, flush the buffer from whatever.
        self._reset_input_buffer()
        try:
            while self._running and self._ctrl.is_open:
                data = self._read_serial_data()
                self._store_serial_data(data)
        except KeyboardInterrupt:
            pass

    def _reset_input_buffer(self):
        self._ctrl.reset_input_buffer()

    def _read_serial_data(self):
        data = None
        try:
            # read all that is there or wait for one byte (blocking)
            data = self._ctrl.read(self._ctrl.in_waiting or 1)
        except (serial.SerialException, AttributeError) as error_msg:
            # probably some I/O problem such as disconnected USB serial
            LOGGER.error(error_msg)
            self._running = False
            data = None
        return data

    def _store_serial_data(self, data):
        if data:
            # make a separated try-except for called user code
            try:
                self._serial_buffer.appendleft(data)
            except Exception as error_msg:
                LOGGER.error(error_msg)
                self._running = False

    def run(self):
        """Start the thread worker.

        Runs the read_data continously.
        Gathers events from serial port and store in buffer.
        """
        self._running = True
        self.read_serial_worker()

    def stop(self):
        """Stops the thread worker.

        Sets running to False and stops the loop.
        """
        LOGGER.debug("Serial worker thread stopping, stop command received")
        self._running = False
