import os
import re
from typing import Dict, List, Optional, Any

from frogml.core.exceptions import FrogmlException


def _validate_existing_path(path: str) -> None:
    """
    validating if path is existing
    :param path:
    :return: None if validation pass successfully else rase error
    """

    if not os.path.exists(path):
        raise FrogmlException(f"Path {path} does not exist")


def __validate_is_directory(path: str) -> None:
    """
    Validate if path is a directory
    :param path: path to validate
    :return: None if validation pass successfully else raise error
    """
    _validate_existing_path(path)

    if not os.path.isdir(path):
        raise FrogmlException(f"Path {path} is not a directory")


def _validate_string(s: str) -> None:
    """
    Validate if string is not empty
    :param s: string
    :return: None if validation pass successfully else raise error
    """
    if not s:
        raise FrogmlException("String is empty")


def _validate_model_name(name: str) -> None:
    """
    Validate if model name is not empty, if the model name is shorter than 60 characters and if the model name match the regex pattern: ^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$ # noqa
    :param name: model name
    :return: None if validation pass successfully else raise error
    """
    _validate_string(name)
    pattern = r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$"

    if not re.fullmatch(pattern, name):
        raise FrogmlException(
            """Invalid input: The string must follow these rules:
        1. Only letters (A-Z, a-z), numbers (0-9), underscores (_), and hyphens (-) are allowed.
        2. Dot-separated segments are allowed, but:
           - The string cannot start or end with a dot.
           - Consecutive dots (..) are not allowed.
            Please modify your input to meet these requirements."""
        )
    if len(name) > 60:
        raise FrogmlException("Model name should be shorter than 60 characters")


def _validate_properties(properties: Dict[str, str]) -> None:
    """
    Validate if properties is dictionary type and if all keys and values are string
    :param properties: dictionary of properties
    :return: None if validation pass successfully else raise error
    """
    if not isinstance(properties, dict):
        raise ValueError("Properties should be dictionary")
    for key, value in properties.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise FrogmlException("Properties keys and values should be string")


def _validate_dict_keys_are_strings(d: Dict[str, Any]) -> None:
    """
    Validate if dictionary is not empty and if all keys are string
    :param d: dictionary
    :return: None if validation pass successfully else raise error
    """
    if not isinstance(d, dict):
        raise ValueError("Properties should be dictionary")
    for key in d.keys():
        if not isinstance(key, str):
            raise FrogmlException("Dictionary keys should be string")


def _validate_dependencies(dependencies: List[str]) -> None:
    """
    Validate if dependencies is list of strings
    :param dependencies: list of strings
    :return: None if validation pass successfully else raise error
    """
    if not isinstance(dependencies, list):
        raise ValueError("Dependencies should be list")
    for dependency in dependencies:
        if not isinstance(dependency, str):
            raise FrogmlException(
                "Dependencies should be list of files paths or list of explicit dependencies"
            )


def _validate_load_model(
    repository: str,
    model_name: str,
    version: str,
    model_framework: str,
    model_flavor: str,
) -> None:
    """
    Private method that validate user input
    :param repository: repository name
    :param model_name: the name of the model
    :param version: version of the model
    :param model_framework: model framework files/catbbost etc..
    :param model_flavor: model flavor files/catboost etc..
    :return: None if validation passed successfully
    """

    _validate_string(repository)

    _validate_string(model_name)
    _validate_string(version)
    if model_framework != model_flavor:
        raise FrogmlException(
            f"The Model: {model_name} in Repository: {repository} - is not a {model_flavor} model"
        )


def _validate_log_files_model(
    source_path: str,
    repository: str,
    model_name: str,
    version: Optional[str],
    properties: Optional[Dict[str, str]],
    dependencies: Optional[List[str]],
    code_dir: Optional[str],
    parameters: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    predict_file: Optional[str] = None,
):
    """
    Private method that validate user input
    :param source_path: path to serialized model
    :param repository: repository name
    :param model_name: the name of the model
    :param version: version of the model
    :param properties: model properties
    :param dependencies: list of dependencies
    :param code_dir: directory path containing the code
    :return: None if validation passed successfully
    """

    _validate_existing_path(source_path)
    _validate_string(repository)
    _validate_string(model_name)

    if version:
        _validate_string(version)
    if code_dir:
        _validate_existing_path(code_dir)
    if properties:
        _validate_properties(properties)
    if dependencies:
        _validate_dependencies(dependencies)
    if parameters:
        _validate_dict_keys_are_strings(parameters)
    if metrics:
        _validate_dict_keys_are_strings(metrics)
    if predict_file:
        _validate_string(predict_file)


def _validate_typed_log_model(
    repository: str,
    model_name: str,
    version: Optional[str],
    properties: Optional[Dict[str, str]],
    dependencies: Optional[List[str]],
    code_dir: Optional[str],
    parameters: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    predict_file: Optional[str] = None,
):
    _validate_string(repository)

    _validate_model_name(model_name)

    if version:
        _validate_string(version)

    if properties:
        _validate_properties(properties)

    if dependencies:
        for dependency in dependencies:
            _validate_string(dependency)

    if code_dir:
        __validate_is_directory(code_dir)

    if parameters:
        _validate_dict_keys_are_strings(parameters)

    if metrics:
        _validate_dict_keys_are_strings(metrics)

    if predict_file:
        _validate_string(predict_file)


def _validate_code_dependencies(
    code_dir: Optional[str],
    dependencies: Optional[List[str]],
    predict_file: Optional[str],
) -> None:
    """
    Validates that either all of code_dir, dependencies, and predict_file are provided,
    or none of them.

    Raises ValueError if the validation fails.
    """
    if (code_dir is None) != (dependencies is None) or (dependencies is None) != (
        predict_file is None
    ):
        raise FrogmlException(
            "You must provide either all of code_dir, dependencies, and predict_file, or none of them."
        )

    __validate_predict_file_in_code_dir(code_dir, predict_file)


def __validate_predict_file_in_code_dir(code_dir, predict_file):
    """
    Validates the presence of the `predict_file` in the specified `code_dir`.

    If `code_dir` is provided, ensures it is a valid directory. If `predict_file` is provided,
    checks whether the file exists within the `code_dir`.

    :param code_dir: Directory containing the code.
    :param predict_file: Name of the prediction file expected in the code directory.
    :raises FrogmlException: If `code_dir` is not a valid directory or if `predict_file` does not exist in `code_dir`.
    """
    if code_dir is not None:
        __validate_is_directory(code_dir)
        full_predict_path = os.path.join(code_dir, predict_file)
        if not os.path.isfile(full_predict_path):
            raise FrogmlException(f"'{predict_file}' does not exist in '{code_dir}'.")
