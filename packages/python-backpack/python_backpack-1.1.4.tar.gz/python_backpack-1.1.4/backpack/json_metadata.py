# ----------------------------------------------------------------------------------------
# Python-Backpack - JsonMetadata
# Maximiliano Rocamora / maxirocamora@gmail.com
# https://github.com/MaxRocamora/python-backpack
# ----------------------------------------------------------------------------------------
import inspect
import os
import platform
import sys
import time
from datetime import datetime
from typing import Any

from backpack.json_utils import json_load, json_save
from backpack.version import version


class JsonMetaFile:
    PREFIX = 'MD_'

    def __init__(self, name: str, path: str) -> None:
        """saves/load a class/dict as a json metadata file.

        Args:
            name (str): name of the file/class
            path (str, optional): filepath. Defaults to None.
        """
        self._name = name
        self._path = path
        self._data = {'_about': {'package': 'python-backpack', 'version': self.version}}

    @property
    def name(self) -> str:
        """Name of this metadata class."""
        return self._name

    @property
    def version(self) -> str:
        """Version of this metadata class."""
        return version

    @property
    def filename(self) -> str:
        """Returns default filename with prefix and extension."""
        return self.PREFIX + self.name + '.json'

    @property
    def filepath(self) -> str:
        """Full json metadata filepath."""
        return os.path.join(self.path, self.filename)

    @property
    def path(self) -> str:
        """Base path location of metadata json file."""
        return self._path

    def has_file(self) -> bool:
        """Returns true if file exists."""
        return os.path.exists(self.filepath)

    # ------------------------------------------------------------------------------------
    # LOAD/INSERT/REMOVE/SAVE
    # ------------------------------------------------------------------------------------

    def load(self) -> None:
        """Loads metadata from disk."""
        self._data = json_load(self.filepath) if self.has_file() else {}

    def insert(self, key: str, value: Any) -> None:
        """Inserts value into metadata."""
        self._data[key] = value

    def remove(self, key: str) -> None:
        """Remove key from metadata."""
        if key in self._data.keys():
            del self._data[key]

    def save(self) -> None:
        """Save current metadata into json file."""
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self._data['system'] = self._system_data()
        json_save(self._data, self.filepath)

    # ------------------------------------------------------------------------------------
    # CLASS MODE METHODS
    # ------------------------------------------------------------------------------------

    def load_as_class(self) -> type:
        """Returns the metadata dict as a class obj."""
        metadata_class = type(self.name, (), self._data)
        return metadata_class

    def insert_class(self, _class: type) -> None:
        """Load all attributes from  a  given class into this class metadata."""
        attributes = {}
        for name in dir(_class):
            value = getattr(_class, name)
            if not name.startswith('__') and not inspect.ismethod(value):
                attributes[name] = value

        self._data = attributes

    # ------------------------------------------------------------------------------------
    # SYSTEM METADATA OS/USER/TIME
    # ------------------------------------------------------------------------------------

    def _system_data(self) -> dict:
        """Add system metadata to the default data before save."""
        return {
            'name': self.name,
            'app': os.path.basename(sys.executable),
            'PC': str(platform.node()),
            'python_version': sys.version,
            'User': str(os.getenv('username')),
            'time': self._current_time_metadata(),
        }

    def _current_time_metadata(self) -> dict:
        """Get export time info."""
        ftime = time.strftime('%Y,%b,%d,%j,%H:%M', time.localtime())
        times = ftime.split(',')
        td = {
            'year': times[0],
            'month': times[1],
            'day': times[2],
            'year_day': times[3],
            'time': times[4],
            'save_time': datetime.now().ctime(),
        }
        return td
