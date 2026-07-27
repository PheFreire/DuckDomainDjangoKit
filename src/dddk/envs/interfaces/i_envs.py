from abc import (
    ABC,
    abstractmethod,
)

from duckdi import (
    Interface,
)

from dddk.envs.models import (
    LogSettingsDto,
)
from dddk.envs.models.api_settings_dto import (
    ApiSettingsDto,
)
from dddk.envs.models.debug_settings_dto import (
    DebugSettingsDto,
)
from dddk.envs.models.database_settings_dto import (
    DatabaseSettingsDto,
)


@Interface(label="env")
class IEnvs(ABC):
    '''Return the env setting from env file defined on "$SETTINGS_PATH"'''

    @property
    @abstractmethod
    def log(self) -> LogSettingsDto:
        """Return log settings"""

    @property
    @abstractmethod
    def debug(self) -> DebugSettingsDto:
        """Return debug settings"""

    @property
    @abstractmethod
    def api(self) -> ApiSettingsDto:
        """Return api settings"""

    @property
    @abstractmethod
    def database(self) -> DatabaseSettingsDto:
        """Return database settings"""
