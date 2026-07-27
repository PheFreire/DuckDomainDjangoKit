from typing import (
    Any,
)

import toml

from dddk import (
    AppError,
)


class Parser:
    def toml_load(self, path: str) -> dict[str, Any]:
        """
        # Function that loads the TOML file from the given path and raises an AppError if something goes wrong.

        # Args:
            - path (str): The path to the TOML file to load.

        # Returns:
            - dict: Parsed content of the TOML file.

        # Raises:
            - AppError: If the TOML file cannot be loaded, raises an AppError with details.
        """
        try:
            return toml.load(path)
        except Exception as e:
            raise AppError(
                class_pointer=self,
                title="TomlFileLoadError",
                message="Failed to load the TOML file.",
                details={"exception_details": str(e), "invalid_path": path},
                code=500,
            )

    def json_load(self, path: str) -> dict[str, Any]:
        try:
            return toml.load(path)
        except Exception as e:
            raise AppError(
                class_pointer=self,
                title="TomlFileLoadError",
                message="Failed to load the TOML file.",
                details={"exception_details": str(e), "invalid_path": path},
                code=500,
            )
