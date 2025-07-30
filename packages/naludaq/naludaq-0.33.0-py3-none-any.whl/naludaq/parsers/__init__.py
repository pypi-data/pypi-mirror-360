from .aardvarcv3_parser import Aardvarcv3Parser
from .aodsoc_parser import OddsockParser
from .asocv3_parser import ASoCv3Parser
from .asocv3s_parser import ASoCv3SParser
from .hdsoc_parser import HDSoCParser
from .hiper_parser import HiperParser
from .parser import Parser
from .trbhm_parser import TRBHMParser
from .udc_parser import UDCParser
from .upac96_parser import Upac96Parser
from .upac_parser import UPACParser

PARSERS = {
    "aardvarcv3": Aardvarcv3Parser,
    "aardvarcv4": Aardvarcv3Parser,
    "aodsoc_aods": OddsockParser,
    "aodsoc_asoc": OddsockParser,
    "asocv3": ASoCv3Parser,
    "asocv3s": ASoCv3SParser,
    "hdsocv1": HDSoCParser,
    "hdsocv1_evalr1": HDSoCParser,
    "hdsocv1_evalr2": HDSoCParser,
    "hdsocv2_eval": HDSoCParser,
    "hdsocv2_evalr2": HDSoCParser,
    "hiper": HiperParser,
    "trbhm": TRBHMParser,
    "dsa-c10-8": TRBHMParser,
    "udc16": UDCParser,
    "upac32": UPACParser,
    "upac96": Upac96Parser,
    "upaci": UPACParser,
    "zdigitizer": UPACParser,
}


def get_parser(params):
    """Return a parser object for the board.

    Args:
        params (dict): Dictionary with the parser parameters.
        These are generally part of the board.params.

    Returns:
        instantiated parser object. ready to roll!
    """
    model = params.get("model", "default")
    p = PARSERS.get(model, Parser)

    return p(params)
