"""This module contains controls for selecting which chips are being written/read.
"""
import contextlib

from naludaq.helpers import validations

from .control_registers import ControlRegisters


@contextlib.contextmanager
def select_chips(board, chips: list[int], restore: bool = True):
    """Context manager for selecting which chips are being written/read.

    On context exit, the chips are restored to the previous selection.

    Args:
        board (Board): the board
        chips (list[int]): list of chips to enable for the duration of the context
        restore (bool): whether to restore the previous selection on context exit.
            Can disable this if you are performing many chip-specific operations
            in a row.

    Example:
    ```py
    with select_chips(board, [0, 1]):
        board.connection.send("write something to chips 0 and 1")
    ```
    """
    validations.validate_chip_list_or_raise(chips, board.params)
    select, deselect = select_chips_commands(board, chips)
    _send_command(board, select)
    try:
        yield
    finally:
        if restore:
            _send_command(board, deselect)


def select_chips_commands(board, chips: list[int]) -> tuple[str, str]:
    """Generate a pair of commands to select/restore chips.

    Args:
        board (Board): the board
        chips (list[int]): list of chips to enable

    Returns:
        tuple[str, str]: select, restore commands
    """
    restore = True
    if board.model in ['trbhm', 'dsa-c10-8']:
        restore = False
    prev_chips = selected_chips(board)
    select_cmd = _select_chips_command_factory(board, chips)
    restore_cmd = _select_chips_command_factory(board, prev_chips, restore=restore)
    return select_cmd, restore_cmd


def selected_chips(board) -> list[int]:
    """Get the chips which are currently selected.

    Args:
        board: the board

    Returns:
        list[int]: list of selected chips
    """
    fn = {
        "hiper": _selected_chips_hiper,
        "aodsoc_asoc": _selected_chips_aodsoc,
        "aodsoc_aods": _selected_chips_aodsoc,
        "trbhm": _selected_chips_trbhm,
        "dsa-c10-8": _selected_chips_trbhm,
        "upac96": _selected_chips_upac96,
    }.get(board.model, None)
    result = []
    if fn is not None:
        result = fn(board)
    return result


def wrap_command(
    board, command: str, chips: list[int], restore: bool = True, wait: bool = True
) -> str:
    """Wrap a command in chip selection commands.

    Args:
        board (Board): the board
        command (str): the command to wrap
        chips (list[int]): list of chips to enable
        restore (bool): whether to include a restoration command

    Returns:
        str: wrapped command
    """
    select, restore_cmd = select_chips_commands(board, chips)
    wait_cmd = ""
    if wait:
        wait_cmd = board.params.get("wait", "AE000FFF")
    if not restore:
        restore_cmd = ""

    ret_cmd = f"{select}{wait_cmd}{command}{wait_cmd}{restore_cmd}"
    return ret_cmd


def _select_chips_command_factory(board, chips: list[int], restore: bool = True) -> str:
    """Generate a command to select/deselect chips for the appropriate board.

    If the board is not multichip, an empty string will be returned.

    Args:
        board (Board): the board
        chips (list[int]): list of chips to enable

    Returns:
        str: _description_
    """
    fn = {
        "hiper": _select_chips_command_hiper,
        "aodsoc_asoc": _select_chips_command_aodsoc,
        "aodsoc_aods": _select_chips_command_aodsoc,
        "trbhm": _select_chips_command_trbhm,
        "dsa-c10-8": _select_chips_command_trbhm,
        "upac96": _select_chips_command_upac96,
    }.get(board.model, None)

    command = ""
    if fn is not None:
        command = fn(board, chips, restore)
    return command


def _select_chips_command_hiper(board, chips: list[int], restore: bool = True) -> str:
    """Chip select command generator for aodsoc boards"""
    mask = _build_chip_mask_or_raise(board.params, chips)
    return _generate_commands(
        board,
        {
            "rxout_en": mask,
        },
    )


def _select_chips_command_aodsoc(board, chips: list[int], restore: bool = True) -> str:
    """Chip select command generator for aodsoc boards"""
    mask = _build_chip_mask_or_raise(board.params, chips)
    return _generate_commands(
        board,
        {
            "ard_tx_en": mask,
            "ard_rx_en": mask,
        },
    )


def _select_chips_command_trbhm(board, chips: list[int], restore: bool = True) -> str:
    """Chip select command generator for TRBHM"""
    mask = _build_chip_mask_or_raise(board.params, chips)
    writes = {
        "ard_tx_en": mask,
        "ard_rx_en": mask,
    }
    if restore:
        if len(chips) != 0:
            writes["chip_select"] = chips[0]
    return _generate_commands(board, writes)


def _select_chips_command_upac96(board, chips: list[int], restore: bool = True) -> str:
    """Chip select command generator for upac96"""
    mask = _build_chip_mask_or_raise(board.params, chips)
    writes = {"udc_rxout_enable": mask}
    if len(chips) != 0:
        writes["udc_select"] = chips[0]
    return _generate_commands(board, writes)


def _selected_chips_hiper(board) -> list[int]:
    """Get selected chips for an aodsoc board"""
    mask = board.registers["control_registers"]["rxout_en"]["value"]
    numchips = board.params["num_chips"]
    maxval = 2**numchips - 1
    mask = max(0, min(mask, maxval))
    chiplist = _build_chip_list_or_raise(mask)
    return chiplist


def _selected_chips_aodsoc(board) -> list[int]:
    """Get selected chips for an aodsoc board"""
    mask = board.registers["control_registers"]["ard_rx_en"]["value"]
    return _build_chip_list_or_raise(mask)


def _selected_chips_trbhm(board) -> list[int]:
    """Get selected chips for an trbhm board"""
    mask = board.registers["control_registers"]["ard_rx_en"]["value"]
    return _build_chip_list_or_raise(mask)


def _selected_chips_upac96(board) -> list[int]:
    """Get selected chips for a upac96 board"""
    mask = board.registers["control_registers"]["udc_rxout_enable"]["value"]
    return _build_chip_list_or_raise(mask)


def _build_chip_mask_or_raise(params: dict, chips: list[int]) -> int:
    """Build a chip mask from a list of chips. This function is the inverse of
    `_build_chip_list_or_raise`.

    The mask is a bitfield where each bit represents a chip. The least significant bit
    represents chip 0, the next bit chip 1, and so on.

    Args:
        params (dict): board params, used for validation
        chips (list[int]): list of enabled chips

    Returns:
        int: the chip mask

    Raises:
        ValueError: if the list of chips is invalid
    """
    validations.validate_chip_list_or_raise(chips, params)
    return sum(1 << c for c in chips)


def _build_chip_list_or_raise(chip_mask: int) -> list[int]:
    """Parses a chip mask into a list of chips. This function is the inverse of
    `_build_chip_mask_or_raise`.

    The mask is expected to be a bitfield where each bit represents a chip. The least
    significant bit represents chip 0, the next bit chip 1, and so on.

    Args:
        chip_mask (int): the chip mask

    Returns:
        list[int]: list of enabled chips
    """
    return [
        chip for chip in range(chip_mask.bit_length()) if (chip_mask >> chip) & 1 == 1
    ]


def _send_command(board, command: str):
    """Send a command to the board"""
    from naludaq.backend import BoardIoManager

    if board.using_new_backend:
        BoardIoManager(board).write(command)
    else:
        board.connection.send(command)


def _generate_commands(board, writes: dict[str, int]) -> str:
    cr = ControlRegisters(board)
    return "".join(cr.generate_write(name, value) for name, value in writes.items())
