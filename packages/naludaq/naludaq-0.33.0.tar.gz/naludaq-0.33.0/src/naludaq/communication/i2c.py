"""i2c controller, talks to the i2c modules o the board.

The i2c communication is both board and chip independent.
"""
from logging import getLogger

from naludaq.communication.i2c_registers import I2CRegisters

LOGGER = getLogger(__name__)
__all__ = [
    "scanI2cDevices",
    "sendI2cCommand",
    "readI2cResponse",
    "readI2cReg",
]


def scanI2cDevices(board) -> list:
    """Checks active devices on the i2c buss.

    Sends out a call to all addresses over the i2c buss and returns
    devices that return an ACK.

    Returns:
        list of devices which returns an ACK.
    """
    response = list()
    for i in range(0, 256, 2):
        addr = hex(i).lstrip("0x").zfill(2)
        words = list()
        if sendI2cCommand(board, addr, words):
            if readI2cResponse(board)[0][-1] == "0":
                response.append(hex(i))

    return response


def sendI2cCommand(board, addr, words, check_ack=False) -> bool:
    """Send commands to the FPGA to rout to i2c devices.

    An abstraction to send an i2c command to GenericWrite.vhd so you don't have to do the dumb
    parsing part input 'words' should be an ordered list of commands in either hex or binary
    address assumes 7 bits in either hex or binary
    and this is always a write.
    be really careful editiing this, because the ordering is both very very important and
    super weird.

    Args:
        addr(str, int): Address of the i2c device, either 7 bits or hex.
        words(list): Words to send. (8-bits)
        board: targeted board.
        check_ack: reads back the response to see if there was an ack

    Returns:
        True if command is sent, False otherwise
    """

    if not isinstance(addr, (str, int)):
        raise TypeError("addr should be a string or int")
    if not isinstance(words, list):
        raise TypeError("words should be a list")

    # LOGGER.debug("sending %s to i2c addr:%s", words, addr)
    if len(words) > 8:
        LOGGER.info("max number of sequential words is 8")
        return False

    try:
        if not isinstance(addr, int):
            addr = _create_i2c_address(addr)
    except Exception as error_msg:
        LOGGER.debug("Couldn't create i2c addr due to: %s", error_msg)
        return False

    # Update the Registers on the board
    try:
        _update_i2c_registers(board, addr, words)
    except Exception as error_msg:
        LOGGER.debug("Couldn't create i2c command due to: %s", error_msg)
        return False

    try:
        I2CRegisters(board).transmit_command()
    except Exception as error_msg:
        LOGGER.debug("Couldn't send i2c command due to: %s", error_msg)
        return False

    if check_ack:
        return all(_check_ack(board, addr, words))

    return True


def _check_ack(board, addr, words):
    """
    Reads back the bitstream from the device and determines if there was an n/ack

    Returns a bool array.  False for NACK, True for ACK

    if addr is *odd*, then it is a write, and only the addr is checked
    """
    response = readI2cResponse(board)
    result = list()
    num_words = len(words) * (addr % 2) + 1
    for iword in range(num_words):
        if response[iword][-1] == "1":
            result.append(False)
            LOGGER.debug("Found a NACK")
        else:
            result.append(True)

    return result


def _create_i2c_address(addr) -> int:
    """Takes a either a 7bit or a hex address and convert into a word address.

    Args:
        addr(str): either a 7bit or a hex address

    """
    if len(addr) == 2:
        addr = int(addr, 16)
    elif len(addr) == 7:
        addr = int(addr, 2)
    else:
        raise ValueError(f"I2c address: {addr} not understood")
    return addr


def _update_i2c_registers(board, addr, words) -> str:
    """Update the I2C registers using the given command parameters.

    Args:
        addr(int): Address of the i2c device in hex.
        words(str): Words to send to the device.
    """

    if len(words) > 8:
        raise ValueError("Too many words, maximum 8 words, provided %s", len(words))

    if addr is None:
        raise TypeError("The provided address type is None.")

    allbits = ""
    for word in words[::-1]:
        if len(word) == 2:
            word = "{0:b}".format(int(word, 16)).zfill(8)
        elif len(word) != 8:
            raise ValueError("i2c word {word} not understood")

        allbits += word

    registers = {
        "i2c_words": len(words),
        "i2c_addr": addr,
    }

    allbits = allbits.ljust(64, "0")
    for reg in range(0, 4):
        name = "i2c_data" + str(3 - reg)
        pair = allbits[reg * 16 : (reg + 1) * 16]
        value = int(pair[8:] + pair[:8], 2)
        registers[name] = value
    I2CRegisters(board).write_many(registers)


def readI2cResponse(board):
    """Read the i2c responses from the registers on the FPGA.

    The i2c module now writes out the SDA value on each high SCL cycle to some registers
    You should be able to parse N/ACKs out of this, as well as responses from devices!
    registers are NGPR+8 through NGPR+11

    Returns:
        List with the responses.
    """
    reg_names = [f"response{i}" for i in range(4)]
    response_regs = I2CRegisters(board).read_many(reg_names)
    phrase = "".join(f"{r:016b}" for r in response_regs)

    phrase = phrase[::-1]
    phrases = []
    if phrase:
        for i in range(0, 7):
            phrases.append(phrase[i * 9 : (i + 1) * 9])

    return phrases


def readI2cReg(board, wraddr, reg):
    """Reads a register from an i2c device

    Basically just sends the address and the reg location, then does the same but with a read

    """

    rdaddr = "{0:02x}".format(int(wraddr, 16) + 1)

    sendI2cCommand(board, wraddr, [reg])
    sendI2cCommand(board, rdaddr, ["FF"])
    response = readI2cResponse(board)
    LOGGER.debug("I2c: %s", response)
    response_int = int(response[1], 2) >> 1

    LOGGER.debug(
        "Register:%s, %s %s %s (ACK,nACK)=%s",
        reg,
        response[1],
        response_int,
        hex(response_int),
        response[1][-1],
    )

    return response_int
