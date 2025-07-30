import ipaddress

from naludaq.backend.managers.base import Manager


class ConfigManager(Manager):
    def __init__(self, board):
        """Utility for higher-level configuration of the backend.

        Args:
            context (Context): context used to communicate with the backend.
        """
        super().__init__(board)

    @property
    def is_embedded_server(self) -> bool:
        """Check if the server is running in the same process via the Python bindings."""
        return getattr(self.board, "server", None) is not None

    @property
    def is_server_local(self) -> bool:
        """Check if the server is running on the same machine as the current process.
        This is done by checking if the server is connected to over the loopback interface.
        """
        local = self.is_embedded_server
        if not local:
            try:
                local = ipaddress.ip_address(self.context.client.host).is_loopback
            except (TypeError, ValueError):
                # don't do anything, this is the wrong place to raise an error
                pass
        return local

    def configure_packaging(self, events: "bytes | str", answers: "bytes | str"):
        """Sets the stop words used by the backend to separate
        events and answers.

        Args:
            events ("bytes | str"): stop word for events.
            answers ("bytes | str"): stop word for answers (register reads).
        """
        if isinstance(events, bytes):
            events = events.hex()
        if isinstance(answers, bytes):
            answers = answers.hex()
        try:
            self.context.client.put(
                "/server/data-format",
                params={
                    "model": self.board.model,
                    "events": events,
                    "answers": answers,
                },
            )
        except ValueError as e:
            raise ValueError("Stop words are invalid") from e
