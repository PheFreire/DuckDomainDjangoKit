import os

from dddk import (
    AppError,
)
from dddk.envs.models import (
    DatabaseSettingsDto,
)
from dddk.envs.interfaces import (
    IEnvs,
)


class EnvsToml(IEnvs):
    def __get(self, env: str) -> str:
        """
        Get env or raise error
        """
        value = os.getenv(env)
        if value is None:
            raise AppError(
                self,
                "Env Key Error",
                f"environment variable '{env}' not found!",
                details={"env_key": env},
                code=500,
            )
        return value

    @property
    def database(self) -> DatabaseSettingsDto:
        return DatabaseSettingsDto.model_validate(
            {"url": self.__get("DATABASE_URL")}
        )
