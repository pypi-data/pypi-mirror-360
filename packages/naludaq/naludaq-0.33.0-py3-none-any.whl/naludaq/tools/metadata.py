from copy import deepcopy
from typing import Iterable

import numpy as np

from naludaq.controllers import get_peripherals_controller
from naludaq.helpers.helper_functions import extract_event_creation_times, type_name

_missing = object()


class Metadata:
    """Proxy class for accessing metadata stored in a dictionary.

    Metadata in the dictionary is stored according to the following structure::

        {
            'params': {}, # board params dict
            'registers': {}, # board registers dict
            'sensors': [
                {...}, # generated from first call to store_sensor_readings()
                {...}, # generated from second call to store_sensor_readings()
                ...
            ],
            'times': [
                np.ndarray([...]), # generated from first call to store_event_times()
                np.ndarray([...]), # generated from second call to store_event_times()
                ...
            ],
        }
    """

    def __init__(self, metadata: dict = _missing):
        """Create helper proxy class for accessing metadata stored in a dict.

        Args:
            metadata (dict): the destination for metadata. If not provided, a new dict is used.
        """
        self.output = {} if metadata is _missing else metadata

    @property
    def output(self) -> dict:
        """Get/set the output dict for metadata"""
        return self._output

    @output.setter
    def output(self, d: dict):
        if not isinstance(d, dict):
            raise TypeError(f"Metadata output must be dict, not {type_name(d)}")
        self._output = d

    @property
    def params(self) -> dict:
        """Get/set the board params dict"""
        return self.output.setdefault("params", {})

    @params.setter
    def params(self, params: dict):
        if not isinstance(params, dict):
            raise TypeError("Params must be a dict")
        self.output["params"] = deepcopy(params)

    @property
    def registers(self):
        """Get/set the board registers dict"""
        return self.output.setdefault("registers", {})

    @registers.setter
    def registers(self, registers: dict):
        if not isinstance(registers, dict):
            raise TypeError("Registers must be a dict")
        self.output["registers"] = deepcopy(registers)

    @property
    def sensors(self) -> list[dict]:
        """Get the sensor readings list"""
        return self.output.setdefault("sensors", [])

    @property
    def times(self) -> list[np.datetime64]:
        """Get the event creation time list"""
        return self.output.setdefault("times", [])

    def set_configuration(self, board):
        """Convenience method for setting registers/params.

        Args:
            board (Board): a board-like object (i.e. having
                both ``params`` and ``registers`` attributes)
        """
        params = getattr(board, "params", _missing)
        registers = getattr(board, "registers", _missing)
        if params is _missing or registers is _missing:
            raise TypeError("Object must have params and registers attributes")
        self.params = params
        self.registers = registers

    def store_sensor_readings(self, board):
        """Read and store sensor readings into the ``sensors`` list.
        See the class docstring for details on the data structure.

        Args:
            board (Board): connected board object to read sensors from.
            key_format (str): format string to use to generate a unique key for the item.
                The format string must contain a single argument which takes an integer.
        """
        try:
            readings = get_peripherals_controller(board).read_all()
        except Exception:
            raise
        self.sensors.append(readings)

    def store_event_times(self, events: Iterable[dict]) -> np.ndarray:
        """Store event creation times into the ``times`` list.
        See the class docstring for details on the data structure.

        Args:
            events (Iterable[dict]): list of events to store creation times for.

        Returns:
            numpy.ndarray: the stored array.
        """
        self.times.append(extract_event_creation_times(events))
