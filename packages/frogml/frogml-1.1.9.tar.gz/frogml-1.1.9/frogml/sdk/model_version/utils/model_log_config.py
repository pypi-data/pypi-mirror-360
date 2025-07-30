import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List, Any, Union

from packaging.version import Version, InvalidVersion
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    DirectoryPath,
    FilePath,
    computed_field,
    model_validator,
)
from typing_extensions import Self

from frogml.sdk.model_version.constants import ModelFramework
from frogml.sdk.model_version.utils.dependencies_tools import (
    _validate_conda,
    _validate_poetry,
    _validate_requirements,
    _validate_versions,
)
from frogml.storage.exceptions.validation_error import FrogMLValidationError


# According to Pydantic documentation, this is the correct way to use field_validator
# https://docs.pydantic.dev/latest/concepts/validators/#using-the-decorator-pattern
# noinspection PyNestedDecorators
class ModelLogConfig(BaseModel):
    model_name: str = Field(
        description="The name of the model being logged.", min_length=1, max_length=60
    )
    target_dir: DirectoryPath = Field(
        description="The directory where the model is stored."
    )
    model_framework: ModelFramework = Field(
        description="The flavor of the model, e.g., 'sklearn', 'tensorflow', etc."
    )
    framework_version: str = Field(
        description="The version of the model framework being used."
    )
    serialization_format: str = Field(
        description="The serialization format of the model, e.g., 'cbm', 'joblib', etc."
    )
    repository: str = Field(
        description="The repository where the model is logged.", min_length=1
    )
    version: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%d-%H-%M-%S-%f"
        )[:-3],
        description="The version of the model being logged. "
        "If no version provided then the current datetime will be used.",
        min_length=1,
    )
    properties: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional properties of the model, stored as key-value pairs.",
    )
    dependencies: Optional[List[str]] = Field(
        default=None,
        min_length=1,
        description="""List of dependencies required to run the model.
            Supported Dependency Types:
                1. requirements files path (e.g., dependencies = ["requirements.txt"])
                2. poetry files path (e.g., dependencies = ["pyproject.toml", "poetry.lock"])
                3. conda files path (e.g., dependencies = ["conda.yml"])
                4. Explicit versions (e.g., dependencies = ["pandas==1.2.3", "numpy==1.2.3"])""",
    )
    code_dir: Optional[DirectoryPath] = Field(
        default=None, description="Directory path containing the code."
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None, description="The model's parameters."
    )
    metrics: Optional[Dict[str, Any]] = Field(
        default=None, description="The model's metrics."
    )
    predict_file: Optional[FilePath] = Field(
        default=None, description="Path to the prediction file."
    )
    model_path: Optional[FilePath] = Field(
        default=None,
        description="The path to the model file, this should be set only when `model_framework` is `ModelFramework.FILES`.",
        exclude=True,
    )

    @field_validator("model_name")
    @classmethod
    def _validate_model_name(cls, value: str) -> str:
        # This regex ensures the string is made of segments of:
        #   - letters
        #   - numbers
        #   - underscores
        #   - or hyphens
        # separated by single dots, with no leading, trailing, or consecutive dots.
        pattern: str = r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$"

        if re.fullmatch(pattern, value):
            return value

        raise FrogMLValidationError(
            "Invalid model name. Please use only letters (A-Z, a-z), "
            "numbers (0-9), underscores (_), and hyphens (-). "
            "You may separate segments with single dots, but the name "
            "cannot start or end with a dot, "
            "and consecutive dots (..) are not allowed. "
            "Please update your input to match these rules."
        )

    @field_validator("framework_version")
    @classmethod
    def _validate_framework_version(cls, value: str) -> str:
        if not value:
            return value

        try:
            return str(Version(value))
        except InvalidVersion as e:
            raise FrogMLValidationError(
                f"Invalid framework version: {value}. "
                "Please provide a valid version that conform to PEP 440. "
                "https://peps.python.org/pep-0440/"
            ) from e

    @field_validator("dependencies")
    @classmethod
    def _validate_dependencies(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None

        if any(dep == "" for dep in value):
            raise FrogMLValidationError(
                "Dependencies list contains empty string elements, "
                "which are not allowed."
            )

        is_conda: bool = _validate_conda(value)
        is_poetry: bool = _validate_poetry(value)
        is_requirements: bool = _validate_requirements(value)
        is_explicit_version: bool = _validate_versions(value)

        if (
            not is_conda
            and not is_poetry
            and not is_requirements
            and not is_explicit_version
        ):
            raise FrogMLValidationError(
                """Dependencies are not in the correct format.
                Supported Dependency Types:
                    1. requirements files path (e.g., dependencies = ["requirements.txt"])
                    2. poetry files path (e.g., dependencies = ["pyproject.toml", "poetry.lock"])
                    3. conda files path (e.g., dependencies = ["conda.yml"])
                    4. Explicit versions (e.g., dependencies = ["pandas==1.2.3", "numpy==1.2.3"])"""
            )

        return value

    @field_validator("code_dir", "predict_file", mode="after")
    @classmethod
    def _resolve_paths(
        cls, path: Optional[Union[DirectoryPath, FilePath]]
    ) -> Optional[Union[DirectoryPath, FilePath]]:
        """
        Resolves the provided path to an absolute path.
        If the path is None, it returns None.
        """
        if path is None:
            return None

        return Path(path).resolve(strict=True)

    @model_validator(mode="after")
    def _validate_model(self: Self) -> Self:
        """
        Validates that either code_dir, dependencies, and predict_file are provided.
        or none of them

        :raise FrogMLValidationError: If the validation fails.
        """
        self.__validate_required_fields_combinations()
        self.__validate_predict_file_location()
        self.__validate_given_model_path()

        return self

    @computed_field  # type: ignore[misc]
    @property
    def full_model_path(self: Self) -> str:
        """
        Returns the full path to the model file, constructed from target_dir,
        model_name, and serialization_format.
        """
        if self.model_path is not None:
            return str(self.model_path.resolve().as_posix())

        return str(
            Path(
                os.path.join(
                    self.target_dir, f"{self.model_name}.{self.serialization_format}"
                )
            )
            .resolve()
            .as_posix()
        )

    def __validate_required_fields_combinations(self: Self):
        are_dependencies_set: bool = self.dependencies is not None
        are_all_fields_set: bool = (
            self.__is_code_dir_set()
            and are_dependencies_set
            and self.__is_predict_file_set()
        )

        are_none_fields_set: bool = (
            not self.__is_code_dir_set()
            and not are_dependencies_set
            and not self.__is_predict_file_set()
        )

        if not (are_all_fields_set or are_none_fields_set):
            raise FrogMLValidationError(
                "You must provide either all of code_dir, dependencies, "
                "and predict_file, or none of them."
            )

    def __validate_predict_file_location(self: Self):
        is_predict_file_not_located_in_code_dir: bool = (
            self.__is_predict_file_set()
            and self.__is_code_dir_set()
            and self.predict_file.parent != self.code_dir
        )

        if is_predict_file_not_located_in_code_dir:
            raise FrogMLValidationError(
                f"The predict_file {self.predict_file} must be located "
                f"within the code_dir directory (provided: {self.code_dir}."
            )

    def __is_code_dir_set(self: Self) -> bool:
        return self.code_dir is not None

    def __is_predict_file_set(self: Self) -> bool:
        return self.predict_file is not None

    def __validate_given_model_path(self: Self):
        if self.model_path is not None and self.model_framework != ModelFramework.FILES:
            raise FrogMLValidationError(
                "model_path should be set only when "
                "model_framework is ModelFramework.FILES."
            )

        if self.model_path is None and self.model_framework == ModelFramework.FILES:
            raise FrogMLValidationError(
                "model_path must be set when "
                "model_framework is ModelFramework.FILES."
            )
