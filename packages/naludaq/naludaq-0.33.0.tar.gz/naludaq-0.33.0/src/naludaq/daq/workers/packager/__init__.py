from naludaq.daq.workers.packager.worker_packager import PackagerLight
from naludaq.daq.workers.packager.worker_packager_debug import DebugPackager
from naludaq.daq.workers.packager.worker_packager_hdsoc import HDSoCPackager
from naludaq.daq.workers.packager.worker_packager_hiper import HiperPackager


def get_packager(board, *args, **kwargs):
    """Returns a Packager object for the given board."""
    if board.params["model"] in ["hdsocv1", "hdsocv1_evalr1", "hdsocv1_evalr2"]:
        return HDSoCPackager(board, *args, **kwargs)
    if board.params["model"] in ["hiper"]:
        return HiperPackager(*args, **kwargs)
    else:
        return PackagerLight(*args, **kwargs)
    # else:
    #     raise ValueError('Unknown board model: {}'.format(board.params['model']))
