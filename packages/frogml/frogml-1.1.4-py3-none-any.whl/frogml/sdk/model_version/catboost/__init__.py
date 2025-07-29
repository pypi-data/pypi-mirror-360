import logging
import os.path
import tempfile
from functools import partial
from typing import Dict, List, Optional, Any

from frogml.core.exceptions import FrogmlException
from frogml.core.utils.proto_utils import CATBOOST_SERIALIZED_TYPE

from frogml.sdk.model_version.utils.error_handling import handle_exception
from frogml.sdk.model_version.utils.files_tools import _get_full_model_path
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig
from frogml.sdk.model_version.utils.storage import (
    _get_model_info_from_artifactory,
    _download_model_version_from_artifactory,
    _log_model,
)
from frogml.sdk.model_version.utils.storage_helper import (
    _get_model_framework,
    _get_model_serialization_format,
    _get_model_framework_version,
)
from frogml.sdk.model_version.utils.validations import _validate_typed_log_model

_logger = logging.getLogger(__name__)

_CATBOOST_MODEL_FLAVOR = "catboost"


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
            serialized_type=CATBOOST_SERIALIZED_TYPE,
        )

        model.save_model(full_model_path, format=CATBOOST_SERIALIZED_TYPE)

        try:
            import catboost

            framework_version = catboost.__version__
        except Exception as e:
            raise FrogmlException(f"Failed to get Catboost version: {e}")

        config = ModelLogConfig(
            model_name=model_name,
            target_dir=target_dir,
            model_flavor=_CATBOOST_MODEL_FLAVOR,
            framework_version=framework_version,
            full_model_path=full_model_path,
            serialization_format=CATBOOST_SERIALIZED_TYPE,
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
    :param repository: Repository to get the model from
    :param model_name: Requested model name
    :param version: version of the model
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
    :return: Path to the model file
    """

    _logger.info(f"Loading model {model_name} from {repository}")
    with tempfile.TemporaryDirectory() as download_target_path:
        model_info = get_model_info(
            repository=repository, model_name=model_name, version=version
        )
        model_framework = _get_model_framework(model_info)
        serialization_format = _get_model_serialization_format(model_info)

        def deserializer_model(serialization_format, download_target_path, model_name):
            from catboost import CatBoostClassifier

            catboost_classifier = CatBoostClassifier()
            return catboost_classifier.load_model(
                os.path.join(
                    download_target_path, f"{model_name}.{serialization_format}"
                )
            )

        try:
            return _download_model_version_from_artifactory(
                model_flavor=_CATBOOST_MODEL_FLAVOR,
                repository=repository,
                model_name=model_name,
                version=version,
                model_framework=model_framework,
                download_target_path=download_target_path,
                deserializer=partial(
                    deserializer_model,
                    serialization_format,
                    download_target_path,
                    model_name,
                ),
            )
        except Exception as e:
            framework_runtime_version = _get_model_framework_version(model_info)
            logging.error(
                f"Failed to load Model. Model was serialized with Catboost version: {framework_runtime_version}"
            )
            raise FrogmlException(f"Failed to deserialized model: {e}")
