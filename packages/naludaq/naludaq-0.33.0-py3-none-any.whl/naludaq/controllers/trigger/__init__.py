"""
"""


def get_trigger_controller(board):
    """Get the controller for the model you are using.

    This is a small factory to give you the correct class without the user caring.

    Args:
        board (Board): the board object.

    Returns:
        Instantiated TriggerController
    """
    if board.model in ["aodsoc_aods", "aodsoc_asoc"]:
        from naludaq.controllers.trigger.aodsoc import TriggerControllerAodsoc

        return TriggerControllerAodsoc(board)
    elif board.model in ["hdsocv1", "hdsocv1_evalr1", "hdsocv1_evalr2"]:
        from naludaq.controllers.trigger.hdsoc import TriggerControllerHdsoc

        return TriggerControllerHdsoc(board)
    elif board.model in ["hdsocv2_eval", "hdsocv2_evalr2"]:
        from naludaq.controllers.trigger.hdsocv2 import TriggerControllerHdsocv2

        return TriggerControllerHdsocv2(board)
    elif board.model in ["upac32", "upaci", "zdigitizer"]:
        from naludaq.controllers.trigger.upac import TriggerControllerUpac

        return TriggerControllerUpac(board)
    elif board.model == "upac96":
        from naludaq.controllers.trigger.upac96 import TriggerControllerUpac96

        return TriggerControllerUpac96(board)
    elif board.model == "siread":
        from naludaq.controllers.trigger.siread import TriggerControllerSiread

        return TriggerControllerSiread(board)
    elif board.model in ["trbhm", "dsa-c10-8"]:
        from naludaq.controllers.trigger.trbhm import TriggerControllerTrbhm

        return TriggerControllerTrbhm(board)
    else:
        from naludaq.controllers.trigger.default import TriggerController

        return TriggerController(board)
