import os
import shutil
from pathlib import Path
from typing import Union


def create_dir(directory_name: Union[str, Path], replace=False):
    if isinstance(directory_name, Path):
        directory_name = str(directory_name)
    directory_path = os.path.abspath(directory_name)
    directory_path += os.path.sep

    if os.path.isdir(directory_path):
        # Directory already exists.
        if replace:
            shutil.rmtree(directory_path)
        else:
            return

    dir_parts = directory_path.split(os.sep)
    directory_to_create = ""
    for part in dir_parts:
        directory_to_create += part + os.sep
        if not os.path.isdir(directory_to_create):
            try:
                os.mkdir(directory_to_create)
            except FileNotFoundError:
                raise FileNotFoundError("failed to create dir " + str(directory_to_create))
