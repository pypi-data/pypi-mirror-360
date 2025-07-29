# ----------------------------------------------------------------------------------------
# Python-Backpack - Folder Utilities
# Maximiliano Rocamora / maxirocamora@gmail.com
# https://github.com/MaxRocamora/python-backpack
# ----------------------------------------------------------------------------------------

import os
import shutil
import subprocess

from backpack.logger import get_logger

log = get_logger('Python Backpack - FolderUtils')


def browse_folder(folder: str) -> bool:
    """Open windows explorer on folder.

    Args:
        folder: (string path) folder to open
    """
    if folder and os.path.isdir(folder):
        subprocess.Popen(f'explorer {os.path.abspath(folder)}')
        return True

    log.warning(f'Unable to open folder {folder}')
    return False


def create_folders(folders: list, force_empty: bool = False, verbose: bool = False):
    """Creates multiple folders on disc.

    Args:
        folders (list): folder list
        force_empty (bool, optional): forces clearing folder content. Defaults to False.
        verbose (bool, optional):shows log. Defaults to False.
    """
    for folder in folders:
        create_folder(folder, force_empty=force_empty, verbose=verbose)


def create_folder(path: str, force_empty: bool = False, verbose: bool = True):
    """Creates a folder.

    Args:
        path (str): folder path
        force_empty (bool, optional): forces clearing folder content. Defaults to False.
        verbose (bool, optional): show log. Defaults to True.
    """
    abspath = os.path.abspath(path)
    if verbose:
        log.info(f'Creating Folder {abspath}')

    try:
        if not os.path.exists(abspath):
            os.makedirs(f'{abspath}/')
        elif force_empty:
            remove_files_in_dir(abspath)
    except OSError as e:
        log.warning(f'Unable to create folder: {path}')
        log.error(str(e))

    return True


def remove_files_in_dir(path: str):
    """Clears all content in given directory."""
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def recursive_dir_copy(source_path: str, target_path: str):
    """Copy all files src dir to dest dir, including sub-directories.

    Args:
        source_path (str): source path
        target_path (str): destination path
    """

    create_folder(source_path)
    create_folder(target_path)

    for item in os.listdir(source_path):
        file_path = os.path.join(source_path, item)

        # if item is a file, copy it
        if os.path.isfile(file_path):
            shutil.copy(file_path, target_path)
        # else if item is a folder, recurse
        elif os.path.isdir(file_path):
            new_dest = os.path.join(target_path, item)
            recursive_dir_copy(file_path, new_dest)
