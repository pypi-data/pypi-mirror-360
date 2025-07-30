import copy
from dataclasses import dataclass

from naluconfigs import get_available_models

from naludaq.helpers import type_name


@dataclass()
class Feature:
    """Dataclass describing a feature"""

    description: str
    long_description: str
    beta_models: list[str]


_FEATURES = {
    "adc2mv": Feature(
        description="ADC to mV Calibration",
        long_description="Allows calibration to convert from units of ADC to mV",
        beta_models=get_available_models(),
    ),
    "calibration_channel": Feature(
        description="Calibration Channel",
        long_description=(
            "Allows control of the calibration channel on the board. "
            "Other channels on the board may be swapped with the calibration channel."
        ),
        beta_models=[],
    ),
    "dac_sweep": Feature(
        description="External DAC Sweep",
        long_description=(
            "Gathers data at various DAC values to characterize the response to "
            "different input levels"
        ),
        beta_models=get_available_models(),
    ),
    "ext_dac": Feature(
        description="External DAC",
        long_description="Allows control of the external DAC on the board",
        beta_models=[],
    ),
    "conversion_ramp_optimizer": Feature(
        description="Amplitude Linearity Optimizer",
        long_description=(
            "Calibrates isel Ramp Current and Cap Select to put individual"
            "channels in the midrange, which can help with amplitude linearity"
        ),
        beta_models=[],
    ),
    "gain_stage_tuner": Feature(
        description="Gain Stage Tuner",
        long_description=(
            "Calibrates external dac and ISEL for a specific "
            "gain stage configuration"
        ),
        beta_models=get_available_models(),
    ),
    "pedestals": Feature(
        description="Pedestal Calibration",
        long_description="Allows generation of pedestals data and subtraction of built-in noise",
        beta_models=[],
    ),
    "threshold_scan": Feature(
        description="Threshold Scan",
        long_description=(
            "Scans over different trigger thresholds to determine the "
            "threshold at which the ASIC will trigger on a signal"
        ),
        beta_models=[],
    ),
    "tia_dac": Feature(
        description="TIA DAC",
        long_description=(
            "Enables use of the transimpedence amplifier (not present on all models) "
            "to digitize an input current rather than input voltage"
        ),
        beta_models=[],
    ),
    "timing_calibration": Feature(
        description="Timing Calibration",
        long_description=(
            "Enables calibration of the internal timing circuit "
            "for better sample-to-sample timing precision"
        ),
        beta_models=get_available_models(),
    ),
}


def features_names() -> list[str]:
    """Get a list of available feature names"""
    return list(_FEATURES.keys())


def all_feature_info() -> dict[str, Feature]:
    """Get a dictionary of all feature information"""
    return copy.deepcopy(_FEATURES)


def feature_info(feature_name: str) -> Feature:
    """Get information about about a feature"""
    _validate_feature_name_or_raise(feature_name)
    return copy.deepcopy(_FEATURES[feature_name])


def is_beta(feature_name: str, model: str) -> bool:
    """Checks whether a feature is currently beta for a given board model"""
    _validate_model_or_raise(model)
    return model in feature_info(feature_name).beta_models


def is_available(feature_name: str, model: str, board_features: dict) -> bool:
    """Checks whether the feature is available.

    Available means that the feature switch is `True` in the configs,
    and if it is a beta feature, that beta features are enabled.

    Args:
        feature_name (dict): name of the feature.
        model (str): board model
        board_features (dict): feature dict from `board.features`.

    Returns:
        bool: True if the feature is available.
    """
    _validate_feature_dict_or_raise(board_features)
    available = board_features.get(feature_name, False)
    beta_enabled = board_features.get("beta_features", False)
    if is_beta(feature_name, model) and not beta_enabled:
        available = False
    return available


def _validate_feature_name_or_raise(feature_name: str):
    """Raise an error if the feature name is wrong type/value"""
    if not isinstance(feature_name, str):
        raise TypeError(f"Name must be a string, not {type_name(feature_name)}")
    if feature_name not in _FEATURES:
        raise ValueError(f"Invalid feature name '{feature_name}'")


def _validate_feature_dict_or_raise(board_features: dict):
    """Raise an error if the board features dict is the wrong type"""
    if not isinstance(board_features, dict):
        raise TypeError(
            f"Board features must be a dict, not {type_name(board_features)}"
        )


def _validate_model_or_raise(model: str):
    """Raise an error if the board model is the wrong type/value"""
    if not isinstance(model, str):
        raise TypeError(f"Board model must be a str, not {type_name(model)}")
    if model not in get_available_models():
        raise ValueError(f"Invalid board model '{model}'")
