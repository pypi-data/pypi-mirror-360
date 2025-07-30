"""Initializer for the trbhm board.

It's based on the aardvarcv3 initializer because the trbhm
has two aardvarcv3 chips.
"""
import logging

from naludaq.board.initializers.aardvarcv3 import InitAardvarcv3

logger = logging.getLogger("naludaq.init_trbhm")


class InitTrbhm(InitAardvarcv3):
    def __init__(self, board):
        """Initializer for the TRBHM.

        Args:
            board (Board): the board to initialize.
        """
        super().__init__(board)
        self.power_sequence = [
            "2v5_en",
            "1v2_en",
            "3v3_i2c_en",
            "clk2v5_en",
            "clk1v8_en",
            "clk_i2c_sel",
        ]
