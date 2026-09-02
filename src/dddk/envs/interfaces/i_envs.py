from abc import (
    ABC,
    abstractmethod,
)

from duckdi import (
    Interface,
)

from dddk.envs.models.database_settings_dto import (
    DatabaseSettingsDto,
)


@Interface(label="env")
class IEnvs(ABC):
    """Return the environment configuration for the running process."""

    @property
    @abstractmethod
    def database(self) -> DatabaseSettingsDto:
        """Return database settings"""
