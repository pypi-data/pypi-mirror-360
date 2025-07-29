import logging
import os.path
import tempfile
from functools import partial
from typing import Dict, List, Optional, Any

import joblib
from frogml.core.exceptions import FrogmlException
from frogml.core.utils.proto_utils import SCIKIT_LEARN_FRAMEWORK_FORMAT

from frogml.sdk.model_version.utils.error_handling import handle_exception
from frogml.sdk.model_version.utils.files_tools import _get_full_model_path
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig
from frogml.sdk.model_version.utils.storage import (
    _log_model,
    _get_model_info_from_artifactory,
    _download_model_version_from_artifactory,
)
from frogml.sdk.model_version.utils.storage_helper import (
    _get_model_framework,
    _get_model_serialization_format,
    _get_model_framework_version,
)
from frogml.sdk.model_version.utils.validations import (
    _validate_typed_log_model,
    _validate_load_model,
)

_logger = logging.getLogger(__name__)
_SCIKIT_LEARN_MODEL_FLAVOR = "scikit_learn"


def log_model(
    model,
    model_name: str,
    repository: str,
    version: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None,
    dependencies: Optional[List[str]] = None,
    code_dir: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    predict_file: Optional[str] = None,
) -> None:
    _logger.info(f"Logging model {model_name} to {repository}")

    _validate_typed_log_model(
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
        full_model_path = _get_full_model_path(
            target_dir=target_dir,
            model_name=model_name,
            serialized_type=SCIKIT_LEARN_FRAMEWORK_FORMAT,
        )

        joblib.dump(model, full_model_path)

        try:
            import sklearn

            model_version = sklearn.__version__
        except Exception as e:
            raise FrogmlException(f"Failed to get scikit-learn version: {e}")

        config = ModelLogConfig(
            model_name=model_name,
            target_dir=target_dir,
            model_flavor=_SCIKIT_LEARN_MODEL_FLAVOR,
            framework_version=model_version,
            full_model_path=full_model_path,
            serialization_format=SCIKIT_LEARN_FRAMEWORK_FORMAT,
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


def get_model_info(repository: str, model_name: str, version: str) -> Dict:
    """
    Get model information
    :param repository:
    :param model_name:
    :param version:
    :return: Model information
    """

    _logger.info(f"Getting model {model_name} information from {repository}")
    return _get_model_info_from_artifactory(
        repository=repository,
        model_name=model_name,
        version=version,
    )


def load_model(repository: str, model_name: str, version: str):
    """
    Load model from Artifactory.
    :param repository: Repository to load the model from
    :param model_name: Name of the model
    :param version: Version of the model
    :return: Loaded model
    """

    _logger.info(f"Loading model {model_name} from {repository}")

    model_info = get_model_info(
        repository=repository, model_name=model_name, version=version
    )
    model_framework = _get_model_framework(model_info)
    serialization_format = _get_model_serialization_format(model_info)

    _validate_load_model(
        repository=repository,
        model_name=model_name,
        version=version,
        model_framework=model_framework,
        model_flavor=_SCIKIT_LEARN_MODEL_FLAVOR,
    )
    with tempfile.TemporaryDirectory() as download_target_path:
        full_model_path = os.path.join(
            download_target_path, f"{model_name}.{serialization_format}"
        )

        def deserializer_model(model_path):
            import joblib

            model = joblib.load(model_path)
            return model

        try:
            return _download_model_version_from_artifactory(
                model_flavor=_SCIKIT_LEARN_MODEL_FLAVOR,
                repository=repository,
                model_name=model_name,
                version=version,
                model_framework=model_framework,
                download_target_path=download_target_path,
                deserializer=partial(deserializer_model, full_model_path),
            )

        except Exception as e:
            model_info = get_model_info(
                repository=repository, model_name=model_name, version=version
            )
            framework_runtime_version = _get_model_framework_version(model_info)
            logging.error(
                f"Failed to load Model. Model was serialized with scikit-learn version: {framework_runtime_version}"
            )
            raise FrogmlException(f"Failed to deserialized model: {e}")
