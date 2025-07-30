def substitute_value(addr_value: int, register_value: int, register: dict):
    """Substitute the register value into the address value.

    Args:
        addr_value(int): The value of the address.
        register_value(int): The value of the register.
        register(dict): The register dict.

    Returns:
        The new value of the address.
    """
    bw = register["bitwidth"]
    bp = register["bitposition"]
    mask = (2**bw - 1) << bp
    return addr_value - (addr_value & mask) + ((register_value & (2**bw - 1)) << bp)


def normalize_address(addr: "int | str", width_addr: int) -> str:
    if not isinstance(addr, (int, str)):
        raise TypeError("Address must be a string or integer")
    if isinstance(addr, int):
        addr = f"{addr:X}"
    return addr.upper().zfill(width_addr)


def normalize_name(name: str) -> str:
    return name.casefold()


def full_to_partial_value(full_value: int, register: dict) -> int:
    """Strip out the value for a single register from a full 12-bit value."""
    position = register["bitposition"]
    width = register["bitwidth"]
    return (full_value >> position) & ((1 << width) - 1)


def partial_to_full_value(register: dict, value: int) -> int:
    """Convert the value for a single register into a 12-bit value, with the
    original value in the correct position.
    """
    position = register["bitposition"]
    width = register["bitwidth"]
    return (value & (1 << width) - 1) << position
