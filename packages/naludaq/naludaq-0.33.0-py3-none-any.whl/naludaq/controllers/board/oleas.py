import logging

from .aodsoc import BoardControllerAodsoc

LOGGER = logging.getLogger("naludaq.board_controller_oleas")


class BoardControllerOleas(BoardControllerAodsoc):
    """Board controller for OLEAS (AODSOC AODS) board."""

    def set_oleas_enabled(self, en_trig: bool, en_a: bool, en_b: bool):
        """Set whether the oleas trigger or A/B are enabled."""
        self._write_control_register("oleas_en_trig", en_trig)
        self._write_control_register("oleas_en_a", en_a)
        self._write_control_register("oleas_en_b", en_b)

    def set_oleas_a(self, length: int, delay: int, polarity: int):
        """Sets the OLEAS A registers"""
        self._write_oleas_regs(0, length, delay, polarity)

    def set_oleas_b(self, length: int, delay: int, polarity: int):
        """Sets the OLEAS B registers"""
        self._write_oleas_regs(1, length, delay, polarity)

    def set_oleas_loop(self, loop: int):
        if not isinstance(loop, int):
            raise TypeError("Must be an int")
        if not 0 <= loop < 2**5:
            raise ValueError("Value out of bounds")
        self._write_control_register("oleas_loop", loop)

    def _write_oleas_regs(self, side: int, length: int, delay: int, polarity: int):
        """Write to the oleas A/B registers."""
        if not isinstance(length, int):
            raise TypeError("Length must be an int")
        if not isinstance(delay, int):
            raise TypeError("Length must be an int")
        if not isinstance(polarity, int):
            raise TypeError("Length must be an int or bool")
        if not 0 <= length < 2**16:
            raise ValueError("Length out of bounds")
        if not 0 <= delay < 2**16:
            raise ValueError("Delay out of bounds")
        if polarity not in [0, 1]:
            raise ValueError("Polarity must be 0 or 1")
        if side not in [0, 1]:
            raise ValueError("Side must be 0 or 1")
        suffix = {
            0: "a",
            1: "b",
        }[side]
        self._write_control_register(f"oleas_length_{suffix}", length)
        self._write_control_register(f"oleas_delay_{suffix}", delay)
        self._write_control_register(f"oleas_pol_{suffix}", polarity)
