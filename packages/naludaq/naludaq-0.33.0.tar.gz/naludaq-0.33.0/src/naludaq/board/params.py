"""Module for loading configurations (i.e. the stuff in YAML files) into
a board object.

There is a single public function `add_config_to_board()` whose purpose is
to validation the configuration, tweak (transform) the values a bit to
make sure they're appropriate for use in NaluDaq, and to populate the
board object with them.

## Validation
-------------
Validation is performed on a configuration dict to make sure that the
core configurations exist in the appropriate structure. Without proper
validation, the configuration necessary all throughout NaluDaq
may be malformed, and cause annoying problems.

**Note:** it is possible to turn off validation using the `safe` flag.
This should be avoided unless you know that your YAML is broken but
you don't care.

Expected structure:
    {
        'model': name of the model as a string
        'features': dict of features
        'params': dict of params -- certain required params must exist.
        'registers': {
            'analog_registers': dict, not required on UPAC
            'digital_registers': dict, not required on UPAC
            'control_registers': dict
        }
    }


Note that the registers are also checked to make sure no registers
in the same register space share the same portion of an register.

The external DAC also has additional validation:
    'ext_dac': {
        'max_counts': int
        'max_mv': int
        'channels': {
            channel number: value as int
        }
    }

## Transforms
-------------
Some aspects of the configuration are tweaked and are slightly different than
what they are set as in the YAML:

- the 'model' top-level entry is moved to 'params'.
- the address for all registers is converted to a hex string if they are not already.
- all stop words under 'params' are converted to bytes if they are not already.


## Board Population
-------------------
Once the validation and transforms are applied, the board gets populated with the
configuration:

- `board.params` holds the 'params' sub-dict
- `board.registers` holds the 'registers' sub-dict
- `board.features` holds the 'features' sub-dict

Trigger values and offsets are stored into the board as well:
- `board.trigger.offsets` is set using calculated values
- `board.trigger.values` is set using calculated values
"""
from copy import deepcopy
from os import PathLike
from pathlib import Path
from typing import Tuple

import naluconfigs
import numpy as np

from naludaq.communication.registers import find_conflicting_registers
from naludaq.helpers.exceptions import InvalidBoardModelError, InvalidParameterFile


def add_config_to_board_from_file(
    board: object, config_file: PathLike, safe: bool = True
):
    """Loads configuration from a file and adds it to the board using `add_config_to_board()`.

    Args:
        board (object): the board object.
        config_file (PathLike): the configuration file to load. Must be a valid YAML.
        safe (bool): whether to skip validation checks.

    Raises:
        OSError: if the file could not be opened.
        InvalidParameterFile: if the configuration could not
            be loaded from the file or is otherwise invalid.
        InvalidRegisterFile: if the registers are invalid.
    """
    config = _read_yaml_config_or_raise(config_file)
    add_config_to_board(board, config, safe=safe)


def add_default_config_to_board(board: object, safe: bool = True):
    """Loads the default configuration from NaluConfigs and adds it to the board.

    Args:
        board (object): the board object.
        safe (bool): whether to perform validation checks on the
            configuration before applying it to the board.

    Raises:
        InvalidParameterFile: if the configuration is invalid.
        InvalidRegisterFile: if the registers are invalid.
        InvalidBoardModel: if there is no default for the given board
    """
    try:
        config = naluconfigs.get_configuration(board.model)
    except naluconfigs.InvalidBoardModelError:
        raise InvalidBoardModelError(
            f"No default configuration found for model: {board.model}"
        )
    add_config_to_board(board, config, safe=safe)


def add_config_to_board(board: object, config: dict, safe: bool = True):
    """Validate and add configuration to the board object.
    See the module docstring for the validation performed on the
    configuration.

    Note: the transforms performed in this function mutate the dict.

    Args:
        board (object): the board object
        config (dict): the configuration dictionary loaded
        safe (bool): whether to perform validation checks on the
            configuration before applying it to the board.

    Raises:
        InvalidParameterFile: if the configuration is invalid.
        InvalidRegisterFile: if the registers are invalid.
    """
    if safe:
        _validate_config_or_raise(config)
    _apply_transforms_to_config(config)
    _add_config_to_board(board, config)


def _read_yaml_config_or_raise(file: PathLike) -> dict:
    """Reads a configuration (YAML) file into a dict.

    Args:
        file (PathLike): the YAML file to load.

    Raises:
        OSError: if the file could not be opened.
        InvalidParameterFile: if the configuration could not be loaded
            from the file.

    Returns:
        dict: the configuration.
    """
    file = Path(file).absolute()
    if not file.exists():
        raise FileNotFoundError(f"The file {file} does not exist")
    if file.suffix.lower() not in [".yml", ".yaml"]:
        raise InvalidParameterFile("Invalid file type; only YAML files are supported")

    try:
        # Can't directly load with yaml.load_safe() since naluconfigs does processing
        return naluconfigs.get_configuration_from_file(file)
    except OSError:
        raise OSError(f"The file {file} could not be opened")
    except naluconfigs.ConfigurationFileParsingError as e:
        raise InvalidParameterFile(f"The file {file} is not a valid YAML file") from e
    except Exception as e:  # pragma: no coverage
        raise InvalidParameterFile(
            f"The file {file} could not be loaded"
        ) from e  # pragma: no coverage


# ========================== Populators ==========================
def _add_config_to_board(board, config: dict):
    """Populate the board object with the configuration.

    Args:
        board (Board): the board object
        config (dict): the configuration dictionary
    """
    board.model = config["model"]
    board.features = config.get("features", {})
    board.params = config["params"]
    board.default_params = deepcopy(config["params"])
    board.registers = config["registers"]


# ========================== Transforms ==========================
_STOPWORD_KEYS = [
    "stop_word",
    "register_stop_word",
]


def _apply_transforms_to_config(config: dict):
    """Applies relevant "transforms" to the dictionary:
    - convert register addresses to hex strings
    - convert stopwords to bytes
    """
    config.get("params", {})["model"] = config["model"]
    _convert_register_addresses_to_hex(config)
    _convert_stopwords_to_bytes(config)
    _add_channel_shift_entry(config)


def _convert_register_addresses_to_hex(config: dict):
    """Convert all register addresses to hex strings"""
    for register_group in config.get("registers", {}).values():
        for reg in register_group.values():
            addr = reg["address"]
            if isinstance(addr, int):
                reg["address"] = hex(addr)[2:].zfill(2)


def _convert_stopwords_to_bytes(config: dict):
    """Convert all stopwords in `_STOPWORD_KEYS` to bytes."""
    params = config["params"]
    for stop_word in _STOPWORD_KEYS:
        value = params.get(stop_word, bytes())
        if not isinstance(value, bytes):
            params[stop_word] = bytes.fromhex(value)


def _add_channel_shift_entry(config: dict):
    """Calculate and add the `chanshift` field to the params if it is not present.

    Args:
        config (dict): the configuration.
    """
    params = config.get("params", {})
    chanmask = params.get("chanmask", None)
    if chanmask is not None:
        params.setdefault("chanshift", _calculate_channel_shift(chanmask))


# ========================== Validation ==========================
_REGISTER_TYPE_EXCEPTIONS = {
    **dict.fromkeys(["upac32", "upaci", "zdigitizer"], ["control_registers"])
}
_EXT_DAC_CHANNEL_EXCEPTIONS = {
    **dict.fromkeys(
        ["upac32", "upaci", "zdigitizer"], {k: int for k in range(0, 32, 8)}
    ),
    "upac96": {k: int for k in range(0, 96, 16)},
}


def validate_config_file_or_raise(config_file: "str | Path"):
    """Validates a configuration file. See the module docstring
    for more information on the specific checks.

    Args:
        config (str | Path): the configuration file

    Raises:
        InvalidParameterFile: if the configuration is invalid.
    """
    config = _read_yaml_config_or_raise(config_file)
    _validate_config_or_raise(config)


def _validate_config_or_raise(config: dict):
    """Validates the configuration. See the module docstring
    for more information on the specific checks.

    Args:
        config (dict): the configuration

    Raises:
        InvalidParameterFile: if the configuration is invalid.
    """
    # The order of the checks is important since each check is self-contained and assumes
    # that everything it needs is present.  This way, each step doesn't have to repeat previous checks
    _check_for_top_level_entries(config)

    _check_for_register_types(config)
    _validate_registers_entries(config)
    _check_for_register_conflicts(config)

    _check_for_minimum_params_entries(config)
    _check_ext_dac_entries(config)


def _check_for_top_level_entries(config: dict):
    """Makes sure the configuration dict has the appropriate top-level entries:
    - model (str)
    - feature (dict)
    - params (dict)
    - registers (dict)

    Args:
        config (dict): the configuration dict

    Raises:
        InvalidParameterFile: if any required fields are missing or have the wrong type,
            or if there are extra top-level keys.
    """
    required_entries = {
        "model": str,
        "features": dict,
        "params": dict,
        "registers": dict,
    }
    missing, extra, invalid = _crosscheck_dict(config, required_entries)
    if missing:
        raise InvalidParameterFile(f"Missing required top-level key(s): {missing}")
    if extra:  # Probably an indentation problem
        raise InvalidParameterFile(f"Found extra top-level key(s): {extra}")
    if invalid:
        raise InvalidParameterFile(f"Incorrect types in top-level key(s): {invalid}")


def _check_for_register_types(config: dict):
    """Makes sure the board has the appropriate types of registers:
    - analog_registers
    - control_registers
    - digital_registers
    - i2c_registers

    On the UPAC series of boards, only control registers are needed.

    Args:
        config (dict): the configuration

    Raises:
        InvalidParameterFile: if the configuration is missing one or more
            types of registers or they are not a `dict`, or if there
            are extra types.
    """
    required_types = [
        "analog_registers",
        "control_registers",
        "digital_registers",
        "i2c_registers",
    ]
    required_types = _REGISTER_TYPE_EXCEPTIONS.get(config["model"], required_types)
    required_types = {x: dict for x in required_types}

    missing, extra, invalid = _crosscheck_dict(config["registers"], required_types)
    if missing:
        raise InvalidParameterFile(f"Missing register type(s): {missing}")
    if extra:  # probably an indentation problem
        raise InvalidParameterFile(f"Found extra register type(s): {extra}")
    if invalid:
        raise InvalidParameterFile(f"All registers types must be dict: {invalid}")


def _check_for_register_conflicts(config: dict):
    """Check for registers that incorrectly share portions of the same register space.

    Args:
        config (dict): the configuration

    Raises:
        InvalidParameterFile: if there are conflicting registers.
    """
    registers_to_check = config["registers"].items()

    for key, register in registers_to_check:
        conflicts = find_conflicting_registers(register)
        if conflicts:
            raise InvalidParameterFile(
                f"These registers in {key} have conflicting bits: {conflicts}"
            )


def _validate_registers_entries(config: dict):
    """Check if registers have valid entries.
    ONLY CHECKS BITWIDTH, other checks can be added

    Args:
        config (dict): the configuration

    Raises:
        InvalidParameterFile: if there are registers with invalid entries.
    """
    bad_bitwidths = [
        name
        for reg in config["registers"].values()
        for name, entry in reg.items()
        if entry["bitwidth"] <= 0
    ]

    if bad_bitwidths:
        raise InvalidParameterFile(
            f"These registers have invalid bitwidths: {bad_bitwidths}"
        )


def _check_ext_dac_entries(config: dict):
    """Makes sure the `ext_dac` field of the parameters file is valid.

    Makes sure the following fields exist:
    - max_counts (int)
    - max_mv (int)
    - channels (dict[int, int])

    The `channels` entry is further validated by making sure the channel numbers
    are correct for the model in question.

    Args:
        config (dict): the configuration

    Raises:
        InvalidParameterFile: if any entries are missing or have the wrong type,
            or if the channels are incorrect for the board.
    """
    ext_dac = config["params"].get("ext_dac", None)
    if ext_dac is None:
        raise InvalidParameterFile('Required field "ext_dac" does not exist')
    if not isinstance(ext_dac, dict):
        raise InvalidParameterFile('Field "ext_dac" must be a dictionary')

    required_keys = {
        "max_counts": int,
        "max_mv": int,
        "channels": dict,
    }
    missing, _, invalid = _crosscheck_dict(ext_dac, required_keys)
    if missing:
        raise InvalidParameterFile(
            f'Field "ext_dac" is missing required keys: {missing}'
        )
    if invalid:
        raise InvalidParameterFile(
            f'Field "ext_dac" has keys of incorrect types: {invalid}'
        )

    model = config["model"]
    num_channels = config["params"]["channels"]
    required_channels = dict.fromkeys(range(num_channels), int)
    required_channels = _EXT_DAC_CHANNEL_EXCEPTIONS.get(model, required_channels)
    missing, extra, invalid = _crosscheck_dict(ext_dac["channels"], required_channels)

    if missing:
        raise InvalidParameterFile(
            f'Field "ext_dac/channels" is missing required channel(s): {missing}'
        )
    if extra:
        raise InvalidParameterFile(
            f'Found extra channel(s) in "ext_dac/channels": {extra}'
        )
    if invalid:
        raise InvalidParameterFile(
            f'Field "ext_dac/channels" has one or more incorrect types: {invalid}'
        )


def _check_for_minimum_params_entries(config: dict):
    """Makes sure the core parameters exist that are necessary for a minimum functioning
    board.

    Args:
        config (dict): the configuration

    Raises:
        InvalidParameterFile: if any required parameters are missing or have the wrong type.
    """
    required_keys = {
        "channels": int,
        "chanmask": int,
        "samples": int,
        "stop_word": (str, bytes),
        "windmask": int,
        "windows": int,
    }

    missing, _, invalid = _crosscheck_dict(config["params"], required_keys)
    if missing:
        raise InvalidParameterFile(
            f'Field "params" is missing required key(s): {missing}'
        )
    if invalid:
        raise InvalidParameterFile(
            f'Field "params" has one or more entries with invalid types: {invalid}'
        )


def _crosscheck_dict(d: dict, reference: dict) -> Tuple[list, list, dict]:
    """Helper function. Compares a reference dictionary with keys and their
    corresponding types to a test dictionary.

    Retrieving keys that are missing or extra with respect to the reference,
    as well as entries that don't have the right types.

    Returns:
        tuple: (missing_keys: list, extra_keys: list, incorrect_types: dict)
    """
    d_keys = set(d.keys())
    ref_keys = set(reference.keys())

    missing_keys = list(ref_keys - d_keys)
    extra_keys = list(d_keys - ref_keys)
    incorrect_types = {
        k: type(d[k])
        for k, v in reference.items()
        if k in d and not isinstance(d[k], v)
    }

    return missing_keys, extra_keys, incorrect_types


def _calculate_channel_shift(chanmask):
    """Calculate the channelshift param based on the bit width of the channel mask.

    The chanmask must mask all bits up until the window_num bits start for this to work.
    Example:
        12-bit channel header
        HHH_WWW_CCCCC_1
        with a chanmask of 2**7-1 (bottom 6 bits), will return 6.
    """
    return np.where(chanmask % (2 ** np.arange(0, 16)) > 0)[0][0] - 1
