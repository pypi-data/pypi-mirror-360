import importlib

from frogml import __version__ as frogml_version
from frogml.core.inner.build_logic.interface.step_inteface import Step


class SetVersionStep(Step):
    STEP_DESCRIPTION = "Getting SDK Version"
    CLI_VERSION_NOT_AVAILABLE_MSG_FORMAT = (
        "CLI version not available, using core version {frogml_core_version}"
    )
    CLI_VERSION_FOUND_MSG_FORMAT = "Found sdk version {frogml_cli_version}"

    def description(self) -> str:
        return self.STEP_DESCRIPTION

    def execute(self) -> None:
        try:
            self.build_logger.debug("Getting sdk version")
            frogml_cli_version: str = importlib.import_module("frogml_cli").__version__
            self.context.frogml_cli_version = frogml_cli_version
            self.build_logger.debug(
                self.CLI_VERSION_FOUND_MSG_FORMAT.format(
                    frogml_cli_version=frogml_cli_version
                )
            )
        except ImportError:
            self.build_logger.debug(
                self.CLI_VERSION_NOT_AVAILABLE_MSG_FORMAT.format(
                    frogml_core_version=frogml_version
                )
            )
            self.context.frogml_cli_version = frogml_version
