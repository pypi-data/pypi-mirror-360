"""
"""


from naludaq.controllers.trigger.default import TriggerController


class TriggerControllerSiread(TriggerController):
    def __init__(self, board):
        super().__init__(board)
        self.banks = 4
