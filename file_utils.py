import glob
import os
import json
import shutil
from pathlib import Path


def write_json_file(json_path, data):
    with open(json_path, "w") as f:
        json.dump(data, f)


def get_all_files_in_dir(path: str, file_extension="*") -> list[str]:
    return glob.glob(os.path.join(path, f"*.{file_extension}"))


def get_filename_without_extension(path: str) -> str:
    return os.path.basename(path).split(".")[0]


def copy_to_destination_dir(files: list[str], destination_dir: str):
    for file in files:
        shutil.copy(file, os.path.join(destination_dir, os.path.basename(file)))


def create_dir_if_not_exists(dir: str):
    Path(dir).mkdir(parents=True, exist_ok=True)


def remove_files_in_dir(dir: str):
    for file in get_all_files_in_dir(dir):
        os.remove(file)
