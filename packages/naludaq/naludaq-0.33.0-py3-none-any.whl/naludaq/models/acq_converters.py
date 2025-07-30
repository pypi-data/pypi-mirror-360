"""Module to convert between acquisition metadata structures of different versions.

This module can be used to upgrade and downgrade metadata formats between
many different versions.

Uses a stack-based approach to "push" and "pop" changes in acq dicts that
appear across versions. Locations of entries in dictionaries are represented
using path strings similar to file system paths.

Supported version strings:
- '0.1': the original Acquisition format. Since this is not a pure dictionary,
    the users of this module will need to handle moving everything into or
    out of a dictionary
- '0.2': placed all metadata into a single dict
- '0.3': remove duplicate model entry

Operations:
- ('move', source_path, dest_path): moves an entry from one location to another
- ('copy', source_path, dest_path): copies an entry from one location to another
- ('set', path, value): stores 'value' in a path
- ('del', path): removes the entry at a path
- ('modify', path, callable): applies a function to an entry, then replaces
    the old entry with the return value of the function.
"""
import ast
import copy
import logging
from collections import deque

from naludaq.helpers.helper_functions import get_package_versions

_LOGGER = logging.getLogger(__name__)


def upgrade_old_acquisition(acq):
    """Upgrades an old acquisition to the latest version

    Args:
        acq (v0.1 Acquisition, dict): acquisition data dict, or
            v0.1 acquisition loaded from a pickle.

    Returns:
        The upgraded acquisition.
    """
    from naludaq.models import Acquisition

    old_version = EARLIEST_VERSION
    if isinstance(acq, dict):
        old_version = acq["metadata"]["file_version"]

    _LOGGER.debug(f"Converting acquisition from {old_version} to {LATEST_VERSION}")

    if type(acq) == deque:
        new_acq = Acquisition()
        new_acq.events.extend(acq)
        return new_acq

    elif old_version == EARLIEST_VERSION:
        naludaq_version, naluscope_version = get_package_versions()

        # Version 0.1 did not use a single dict, need to grab info from a few places
        # and create a fake acq dict for the converter to use
        data = {
            "file_version": EARLIEST_VERSION,
            "naludaq_version": naludaq_version,
            "naluscope_version": naluscope_version,
            "model": acq.info.get("board_info", {}).get("model", None),
            "acq_num": acq._acq_num,
            "created_at": getattr(acq, "created_at"),
            "name": acq._name,
            "notes": getattr(acq, "notes"),
            "numevt": len(acq),
            "info": acq.info,
            "trigger_settings": getattr(acq, "trigger_settings", None),
        }
        data = convert(data, old_version, LATEST_VERSION)
        new_acq = Acquisition()
        new_acq.as_dict().update({"metadata": data})
        new_acq.events.extend(acq)
        new_acq.pedestals = getattr(acq, "_pedestals", None)
        new_acq.caldata = getattr(acq, "_caldata", None)
        new_acq.timingcal = getattr(acq, "_timingcal", None)
        return new_acq

    # > v0.1
    data = convert(acq, old_version, LATEST_VERSION)
    return Acquisition(data=data)


def convert(acq: dict, from_version: str, to_version: str, in_place=False):
    """Converts an acquisition structure from one version to another.

    Args:
        acq (dict): the acquisition dict to work on
        from_version (str): the starting version number
        to_version (str): the ending version number
        in_place (bool): whether to apply the changes directly to the
            dict, or a copy of it.

    Returns:
        A dict in the 'to_version' format.
    """
    _LOGGER.debug(f"Converting metadata from {from_version} to {to_version}")
    try:
        changes = _get_changes_list(from_version, to_version)
    except ValueError as e:
        _LOGGER.error(f"Could not convert metadata: {e}")
        raise

    if not in_place:
        acq = copy.deepcopy(acq)
    _apply_changes(acq, changes)

    return acq


def _get_entry(d: dict, path: str):
    """Finds an entry in a dictionary. Creates dictionaries
    if they do not appear along the path.

    Entries are located using path representation. For example, to reference
    the 'inner' key in  `{'outer': {'inner': 5}}`, the path would be
    '/outer/inner.' Do not use trailing slashes.

    Args:
        d (dict): the dictionary to search in
        path (str): the path string

    Returns:
        A tuple of
            (
                parent dictionary of entry,
                entry name,
                entry value (or None if not present),
            )
    """
    split = path.split("/")
    for name in split[:-1]:
        if not name:
            continue
        child = d.get(name, None)
        if child is None:
            d[name] = {}
        d = d[name]

    return d, split[-1], d.get(split[-1], None)


def _apply_changes(acq: dict, changes: list):
    """Applies all the changes in a list to an acquisition dict.
    All changes are performed in-place on the dict.

    Args:
        acq (dict): the dict to apply changes to
        changes (list): the list of changes
    """
    _LOGGER.debug(f"Applying {len(changes)} changes in conversion")
    for change in changes:
        if not isinstance(change, tuple):  # skip version tags
            continue

        op = change[0]
        args = change[1:]

        if op == "move":
            src_parent, src_name, src_value = _get_entry(acq, args[0])
            if src_value is not None:
                dst_parent, dst_name, _ = _get_entry(acq, args[1])
                dst_parent[dst_name] = src_value
                del src_parent[src_name]

        elif op == "copy":
            src_parent, src_name, src_value = _get_entry(acq, args[0])
            if src_value is not None:
                dst_parent, dst_name, _ = _get_entry(acq, args[1])
                dst_parent[dst_name] = copy.deepcopy(src_value)

        elif op == "del":
            parent, name, _ = _get_entry(acq, args[0])
            if name in parent:
                del parent[name]

        elif op == "set":
            parent, name, _ = _get_entry(acq, args[0])
            parent[name] = args[1]

        elif op == "modify":
            parent, name, value = _get_entry(acq, args[0])
            if value is not None:
                # Avoid sharing the same dicts between acquisitions
                if type(value) == dict:
                    value = copy.deepcopy(value)
                parent[name] = args[1](value)


def _get_changes_list(from_version: str, to_version: str):
    """Fetches a list of changes to convert from one version
    to another

    Args:
        from_version (str): the starting version number
        to_version (str): the ending version number

    Raises:
        ValueError if one of the versions is unsupported

    Returns:
        A list of changes to apply
    """
    try:
        from_version_index = _VERSION_TAGS.index(from_version)
        to_version_index = _VERSION_TAGS.index(to_version)
        if to_version_index >= from_version_index:
            changes = _UPGRADE_CHANGES
        else:
            changes = _DOWNGRADE_CHANGES

        start_index = changes.index(from_version)
        end_index = changes.index(to_version)

        return changes[start_index:end_index]
    except ValueError as e:
        _LOGGER.error(f"Got an invalid revision: {e}")
        raise ValueError(f"Unsupported version number in conversion: {e}")


# List of version tags in chronological order, used to distinguish upgrades/downgrades
_VERSION_TAGS = [
    "0.1",
    "0.2",
    "0.3",
]
LATEST_VERSION = _VERSION_TAGS[-1]
EARLIEST_VERSION = _VERSION_TAGS[0]


_UPGRADE_CHANGES = [  # Version tags appear after the operations needed to upgrade to that version
    "0.1",  # ==========================================================================
    ("move", "/info/board_info/model", "/settings/model"),
    ("move", "/info/board_info", "/info/readings"),
    ("move", "/info/readings/connection", "/info/connection"),
    ("move", "/info/parameters", "/settings/params"),
    ("move", "/info/analog_values", "/settings/registers/analog_registers"),
    ("move", "/info/control_registers", "/settings/registers/control_registers"),
    ("move", "/info/digital_registers", "/settings/registers/digital_registers"),
    ("move", "/trigger_settings/date", "/info/trigger_settings/date"),
    ("move", "/trigger_settings/levels", "/info/trigger_settings/levels"),
    ("move", "/trigger_settings/offset", "/info/trigger_settings/offset"),
    ("del", "/trigger_settings"),
    ("set", "file_version", "0.2"),
    "0.2",  # ==========================================================================
    ("del", "/model"),
    ("set", "file_version", "0.3"),
    "0.3",  # ==========================================================================
]
_DOWNGRADE_CHANGES = [  # Version tags appear after the operations needed to downgrade to that version
    "0.3",  # ==========================================================================
    ("copy", "/settings/model", "/model"),
    "0.2",  # ==========================================================================
    ("move", "/info/readings", "/info/board_info"),
    ("move", "/info/connection", "/info/board_info/connection"),
    ("move", "/settings/model", "/info/board_info/model"),
    ("move", "/settings/params", "/info/parameters"),
    ("move", "/settings/registers/analog_registers", "/info/analog_values"),
    ("move", "/settings/registers/control_registers", "/info/control_registers"),
    ("move", "/settings/registers/digital_registers", "/info/digital_registers"),
    ("del", "/settings"),
    ("copy", "/info/readout_settings/acq", "/trigger_settings/acq"),
    ("copy", "/info/readout_settings/readout_channels", "/trigger_settings/channels"),
    ("modify", "/trigger_settings/channels", (lambda x: ast.literal_eval(x))),
    ("move", "/info/trigger_settings/date", "/trigger_settings/date"),
    ("copy", "/info/readout_settings/lb", "/trigger_settings/lb"),
    ("copy", "/info/readout_settings/limit", "/trigger_settings/limit"),
    ("copy", "/info/readout_settings/ped", "/trigger_settings/ped"),
    ("copy", "/info/readout_settings/readoutEn", "/trigger_settings/readoutEn"),
    (
        "copy",
        "/info/readout_settings/readoutlookback",
        "/trigger_settings/readoutlookback",
    ),
    (
        "copy",
        "/info/readout_settings/readoutwindows",
        "/trigger_settings/readoutwindows",
    ),
    ("copy", "/info/readout_settings/singleEv", "/trigger_settings/singleEv"),
    ("copy", "/info/readout_settings/trig", "/trigger_settings/trig"),
    (
        "copy",
        "/info/readout_settings/writeaftertrig",
        "/trigger_settings/writeaftertrig",
    ),
    ("set", "file_version", "0.1"),
    "0.1",  # ==========================================================================
]
