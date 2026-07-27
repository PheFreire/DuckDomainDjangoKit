import os
from typing import (
    Any,
)

from dddk import (
    AppError,
)
from dddk.envs.models import (
    ApiSettingsDto,
    LogSettingsDto,
    DebugSettingsDto,
    DatabaseSettingsDto,
)
from dddk.utils.parser import (
    Parser,
)
from dddk.envs.interfaces import (
    IEnvs,
)


class EnvsToml(IEnvs):
    def __init__(self) -> None:
        self.parser = Parser()

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

    def __toml_env(self, key: str) -> dict[str, Any]:
        settings_path = self.__get("SETTINGS_PATH")
        envs = self.parser.toml_load(settings_path)
        field = envs.get(key)

        if field is not None:
            return field

        raise AppError(
            self,
            "Missing TOML Section",
            f"Missing '{key}' section in settings file",
            code=500,
        )

    @property
    def log(self) -> LogSettingsDto:
        return LogSettingsDto.model_validate(self.__toml_env("log"))

    @property
    def debug(self) -> DebugSettingsDto:
        return DebugSettingsDto.model_validate(self.__toml_env("debug"))

    @property
    def api(self) -> ApiSettingsDto:
        return ApiSettingsDto.model_validate(self.__toml_env("api"))

    @property
    def database(self) -> DatabaseSettingsDto:
        return DatabaseSettingsDto.model_validate(
            {"url": self.__get("DATABASE_URL")}
        )
