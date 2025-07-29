import os
import shutil
from pathlib import Path
from typing import List, Optional

from frogml.core.exceptions import FrogmlException

DEFAULT_ZIP_NAME = "code"
DEFAULT_ZIP_FORMAT = "zip"
IGNORED_PATTERNS_FOR_UPLOAD = [r"\..*", r"__pycache__"]
HIDDEN_DIRS_TO_INCLUDE = [".dvc"]
HIDDEN_FILES_PREFIX = "."


def _zip_dir(
    root_dir: str,
    dir_to_zip: str,
    zip_name: str = DEFAULT_ZIP_NAME,
) -> Optional[str]:
    """
    Zip model code directory
    :param root_dir: The root directory to put the zip into
    :param dir_to_zip: The directory to zip
    :param zip_name: Name of the zipped file
    :return: return str object of the zipped file
    """
    try:
        zip_file_path = os.path.join(root_dir, zip_name)
        zip_path = Path(
            shutil.make_archive(
                base_name=zip_file_path,
                format=DEFAULT_ZIP_FORMAT,
                root_dir=dir_to_zip,
            )
        )

        return zip_path.absolute().as_posix()

    except Exception as e:
        raise FrogmlException(f"Unable to zip model: {e}") from e


def _copy_dir_without_ignored_files(source_dir: str, parent_dir_path: str) -> str:
    """
    Copy directory to target directory

    :param source_dir: Source directory
    :param parent_dir_path: The parent directory to copy the source directory

    :return: Copied directory path
    """
    source_dir: str = os.path.abspath(source_dir)
    dest_dir: str = os.path.join(parent_dir_path, "filtered_model_files")
    ignored_files: List[str] = _get_files_to_ignore(directory=Path(source_dir))
    shutil.copytree(
        src=source_dir,
        dst=dest_dir,
        ignore=shutil.ignore_patterns(*ignored_files),
        dirs_exist_ok=True,
    )

    return dest_dir


def _get_files_to_ignore(directory: Path) -> List[str]:
    def ignore_hidden(file: Path, exclusions: List[str]):
        name = os.path.basename(os.path.abspath(file))
        is_hidden = name.startswith(HIDDEN_FILES_PREFIX) and name not in exclusions
        return is_hidden

    return [
        file.name
        for file in Path(directory).rglob("*")
        if ignore_hidden(file, exclusions=HIDDEN_DIRS_TO_INCLUDE)
    ]


def _get_file_extension(file_path: str) -> str:
    """
    Get file extension
    :param file_path: File path
    :return: File extension
    """
    suffix = Path(file_path).suffix
    if suffix:
        suffix = suffix[1:]
    return suffix


def _get_full_model_path(target_dir: str, model_name: str, serialized_type: str) -> str:
    return os.path.join(target_dir, f"{model_name}.{serialized_type}")


def _remove_dir(dir_path: str):
    """
    Remove a directory
    :param dir_path: The directory's path
    """
    shutil.rmtree(dir_path, ignore_errors=True)
