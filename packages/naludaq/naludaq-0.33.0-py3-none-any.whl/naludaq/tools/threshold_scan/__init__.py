"""Thresholdscanner

"""


def get_threshold_scanner(board, *args, **kwargs):
    """Gets a `ThresholdScan` object appropriate for a given board.

    Args:
        board (Board): the board object.

    Returns:
        The ThresholdScan object which can be used to run threshold
        scans on the board.
    """
    if board.model in ["hdsocv1_evalr1", "hdsocv1_evalr2"]:
        from naludaq.tools.threshold_scan.hdsoc_thresholdscan import ThresholdScanHdsoc

        return ThresholdScanHdsoc(board, *args, **kwargs)
    elif board.model in [
        "hdsocv2_eval",
        "hdsocv2_evalr2",
    ]:
        from naludaq.tools.threshold_scan.hdsocv2_thresholdscan import (
            ThresholdScanHdsocv2,
        )

        return ThresholdScanHdsocv2(board, *args, **kwargs)
    elif board.model in ["upac96"]:
        from naludaq.tools.threshold_scan.upac96_thresholdscan import (
            Upac96ThresholdScan,
        )

        return Upac96ThresholdScan(board, *args, **kwargs)
    elif not board.is_feature_enabled("threshold_scan"):
        raise NotImplementedError(f"Threshold scan not supported on {board.model}")
    else:
        from naludaq.tools.threshold_scan.threshold_scan import ThresholdScan

        return ThresholdScan(board, *args, **kwargs)
