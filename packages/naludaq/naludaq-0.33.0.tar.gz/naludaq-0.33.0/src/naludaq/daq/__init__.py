from naludaq.board.connections.base_serial import BaseSerialConnection
from naludaq.daq.debugdaq import DebugDaq
from naludaq.daq.debugdaq import DebugDaq as BenDaq
from naludaq.daq.hiperdaq import HiperDaq
from naludaq.daq.lightdaq import LightDaq


def get_daq(board, *args, parsed: bool = False, debug: bool = False, **kwargs):
    """Return an instantiated Daq object based on model and preferences.

    Args:
        board: board object
        parsed: should returndata be parsed or raw?
        debug: True to use a daq with more telemetry and storage options

    Returns:
        Instantiated daq object
    """
    daq = LightDaq
    if debug or parsed:
        daq = DebugDaq

    elif board.params["model"] in ["hiper"]:
        daq = HiperDaq

    return daq(board, *args, **kwargs)
