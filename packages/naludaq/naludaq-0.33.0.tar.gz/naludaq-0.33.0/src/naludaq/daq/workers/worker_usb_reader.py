"""Worker for reading out FT60x data.

"""
import logging
import time

from naludaq.daq.workers.worker_serial_reader import SerialReader

LOGGER = logging.getLogger("naludaq.usb_reader")


class UsbReader(SerialReader):
    def __init__(self, connection, serial_buffer, *args, frequency=1000, **kwargs):
        super().__init__(connection, serial_buffer, *args, **kwargs)
        self._frequency = frequency
        self._max_interval = 0.01
        self._min_interval = 0.0001
        self._interval = self._clamp_interval(1 / frequency)

    def _reset_frequency(self):
        self._interval = 1.0 / self._frequency

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
                if len(data) != 0:
                    self._store_serial_data(data)
        except KeyboardInterrupt:
            pass

    def _read_serial_data(self):
        data = None
        try:
            # read all that is there or wait for one byte (blocking)
            data = self._ctrl.read(self._ctrl.in_waiting or 2)
        except Exception as error_msg:
            # probably some I/O problem such as disconnected USB serial
            LOGGER.error(error_msg)
            self._running = False
            data = None
        if len(data) <= 0:
            time.sleep(self._interval)
            self._interval = self._clamp_interval(self._interval * 1.2)
        else:
            self._interval = self._clamp_interval(1.0 / self._frequency)
        return data

    def _clamp_interval(self, interval: float) -> float:
        """Clamp the given interval between `self._min_interval` and `self._max_interval`."""
        return min(max(interval, self._min_interval), self._max_interval)
