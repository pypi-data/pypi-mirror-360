import datetime
from copy import deepcopy
from pathlib import Path

from naludaq.backend.exceptions import AcquisitionError
from naludaq.backend.managers.base import Manager
from naludaq.backend.models.acquisition import RemoteAcquisition, TemporaryAcquisition


class AcquisitionManager(Manager):
    def __init__(self, board):
        """Utility providing methods for accessing acquisitions on the remote.

        Args:
            context (Context): context used to communicate with the backend.
        """
        super().__init__(board)

    @property
    def current_acquisition(self) -> "RemoteAcquisition | None":
        """Get/set the current output acquisition.

        Set this to `None` to stop data capture on the server side (saves resources).
        """
        name = self.context.client.get_json("/acq/output").get("name", None)
        if name is not None:
            return RemoteAcquisition(self.context, name)
        return None

    @current_acquisition.setter
    def current_acquisition(self, acq: "RemoteAcquisition | None"):
        if acq is not None:
            acq.set_output()
            return
        self.context.client.put("/acq/output")

    def list(self) -> list[RemoteAcquisition]:
        """List all acquisitions in the backend's working directory."""
        acquisitions = self.context.client.get_json("/acq/list")["acquisitions"]
        return [RemoteAcquisition(self.context, name) for name in acquisitions]

    def get(self, name: str) -> RemoteAcquisition:
        """Get an existing acquisition.

        Args:
            name (str): name of the acquisition

        Returns:
            RemoteAcquisition: handle to the acquisition.

        Raises:
            HttpError: if the request failed, or the acquisition does not exist.
        """
        acq = RemoteAcquisition(self.context, name)
        if not acq.exists:
            raise AcquisitionError(f"No such acquisition: {name}")
        return acq

    def create(self, name: str = None, metadata: dict = None) -> RemoteAcquisition:
        """Creates a new acquisition.

        Args:
            name (str): name of the acquisition.
            metadata (dict): metadata to store in the acquisition.
                If not provided, default metadata is built from the board.

        Returns:
            RemoteAcquisition: handle to the acquisition.

        Raises:
            HttpError: if the acquisition already exists or the request failed.
        """
        if name is None:
            name = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
        if metadata is None:
            metadata = self._build_metadata()
        acq = RemoteAcquisition(self.context, name)
        acq.create(metadata)
        return acq

    def create_temporary(
        self, name: str = None, metadata: dict = None
    ) -> TemporaryAcquisition:
        """Create a temporary acquisition.

        The temporary acquisition should be used as a context manager
        to ensure the acquisition is deleted from the backend when it
        is no longer needed.

        Args:
            name (str): an optional name for the acquisition.
            metadata (dict): optional metadata to include.

        Returns:
            TemporaryAcquisition: handle to the temporary acquisition.
        """
        if name is None:
            name = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
        if metadata is None:
            metadata = self._build_metadata()
        return TemporaryAcquisition(self.context, name, metadata)

    def _build_metadata(self) -> dict:
        """Create default metadata from the board"""
        return _normalize_metadata(
            {
                "model": self.board.model,
                "params": deepcopy(self.board.params),
                "registers": deepcopy(self.board.registers),
            }
        )

    def lengths(self) -> dict[RemoteAcquisition, int]:
        """Get the lengths of all acquisitions"""
        return {acq: details["len"] for acq, details in self.show_all(len=True).items()}

    def paths(self) -> dict[RemoteAcquisition, Path]:
        """Get the paths of all acquisitions"""
        return {
            acq: Path(details["path"])
            for acq, details in self.show_all(path=True).items()
        }

    def sizes(self) -> dict[RemoteAcquisition, int]:
        """Get the total sizes in bytes of all acquisitions"""
        return {
            acq: details["total_size"]
            for acq, details in self.show_all(total_size=True).items()
        }

    def show_all(
        self,
        *,
        len: bool = False,
        path: bool = False,
        metadata: bool = False,
        chunk_count: bool = False,
        total_size: bool = False,
    ) -> dict[RemoteAcquisition, dict]:
        """Get select information about all acquisitions.

        Args:
            len (bool): fetch the length of each acquisition.
            path (bool): fetch the path of each acquisition.
            metadata (bool): fetch the metadata of each acquisition.
            chunk_count (bool): fetch the number of chunks in each acquisition.
            total_size (bool): fetch the total size of each acquisition.

        Returns:
            dict[RemoteAcquisition, dict]: a dictionary mapping acquisitions to the request information.
        """
        response = self.context.client.get_json(
            "/acq/show-all",
            params={
                "len": int(len),
                "path": int(path),
                "metadata": int(metadata),
                "chunk_count": int(chunk_count),
                "total_size": int(total_size),
            },
        )
        return {
            RemoteAcquisition(self.context, name): details
            for name, details in response.items()
        }


def _normalize_metadata(d: dict) -> dict:
    """Substitute keys/values that are not JSON-encodable with values that are."""

    def _normalize_key(k: object):
        if isinstance(k, int):
            k = str(k)
        return k

    output = {}
    for k, v in d.items():
        k = _normalize_key(k)
        if isinstance(v, dict):
            v = _normalize_metadata(v)
        elif isinstance(v, datetime.datetime):
            v = v.timestamp()
        elif isinstance(v, bytes):
            v = v.hex()
        elif isinstance(v, Path):
            v = str(v)
        output[k] = v
    return output
