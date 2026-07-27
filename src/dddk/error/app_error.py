import os
import json
import inspect
from typing import (
    Any,
)


class AppError(Exception):
    """
    Custom exception class to represent application errors with detailed information.

    Attributes:
    - class_pointer: The class instance where the error originated.
    - title: A short, human-readable title for the error.
    - message: A detailed message describing the error.
    - details: Additional details for the error, typically a dictionary with further information.
    - code: An HTTP-like status code representing the type of error (default is 400).
    """

    def __init__(
        self,
        class_pointer: Any,
        title: str,
        message: str = "",
        details: dict[str, Any] | None = None,
        code: int = 400,
    ) -> None:
        frame = inspect.stack()[1]
        self._caller_file = os.path.relpath(frame.filename)
        self._caller_line = frame.lineno
        super().__init__(title)
        self.class_pointer = class_pointer
        self.title = title
        self.message = message
        self.details = details if details is not None else {}
        self.code = code

    @property
    def error(self) -> dict[str, Any]:
        return {
            "class_name": self._resolve_pointer(),
            "caller": f"{self._caller_file}:{self._caller_line}",
            "title": self.title,
            "message": self.message,
            "details": self.details,
            "code": self.code,
        }

    def _resolve_pointer(self) -> str:
        if isinstance(self.class_pointer, str):
            return self.class_pointer
        elif self.class_pointer is None:
            return ""
        return self.class_pointer.__class__.__name__

    def __str__(self) -> str:
        line = "-=" * 30
        try:
            error_details = json.dumps(
                self.error, ensure_ascii=False, indent=3, default=str
            )
        except TypeError:
            error_details = ""
            for k, v in self.error.items():
                error_details += f" {k}: {v}\n"

        return f"\n{line}\n\n({self.code})[{self.title.upper()}]: {self.message}\n\n{error_details}\n{line}\n"
