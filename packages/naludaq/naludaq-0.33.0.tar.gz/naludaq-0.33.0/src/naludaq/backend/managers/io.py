import time
from typing import Optional

from naludaq.backend.managers.base import Manager

_WRITE_MESSAGE_NIBBLES = 8
_WRITE_MESSAGE_NIBBLES_BYTES = _WRITE_MESSAGE_NIBBLES // 2


class BoardIoManager(Manager):
    def __init__(self, board):
        """Utility for I/O with a board connected to the backend.

        Args:
            context (Context): context used to communicate with the backend.
        """
        super().__init__(board)
        self.bundle_mode = self.board.params.get("usb", {}).get("bundle_mode", False)
        self.tx_pause = self.board.params.get("usb", {}).get("tx_pause", 0.0)

    def write(
        self,
        command: "str | bytes | list[str | bytes]",
        bundle: bool = False,
        pause: Optional[float] = None,
    ):
        """Writes a non-read command to the board.

        Args:
            command (str | bytes): command to send.
        """
        if pause is None:
            pause = self.tx_pause
        if bundle is None:
            bundle = self.bundle_mode
        if isinstance(command, list):
            commands = command
        elif isinstance(command, str):
            if (len(command) > _WRITE_MESSAGE_NIBBLES) and bundle is False:
                commands = [
                    command[i : i + _WRITE_MESSAGE_NIBBLES]
                    for i in range(0, len(command), _WRITE_MESSAGE_NIBBLES)
                ]
            else:
                commands = [command]
        elif isinstance(command, bytes):
            if (len(command) > _WRITE_MESSAGE_NIBBLES_BYTES) and bundle is False:
                commands = [
                    command[i : i + _WRITE_MESSAGE_NIBBLES_BYTES].hex()
                    for i in range(0, len(command), _WRITE_MESSAGE_NIBBLES_BYTES)
                ]
            else:
                commands = [command.hex()]
        self.write_all(commands, pause)

    def write_all(self, commands: list["str | bytes"], pause: Optional[float] = None):
        """Writes a list of non-read commands to the board.

        Args:
            commands (list[str | bytes]): the commands to send.
        """
        if pause is None:
            pause = self.tx_pause
        if len(commands) == 0:
            raise ValueError("Need at least one command")
        commands = [c.hex() if isinstance(c, bytes) else c for c in commands]
        self._send(commands, pause)

    def _send(self, commands: list["str | bytes"], pause: Optional[float] = None):
        if pause is None:
            pause = self.tx_pause
        self.context.client.put(
            "/board/raw",
            json={"packages": commands},
        )
        time.sleep(pause)

    def read(self, command: "str | bytes") -> bytes:
        """Sends a read command to the board and gets the response.

        Args:
            command (str | bytes): read command to send.

        Returns:
            bytes: the response.
        """
        response = self.read_all([command])[0]
        return response

    def read_all(self, commands: "list[str | bytes]") -> list[bytes]:
        """Sends several read commands to the board and retrieves the responses.

        Args:
            commands (list[str | bytes]): commands to send

        Returns:
            list[bytes]: The responses from the board
        """
        if len(commands) == 0:
            raise ValueError("Need at least one command")
        commands = [c.hex() if isinstance(c, bytes) else c for c in commands]
        response = self.context.client.get_json(
            "/board/raw",
            json={"packages": commands},
        )

        return [bytes.fromhex(a) for a in response["packages"]]
