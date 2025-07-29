import json
import os

from backpack.logger import get_logger

log = get_logger('Python Backpack - JsonUtils')


def json_load(json_file: str) -> dict:
    """Reads a json file.

    Args:
        json_file: (string filepath) json file to read data.

    Returns:
        dict (file content)
    """
    if not os.path.exists(json_file):
        raise OSError(f'json_load: File not found: {json_file}.')

    with open(json_file) as json_file_opened:
        try:
            value = json.load(json_file_opened)
        except ValueError as e:
            json_file_opened.close()
            raise OSError(f'{json_file} \n JSON File issue: {str(e)}') from e

    return value


def json_save(data: dict, json_file: str) -> bool:
    """Saves a dictionary into a json file.

    Args:
        data: (dict) dictionary to save
        json_file: (string filepath) json file to save data.

    Returns:
        bool (True if success)
    """

    if not os.path.exists(os.path.dirname(json_file)):
        os.makedirs(os.path.dirname(json_file))

    try:
        with open(json_file, 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4)
            return True

    except (OSError, TypeError) as e:
        log.error(f'{e} - {json_file}')

    return False
