from naludaq.backend.client import HttpClient
from naludaq.backend.exceptions import BackendError

DEFAULT_LOCAL_CONTEXT_ADDRESS = ("127.0.0.1", 7878)


class Context:
    def __init__(self, addr: tuple[str, int] = None):
        """Utility for communicating with the Rust backend.

        Args:
            addr (tuple[str, int]): address of the backend. Defaults to
                the default address for a local backend.

        Raises:
            HttpError: if the backend is unreachable.
        """
        if addr is None:
            addr = DEFAULT_LOCAL_CONTEXT_ADDRESS
        self._client = HttpClient(addr)
        if not self._client.reachable():
            raise BackendError(f"The server at {addr} is unreachable")

    def __eq__(self, other) -> bool:
        """Check if this context is equal to another.

        Only checks the address of the two contexts.
        """
        return isinstance(other, Context) and self.address == other.address

    @property
    def address(self) -> tuple[str, int]:
        """The host which the backend is running on"""
        return self._client.address

    @property
    def client(self) -> HttpClient:
        """The client used to communicate with the backend."""
        return self._client

    @property
    def is_alive(self) -> bool:
        """Tries to ping the server to check if it's reachable."""
        return self._client.reachable()
