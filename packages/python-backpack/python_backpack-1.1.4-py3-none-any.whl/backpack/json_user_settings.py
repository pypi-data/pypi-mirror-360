# ----------------------------------------------------------------------------------------
# Json Settings Class
# This class handle load/save json files on win/linux local user folder

"""Usage.

us = JsonUserSettings('my_app')
us.save(someDict)
data = us.load()

"""
# ----------------------------------------------------------------------------------------
import os

from backpack.json_utils import json_load, json_save
from backpack.logger import get_logger

log = get_logger('Python Backpack - UserSettings')


class JsonUserSettings:
    def __init__(self, folder: str, name: str) -> None:
        """Manages saving/loading json file on local user folder.

        Args:
            folder (str): name of sub folder inside user path. Defaults to 'json_settings'.
            name (str): name used for the json file. Defaults to 'user_data'.
        """
        self.name = name
        self.folder = folder
        self._user_data = {}
        self._verify_path()

    @property
    def filepath(self) -> str:
        """Returns user filepath."""
        path = os.path.join(self.os_user_folder, self.folder, f'{self.name}.json')
        return os.path.abspath(path)

    @property
    def os_user_folder(self) -> str:
        """Returns os users home directory."""
        return os.path.expanduser('~')

    @property
    def user_data(self) -> dict:
        """Override this property to modify saving dict."""
        return self._user_data

    @user_data.setter
    def user_data(self, v: dict) -> None:
        self._user_data = v

    def _verify_path(self) -> bool:
        """Checks for target directory or make it."""
        path = os.path.dirname(self.filepath)
        if not os.path.exists(path):
            os.makedirs(path)

        return True

    def save_settings(self, data=False) -> bool:
        """Saves a dictionary into a json file (os user path).

        Args:
            data (dictionary) : info dictionary to save, if set to False,
                saves instead local self.user_data property
        """
        if not data:
            data = self.user_data

        r = json_save(data, self.filepath)
        if r:
            log.info('json settings file saved! [%s]', self.filepath)
        return r

    def load_settings(self) -> dict:
        """Load json file from path and returns its contents."""
        try:
            return json_load(self.filepath)
        except OSError:
            return False
