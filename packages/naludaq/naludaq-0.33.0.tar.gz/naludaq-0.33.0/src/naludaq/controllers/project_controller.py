""" Project controller
"""
import gzip
import logging
import os
import pickle
from collections import deque

from naludaq.helpers.exceptions import AcquisitionIOError, ProjectIOError
from naludaq.io import load_pickle_acquisition, save_pickle_acquisition
from naludaq.models import Acquisition

LOGGER = logging.getLogger(__name__)


class ProjectController:
    """ProjectController handles projects, acquisitions and events.

    Project Controller acts as an intermediary between the
    GUI and the Project, Acquisition and events models.
    Every function modifying the datastructure of those objects
    is in this controller.

    Example:
        pc = ProjectController(name, working_directory)

        # Add an acquisition to the project.
        pc.add_acquisition()

        # Get the last acquistion to be added
        acq = pc.get_acquisition()

    """

    def __init__(self, name, working_directory):
        self._project = {
            "name": name,
            "acquisitions": deque(),
            "working_directory": working_directory,
        }
        self._active_acquisition = None
        self._selected_acq = None
        self.maxlen = None

    @property
    def project_name(self):
        """Set/Get the project name.

        Project name is not the same as the project filename.
        The name need to be a str.

        Raises:
            TypeError if the name is not a string.
        """
        return self._project["name"]

    @project_name.setter
    def project_name(self, name):
        if not isinstance(name, (str)):
            raise TypeError("Name must be a string")
        self._project["name"] = str(name)

    @property
    def working_directory(self):
        """The projects working directory.

        Need to be a valid directory.
        Raises:
            NotADirectoryError if the directory is not found.
        """
        return self._project["working_directory"]

    @working_directory.setter
    def working_directory(self, work_dir):
        if not isinstance(work_dir, (str, bytes, os.PathLike)):
            raise TypeError("Working directory must be bytes, string or os.PathLike")
        if not os.path.isdir(work_dir):
            raise NotADirectoryError(f"Directory doesn't exist: {work_dir}")
        self._project["working_directory"] = work_dir

    @property
    def acquisition_notes(self):
        """Get or add notes to the selected acquisition.
        This is notes for the user to store with the selected run.
        Default notes are blank but can be whatever the user needs.

            Returns a blank string if active acquistion is not set.

            Text must be in string format or it'll raise a TypeError.
            Please note the text can contain formatting.
        """
        try:
            return self._active_acquisition.notes
        except AttributeError:
            LOGGER.error("Acquisition notes not found")
            return ""

    @acquisition_notes.setter
    def acquisition_notes(self, text):
        if not isinstance(self._active_acquisition, type(Acquisition())):
            raise NameError("Active acquisition not found, not set yet?")

        try:
            self._active_acquisition.notes = text
        except TypeError as e_msg:
            LOGGER.error(
                "Setting acquisition notes to: %r failed, error %r", text, e_msg
            )

    def create(self, name, working_dir):
        """Create a new project object.

        Args:
            name (str): project name
            working_dir (str): full path to the project
        """
        self._project = {
            "name": name,
            "acquisition": deque(),
            "working_directory": working_dir,
        }

    @staticmethod
    def change_name(obj, name):
        """Change the name of an Acquisition or an Event.

        Args:
            obj (Event or Acquisition): object to change name on.
            name (str): Name as a string.
        """
        if isinstance(obj, type(Acquisition())):
            obj.name = name
        elif isinstance(obj, dict):
            obj["name"] = name

    def add_acquisition(self, name=None):
        """Add a new aquisition to the project.

        Acquisition is added to the top of the stack.

        Args:
            name (str): Default is "Acquisition n", n is the number of prev. Acquisitions.

        """
        if not name:
            name = f"Acquisition {len(self._project['acquisitions'])}"
        acq = Acquisition(
            name=name,
            acq_num=len(self._project["acquisitions"]),
            maxlen=self.maxlen,
        )
        if self._project.get("acquisitions", None) is None:
            self._project["acquisitions"] = deque()
        self._project["acquisitions"].append(acq)

    def get_acquisition(self, value: int = -1) -> dict:
        """Return the acquisition.

        Returns the last acquisition of no number is specified.

        Args:
            value (str): Acquisition number, default -1 (last)
        Returns:
            Acquisition
        """
        if not isinstance(value, int):
            raise TypeError("Value need to be int")

        if not self._project.get("acquisitions", None):
            LOGGER.debug("Found no acquistition using get, adding acquisition.")
            self.add_acquisition()

        if value > len(self._project["acquisitions"]):
            value = len(self._project["acquisitions"]) - 1

        if value < -len(self._project["acquisitions"]):
            value = -len(self._project["acquisitions"]) + 1

        return self._project["acquisitions"][value]

    def get_active_acquisition(self):
        """Returns the active acquisition.

        Active acquisition is used for plotting, printing and updating of acquisitions.
        For adding new events, use get_acquisition, it returns the last one.
        If no active acquisition has been set, returns the last one.
        """

        if not self._active_acquisition:
            self._active_acquisition = self.get_acquisition()
        return self._active_acquisition

    def set_active_acquisition(self, acquisition=None):
        """Set the active acquisition.

        Doesn't have to be from the acquisitions deque, can be any acquisition object.
        active_acquisition can be used independent of get_acquistion which is used to add events.
        If no acquisition is supplied, the last acquisition is set.
        """
        if not acquisition:
            self._active_acquisition = self.get_acquisition()
        else:
            self._active_acquisition = acquisition

    def amount_acquisitions(self):
        """The amount of aquisitions currently in the project.

        Returns:
            Amount of aquisitions as an integer.
        """
        return len(self._project.get("acquisitions"))

    def save(self, filename):
        """PICKLE THE ENTIRE PROJECT!"""
        if filename is None:
            raise TypeError("Supplied pathname is NoneType.")
        path, _ = os.path.split(filename)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a valid directory: {path}")

        try:
            sfile = gzip.GzipFile(filename, "w", compresslevel=4)
            pickle.dump(self._project, sfile, protocol=pickle.HIGHEST_PROTOCOL)
        except IOError as error_msg:
            raise ProjectIOError("File could not be created. %s", error_msg)
        except pickle.PicklingError as error_msg:
            raise ProjectIOError("Saving acquisition failed: %s", error_msg)

    def load(self, filename):
        """Loads a saved Project.

        Args:
            filename (str): Full path to the file including the name of the file.
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"No file found: {filename}")
        try:
            sfile = gzip.GzipFile(filename, "r")
            project = pickle.load(sfile)
        except IOError as error_msg:
            raise ProjectIOError("File could not be created. %s", error_msg)
        except pickle.UnpicklingError as error_msg:
            raise ProjectIOError("Loading acquisition failed: %s", error_msg)
        else:
            if not isinstance(project, type(dict())):
                raise TypeError("Not a valid project file.")
            self._project = project

    @staticmethod
    def save_acq(acq, filename):
        """Save an Acquisition.
        Takes an Acquistion and a filename.
        Will overwrite existing file without asking.

        Args:
            acq (Acquisition): Acquisition to save
            filename (path): Full filepath and filename to save.
        """
        if not isinstance(acq, type(Acquisition())):
            raise TypeError("Supplied Acquisition is NoneType.")
        if filename is None:
            raise TypeError("Supplied pathname is NoneType.")

        path, _ = os.path.split(filename)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a valid directory: {path}")

        try:
            save_pickle_acquisition(acq, filename)
        except IOError as error_msg:
            raise AcquisitionIOError("File could not be created. %s", error_msg)
        except pickle.PicklingError as error_msg:
            raise AcquisitionIOError("Saving acquisition failed: %s", error_msg)

    def load_acq(self, filename):
        """Load an acquisition to the current project.

        Args:
            filename (path): Valid acquisition file.

        Raises:
            NotADirectoryError if a non-valid path is supplied.
            PicklingError if the pickle failed.
            IOError if the file can't be read.
        """

        path, _ = os.path.split(filename)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a valid directory: {path}")

        try:
            acq = load_pickle_acquisition(filename)
        except IOError as error_msg:
            raise AcquisitionIOError("File could not be loaded. %s", error_msg)
        except pickle.UnpicklingError as error_msg:
            raise AcquisitionIOError("Loading acquisition failed: %s", error_msg)
        else:
            self._project["acquisitions"].append(acq)

    def delete(self, item):
        """Delete acquisition or event from project.

        Args:
            item (tuple): (acq_num, evt_num)
        """
        if item[1] is None:
            self.delete_acq(item)
        else:
            self.delete_evt(item)

    def delete_evt(self, item: tuple):
        """Remove event from Acquisition.

        Args:
            item (tuple): tuple with (Acquisition #, Event #).
        """
        acquisition = self._project["acquisitions"][item[0]]
        event = item[1]

        acquisition.rotate(-event)
        acquisition.popleft()
        acquisition.rotate(event)

    def delete_acq(self, item: tuple):
        """Delete the acquisitions in the project.

        Args:
            item (tuple): tuple with (Event, Acquisition)
        """
        index = item[0]
        self._project["acquisitions"].rotate(-index)
        self._project["acquisitions"].popleft()
        self._project["acquisitions"].rotate(index)

    @staticmethod
    def _find_event_in_acquisition(event, acquisition):
        """Find an event for deletion using the index rather than the built-in.

        deques index and remove function can't find numpy objects properly.
        Give more flexibility by finding using object id rather than the built in.

        Args:
            event: item to find
            acquistion: deque-like object to find item in.

        Returns:
            index int if found or None if not found.
        """
        for index, item in enumerate(acquisition):
            if id(event) == id(item):
                return index

        return None

    def __getitem__(self, value):
        if value is None:
            raise IndexError

        if isinstance(value, int):
            return self._project["acquisitions"][value]

        if len(value) > 2:
            raise IndexError

        if isinstance(value[0], slice) or isinstance(value[1], slice):
            TypeError("Project doesn't support slices yet")

        acq_idx = value[0]
        evt_idx = value[1]

        if evt_idx is None:
            return self._project["acquisitions"][acq_idx]

        return self._project["acquisitions"][acq_idx][evt_idx]

    def __len__(self):
        return len(self._project["acquisitions"])

    def __bool__(self):
        return len(self) != 0

    def __iter__(self):
        yield from self._project["acquisitions"]
