def get_data_collector(board):
    if board.model in ["upac96", "udc16"]:
        from .udc16 import Udc16DataCollector

        return Udc16DataCollector(board)
    else:
        from .default import DataCollector

        return DataCollector(board)
