from os.path import exists

import h5py


class LookupTable:
    """
    Class for accessing/storing lookup table data
    Lookup table can be accessed straight from the class
    File is opened on initialization

    Example:
        with LookupTable('filename', 'r+') as lookup_table:
            lookup_table[0,0,:] = 23
            data = lookup_table[0,0,0]
            lookup_table[(2,0,0)] = 6
            captured_data = np.array(lookup_table.captured_data)
            times_captured = np.array(lookup_table.times_captured)
    """

    def __init__(self, file_name: str, file_mode: str):
        """Sets up class to access lookup table from file

        Args:
            file_name (str): Name of lookup table file
            file_mode (str): 'r' Read only, 'r+' Read/write
        """
        if not exists(file_name):
            raise FileNotFoundError("Lookup table file does not exist")
        self.file_name = file_name
        self.file_mode = file_mode
        self.open()

    @property
    def lookup(self):
        """Dataset containing values used for processing data.
        This is the table modified & filled when interpolating
        data from the lookup table generator.
        """
        self._opened_or_raise()
        if not hasattr(self, "_lookup") or not self._lookup.id:
            self._lookup = self._h5_file["lookup_table"]
        return self._lookup

    @lookup.setter
    def lookup(self, lookup):
        self._lookup = lookup

    @property
    def captured_data(self):
        """Dataset containing raw data captured from a dac sweep.
        Modified when adding data to the file using the lookup table
        generator functions.
        """
        self._opened_or_raise()
        if not hasattr(self, "_captured_data") or not self._captured_data.id:
            self._captured_data = self._h5_file["captured_data"]
        return self._captured_data

    @captured_data.setter
    def captured_data(self, captured_data):
        self._captured_data = captured_data

    @property
    def times_captured(self):
        """Number of times a certain entry in the lookup table is
        captured. Mainly used to determine the average value of
        entries captured more than once.
        """
        self._opened_or_raise()
        if not hasattr(self, "_times_captured") or not self._times_captured.id:
            self._times_captured = self._h5_file["times_captured"]
        return self._times_captured

    @times_captured.setter
    def times_captured(self, times_captured):
        self._times_captured = times_captured

    @property
    def settings(self):
        self._opened_or_raise()
        if not hasattr(self, "_settings") or not self._settings.id:
            self._settings = _settings_to_dict(self._h5_file["settings"])
        return self._settings

    def open(self):
        if not self.is_open:
            self._h5_file = h5py.File(self.file_name, self.file_mode)

    def close(self):
        self._h5_file.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def __getitem__(self, key):
        self._opened_or_raise()
        return self.lookup[key]

    def __setitem__(self, key, value):
        self._opened_or_raise()
        self.lookup[key] = value

    @property
    def is_open(self) -> bool:
        """Checks if h5 file is opened"""
        return bool(getattr(self, "_h5_file", False))

    def _opened_or_raise(self):
        """Checks if h5 file is opened, if not raise IOError"""
        if not self.is_open:
            raise IOError("Lookup table file is not open")


def _settings_to_dict(value):
    """Converts h5.Group settings to dict"""
    settings = dict()
    if isinstance(value, h5py.Group):
        for key in value.keys():
            settings[key] = _settings_to_dict(value[key])
    for key in value.attrs.keys():
        settings[key] = value.attrs[key]
    return settings
