import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from frogml.core.exceptions import FrogmlException

_VERSION_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+==[a-zA-Z0-9_.-]+$")

_logger = logging.getLogger(__name__)


class DependencyManagerType(Enum):
    UNKNOWN = 0
    PIP = 1
    POETRY = 2
    CONDA = 3


@dataclass
class DependencyFileObject:
    dep_file_name: List[str]
    lock_file_name: str = field(default="")


DEPS_MANAGER_FILE_MAP = {
    DependencyManagerType.PIP: DependencyFileObject(dep_file_name=["requirements.txt"]),
    DependencyManagerType.POETRY: DependencyFileObject(
        dep_file_name=["pyproject.toml"], lock_file_name="poetry.lock"
    ),
    DependencyManagerType.CONDA: DependencyFileObject(
        dep_file_name=["conda.yml", "conda.yaml"]
    ),
}


def _dependency_files_handler(
    dependencies: List[str], target_dir: Union[Path, str]
) -> Optional[List[str]]:
    """
    Check if dependencies is list of version and create requirements.txt file
    :param dependencies: list of dependencies
    :param target_dir: temporary directory for explicit versions
    :return: List of dependencies if dependencies is not None else None
    """
    if dependencies:
        is_conda = _validate_conda(dependencies)
        is_poetry = _validate_poetry(dependencies)
        is_requirements = _validate_requirements(dependencies)
        is_explicit_version = _validate_versions(dependencies)

        if (
            not is_conda
            and not is_poetry
            and not is_requirements
            and not is_explicit_version
        ):
            _logger.error(f"Invalid dependencies: {dependencies}")
            raise FrogmlException(
                "Dependencies are not in the correct format. Supported formats are: poetry files path, conda files path, requirements files path, or explicit versions."
            )

        if (
            not is_conda
            and not is_poetry
            and not is_requirements
            and is_explicit_version
        ):
            return _create_requirements_file(
                dependencies=dependencies, target_dir=target_dir
            )

        return dependencies
    else:
        return None


def _create_requirements_file(
    dependencies: List[str], target_dir: Union[Path, str]
) -> List[str]:
    """
    Create requirements file from list of explicit versions
    :param dependencies:
    :return: requirements file path
    """
    requirements_path = os.path.join(target_dir, "requirements.txt")
    with open(requirements_path, "w") as file:
        for package in dependencies:
            if _VERSION_PATTERN.match(package):
                file.write(package + "\n")
            else:
                _logger.info(f"Invalid package format: {package}")
        _logger.debug(f"Requirements file created at: {requirements_path}")
        return [requirements_path]


def _validate_conda(dependencies: List[str]) -> bool:
    """
    Validate if dependencies is conda type
    :param dependencies: list of conda files
    :return: true if all conda files are existing else false
    """

    conda_deps_manager = DEPS_MANAGER_FILE_MAP.get(DependencyManagerType.CONDA)
    requirements_file_count = len(dependencies) == 1
    is_valida_conda_file_path = False

    if requirements_file_count:
        file_path = dependencies[0]
        file_path = os.path.expanduser(file_path)
        for conda_dep_file in conda_deps_manager.dep_file_name:
            if file_path.__contains__(conda_dep_file) and os.path.exists(file_path):
                is_valida_conda_file_path = True

    return is_valida_conda_file_path


def _validate_poetry(dependencies: List[str]) -> bool:
    """
    Validate if dependencies is poetry type
    :param dependencies: list of poetry files
    :return: true if all poetry files are existing else false
    """

    poetry_deps_manager = DEPS_MANAGER_FILE_MAP.get(DependencyManagerType.POETRY)

    is_lock_file_validate = False
    is_toml_file_validate = False
    requirements_file_count = len(dependencies) == 2

    for dependency in dependencies:
        dependency = os.path.expanduser(dependency)
        if dependency.__contains__(
            poetry_deps_manager.dep_file_name[0]
        ) and os.path.exists(dependency):
            is_toml_file_validate = True
        elif dependency.__contains__(
            poetry_deps_manager.lock_file_name
        ) and os.path.exists(dependency):
            is_lock_file_validate = True

    return is_toml_file_validate or (
        is_lock_file_validate and requirements_file_count and is_toml_file_validate
    )


def _validate_requirements(dependencies: List[str]) -> bool:
    """
    Validate if dependencies is requirements type
    :param dependencies:
    :return: true if all requirements files are existing else false
    """

    pip_deps_manager = DEPS_MANAGER_FILE_MAP.get(DependencyManagerType.PIP)

    for dependency in dependencies:
        dependency = os.path.expanduser(dependency)
        if (
            dependency.__contains__(pip_deps_manager.dep_file_name[0])
            and len(dependencies) == 1
        ):
            return True

    return False


def _validate_versions(packages: List[str]):
    """
    Validate if packages are in the correct format
    :param packages: list of packages
    :return: True if all packages are in the correct format else False
    """
    return all(_VERSION_PATTERN.match(pkg) for pkg in packages)
