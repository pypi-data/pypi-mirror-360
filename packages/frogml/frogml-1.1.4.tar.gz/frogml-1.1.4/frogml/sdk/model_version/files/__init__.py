import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig
from frogml.storage.frog_ml import FrogMLStorage

from frogml.sdk.model_version.utils.error_handling import handle_exception
from frogml.sdk.model_version.utils.files_tools import _get_file_extension
from frogml.sdk.model_version.utils.storage import (
    _get_model_info_from_artifactory,
    _log_model,
)
from frogml.sdk.model_version.utils.storage_helper import _get_model_framework
from frogml.sdk.model_version.utils.validations import (
    _validate_load_model,
    _validate_log_files_model,
)

_logger = logging.getLogger(__name__)

_FILES_MODEL_FLAVOR = "files"


def log_model(
    source_path: str,
    repository: str,
    model_name: str,
    version: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None,
    dependencies: Optional[List[str]] = None,
    code_dir: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    predict_file: Optional[str] = None,
) -> None:
    """
    Log model to a repository in Artifactory.
    :param source_path: Path to the model to be logged`
    :param repository: Repository to log the model to
    :param model_name: Name of the model
    :param version: Version of the model
    :param properties: Model properties
    :param dependencies: Model dependencies path
    :param code_dir: Model code directory path
    :param parameters: Model parameters
    :param metrics: Model metrics
    :return: None
    """

    _logger.info(f"Logging model {model_name} to {repository}")

    _validate_log_files_model(
        source_path=source_path,
        repository=repository,
        model_name=model_name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
        parameters=parameters,
        metrics=metrics,
        predict_file=predict_file,
    )

    with tempfile.TemporaryDirectory() as target_dir:
        config = ModelLogConfig(
            model_name=model_name,
            target_dir=target_dir,
            model_flavor=_FILES_MODEL_FLAVOR,
            framework_version="",
            full_model_path=source_path,
            serialization_format=_get_file_extension(source_path),
            repository=repository,
            version=version,
            properties=properties,
            dependencies=dependencies,
            code_dir=code_dir,
            parameters=parameters,
            metrics=metrics,
            predict_file=predict_file,
        )
        try:
            _log_model(config=config)
        except Exception as e:
            handle_exception(e, model_name, repository)


def load_model(
    repository: str, model_name: str, version: str, target_path: Optional[str] = None
) -> Path:
    """
    Load model from Artifactory.
    :param repository: Repository to load the model from
    :param model_name: Name of the model
    :param version: Version of the model
    :param target_path: Path to save the model
    :return: Path to the model file
    """

    _logger.info(f"Loading model {model_name} from {repository}")

    model_info = get_model_info(
        repository=repository, model_name=model_name, version=version
    )
    model_framework = _get_model_framework(model_info)

    _validate_load_model(
        repository=repository,
        model_name=model_name,
        version=version,
        model_framework=model_framework,
        model_flavor=_FILES_MODEL_FLAVOR,
    )

    target_path = target_path if target_path else tempfile.mkdtemp()

    FrogMLStorage().download_model_version(
        repository=repository,
        model_name=model_name,
        version=version,
        target_path=target_path,
    )

    return Path(target_path)


def get_model_info(repository: str, model_name: str, version: str) -> Dict:
    """
    Get model information
    :param repository: Repository to get the model from
    :param model_name: Requested model name
    :param version: Version of the model
    :return: Model information
    """

    _logger.info(f"Getting model {model_name} information from {repository}")
    return _get_model_info_from_artifactory(
        repository=repository,
        model_name=model_name,
        version=version,
    )
