import logging

from frogml.core.exceptions import FrogmlException

_logger = logging.getLogger(__name__)


def handle_exception(exception: Exception, model_name: str, repository: str) -> None:
    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(
            f"An error occurred while logging model {model_name} to {repository}"
        )
        raise RuntimeError(
            f"Exception in model: {model_name}, repository: {repository}"
        ) from exception
    else:
        _logger.error(
            f"An error occurred while logging model {model_name} to {repository}"
        )
        raise FrogmlException(f"An error occurred: {exception}") from None
