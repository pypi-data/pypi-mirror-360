# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231224

import os
import pathlib
import sys
import threading
from typing import Dict, List, Union

from loguru import logger


def get_user_config_directory():
    """Returns a platform-specific root directory for user config settings.
    On Windows, prefer %LOCALAPPDATA%, then %APPDATA%, since we can expect the AppData directories to be ACLed to be visible only to the user and admin users (https://stackoverflow.com/a/7617601/1179226). If neither is set, return None instead of falling back to something that may be world-readable.
    """
    if os.name == "nt":
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            return appdata
        appdata = os.getenv("APPDATA")
        if appdata:
            return appdata
        return None
    # On non-windows, use XDG_CONFIG_HOME if set, else default to ~/.config.
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        return xdg_config_home
    return os.path.join(os.path.expanduser("~"), ".config")


def get_user_app_data_directory():
    """
    Returns a parent directory path
    where persistent application data can be stored.

    - linux: ~/.local/share
    - macOS: ~/Library/Application Support
    - windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        app_data_path = home / "AppData/Roaming"
    elif sys.platform == "linux":
        app_data_path = home / ".local/share"
    elif sys.platform == "darwin":
        app_data_path = home / "Library/Application Support"

    return str(app_data_path)


def get_file_size_in_bytes(file_path):
    return os.path.getsize(file_path)


def get_folder_size_in_bytes(folder_path, skip_symbolic_link=True):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.islink(fp) and skip_symbolic_link:
                continue  # Skip if it is symbolic link
            total_size += os.path.getsize(fp)
    return total_size


def format_bytes(n):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024.0:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} PB"


_loader_pool: Dict[
    str, "ResourceLoader"
] = dict()  # all ResourceLoaders are stored here


class ResourceLoader:
    ready: bool = False  # stands for each scan
    file_path_list: list = []
    _initialized: bool = False  # stands for the first scan on creation

    def __new__(
        cls,
        folder: str = ".",
        file_types=["*"],
        sub_dirs=True,
        verbose=False,
        force_rescan=False,
        *args,
        **kwargs,
    ):
        _id = folder + str(file_types) + "_R" if sub_dirs else ""
        if _id in _loader_pool and not force_rescan:
            logger.info(
                "ResourceLoader with same path and same file type(s) already exists. Returning the old one."
            )
        else:
            _loader_pool[_id] = super(ResourceLoader, cls).__new__(cls)
        return _loader_pool[_id]

    def __init__(
        self,
        folder: str = ".",
        file_types=["*"],
        sub_dirs=True,
        async_scan=False,
        verbose=False,
        force_rescan=False,
    ):
        """ResourceLoader scans given file type(s) in given place(s)

        Args:
            folder (str): which folder to scan
            file_types (str[]): file type(s) to include. For example, ['jpg','png']
            sub_dirs (bool, optional): scan sub-folder(s)?. Defaults to True.
            async_scan (bool, optional): run scan traks in a new thread. Defaults to False.
            verbose (bool, optional): verbose output. Defaults to False.
            force_rescan (bool, optional): rescan the folder even the same file type(s) was scanned here before. Default to False.
        """
        super().__init__()
        self.path = os.path.abspath(folder)
        self._file_types = file_types
        self._scan_sub_dirs = sub_dirs
        self._async_scan = async_scan
        if not self.ready:
            self._scan(verbose)

    def _scan(self, verbose):
        if not self.ready and self._initialized:
            raise Exception(
                "another scanning requested during the previous one."
            )
        self.ready = False

        def can_match(path: pathlib.Path):
            if not path.is_file():
                return False
            for file_type in self._file_types:
                if path.match("*." + file_type):
                    return True
            return False

        def perform_scan():
            glob_str = "**/*" if self._scan_sub_dirs else "*"
            if not verbose:  # do not output
                self.file_path_list = [
                    str(path)
                    for path in pathlib.Path(self.path).glob(glob_str)
                    if can_match(path)
                ]
            else:
                self.file_path_list = []
                for path in pathlib.Path(self.path).glob(glob_str):
                    if can_match(path):
                        self.file_path_list.append(path)
            self.ready = True  # scan complete
            if not self._initialized:
                self._initialized = True
            logger.info(
                f"Resource loader '{self.path}' ready with {'all' if '*' in self._file_types else len(self._file_types)} file types({len(self.file_path_list)} files)."
            )

        logger.info(
            f"Scanning started at '{self.path}' for {'all' if '*' in self._file_types else len(self._file_types)} file types."
        )
        # call to scan
        if self._async_scan:
            threading.Thread(target=perform_scan).start()
        else:
            perform_scan()

    def get_file_list(self):
        if not self.ready:
            raise Exception("not ready. scanning in process.")
        return self.file_path_list.copy()

    def __getitem__(self, index):
        if not self.ready:
            raise Exception("not ready. scanning in process.")
        if type(index) is int:
            return self.file_path_list[index]
