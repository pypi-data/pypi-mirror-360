import logging
import os.path
import tempfile
from functools import partial
from typing import Dict, List, Optional, Any

from frogml.core.exceptions import FrogmlException
from frogml.core.utils.proto_utils import PYTORCH_FRAMEWORK_FORMAT

from frogml.sdk.model_version.utils.error_handling import handle_exception
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

_PYTORCH_MODEL_FLAVOR = "pytorch"


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
        full_model_path = os.path.join(
            target_dir, f"{model_name}.{PYTORCH_FRAMEWORK_FORMAT}"
        )

        try:
            import torch
            from frogml.sdk.model_version.pytorch import (
                pickle_module as pytorch_pickle_module,
            )

            torch.save(
                obj=model, f=full_model_path, pickle_module=pytorch_pickle_module
            )  # nosec B614

            model_version = torch.__version__
        except Exception as e:
            raise FrogmlException(f"Failed to get Pytorch version: {e}")

        config = ModelLogConfig(
            model_name=model_name,
            target_dir=target_dir,
            model_flavor=_PYTORCH_MODEL_FLAVOR,
            framework_version=model_version,
            full_model_path=full_model_path,
            serialization_format=PYTORCH_FRAMEWORK_FORMAT,
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
    """

    logging.info(f"Loading model {model_name} from {repository}")

    with tempfile.TemporaryDirectory() as download_target_path:
        model_info = get_model_info(
            repository=repository, model_name=model_name, version=version
        )
        model_framework = _get_model_framework(model_info)
        serialization_format = _get_model_serialization_format(model_info)

        def deserializer_model(model_path):
            import torch
            from frogml.sdk.model_version.pytorch import (
                pickle_module as pytorch_pickle_module,
            )

            return torch.load(
                f=model_path, pickle_module=pytorch_pickle_module
            )  # nosec B614

        try:
            return _download_model_version_from_artifactory(
                model_flavor=_PYTORCH_MODEL_FLAVOR,
                repository=repository,
                model_name=model_name,
                version=version,
                model_framework=model_framework,
                download_target_path=download_target_path,
                deserializer=partial(
                    deserializer_model,
                    os.path.join(
                        download_target_path, f"{model_name}.{serialization_format}"
                    ),
                ),
            )
        except Exception as e:
            framework_runtime_version = _get_model_framework_version(model_info)
            logging.error(
                f"Failed to load Model. Model was serialized with Pytorch version: {framework_runtime_version}"
            )
            raise FrogmlException(f"Failed to deserialized model: {e}")
