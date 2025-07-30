import pytest
from naludaq.board import Board

BOARD_MODELS = ["aodsoc_asoc", "aodsoc_aods"]


class TestTriggerControllerAodsoc:
    @pytest.fixture(autouse=True)
    def setup_board(self):
        self.boards = {}
        for model in BOARD_MODELS:
            self.boards[model] = Board(model)

    @pytest.mark.parametrize("model", BOARD_MODELS)
    def test_set_wbiases(self, mocker, model):
        board = self.boards[model]
        # Mock the _write_analog_registers_per_chip method
        tc_mock = mocker.patch.object(board.trigger, "_write_analog_registers_per_chip")
        mocker.patch.object(
            board.trigger, "values", {0: 1, 1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1, 7: 0}
        )
        mocker.patch.object(
            board.trigger,
            "wbias",
            {0: 10, 1: 20, 2: 30, 3: 40, 4: 50, 5: 60, 6: 70, 7: 80},
        )
        # Expected wbias values after processing
        expected_wbias = {0: 10, 1: 0, 2: 30, 3: 0, 4: 50, 5: 0, 6: 70, 7: 0}
        board.trigger._set_wbiases()

        # Assert the _write_analog_registers_per_chip method was called with the correct arguments
        tc_mock._write_analog_registers_per_chip.assert_called_once_with(
            "wbias_{:02}", expected_wbias
        )
