def get_clock_controller(board):
    if (
        board.params.get("clock_file", None) is None
        or board.params.get("si5341_address", None) == "None"
    ):
        return None
        # raise NotImplementedError(
        #     "The loaded Register file doesn't have a clock_file specified"
        # )
    from naludaq.controllers.clock.si5341_controller import Si5341Controller

    return Si5341Controller(board)
