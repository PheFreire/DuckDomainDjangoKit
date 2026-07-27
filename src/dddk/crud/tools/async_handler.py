from __future__ import (
    annotations,
)

from typing import (
    Any,
    Generic,
    TypeVar,
    cast,
)
from collections.abc import (
    Callable,
    Iterator,
)
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)

from dddk.error.app_error import (
    AppError,
)

T = TypeVar("T")
R = TypeVar("R")


class AsyncHandler(Generic[T]):
    """
    A concurrent data processor that divides collections into chunks and applies
    a function across them using threads.

    Example
    -------
        handler = AsyncHandler(data=users, object_name="User")
        results = handler.map(serialize_users, divisions=8)

    Notes
    -----
    - Uses ThreadPoolExecutor.
    - Automatically balances chunks and preserves result order.
    - Converts any internal failure to a standardized AppError.
    """

    def __init__(self, data: list[T], object_name: str) -> None:
        self.data = data
        self.object_name = object_name

    def get_chunks(self, divisions: int) -> Iterator[list[T]]:
        """Split data into exactly `divisions` balanced chunks for parallel processing."""

        total = len(self.data)
        divisions = max(1, min(divisions, total))
        base_size, remainder = divmod(total, divisions)

        start = 0
        for i in range(divisions):
            end = start + base_size + (1 if i < remainder else 0)
            yield self.data[start:end]
            start = end

    def parallel_map(
        self,
        func: Callable[[list[T]], list[R]] | Any,
        divisions: int = 4,
        class_pointer: Any = None,
    ) -> list[R] | AppError:
        """
        Execute a function in parallel over divided chunks of data.

        Parameters
        ----------
        func : Callable[[List[T]], List[R]]
            Function to apply to each data chunk. Must return a list of results.
        divisions : int, optional
            Number of worker threads to spawn. Default is 4.
        class_pointer : Any, optional
            Context object for error attribution.

        Returns
        -------
        List[R] | AppError
            - A flattened list containing all successfully processed results,
              preserving the original chunk order.
            - An `AppError` instance if the provided function is not callable
              or if any thread or chunk raises an exception during execution.
        """

        if not callable(func):
            return self.__function_not_callable_error(func, class_pointer)

        if not self.data:
            return []

        results: list[list[R] | None] = [None] * divisions
        try:
            max_workers = min(divisions, len(self.data))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(func, chunk): idx
                    for idx, chunk in enumerate(self.get_chunks(divisions))
                }

                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        result = cast(list[R], future.result())
                        results[idx] = result
                    except Exception as e:
                        return self.__thread_process_error(
                            e, class_pointer, idx
                        )

            return [item for sublist in results if sublist for item in sublist]

        except Exception as e:
            return self.__thread_process_error(e, class_pointer)

    # -------------------------------------------------------------------------
    # Error builders
    # -------------------------------------------------------------------------

    def __function_not_callable_error(
        self, func: Any, class_pointer: Any
    ) -> AppError:
        return AppError(
            class_pointer=class_pointer or self,
            title="Invalid Function Argument",
            message="The provided `func` parameter must be callable.",
            details={
                "provided_type": type(func).__name__,
                "expected_type": "Callable[[List[T]], List[R]]",
                "hint": "Ensure you are passing a function, lambda, or method reference — not the result of a call.",
            },
            code=400,
        )

    def __thread_process_error(
        self, e: Exception, class_pointer: Any, idx: int | None = None
    ) -> AppError:
        return AppError(
            class_pointer=class_pointer or self,
            title="Threaded Execution Failed",
            message="An unexpected error occurred during threaded execution.",
            details={
                "object_name": self.object_name,
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                **({"chunk_num": str(idx)} if idx is not None else {}),
            },
            code=500,
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int) -> T:
        return self.data[index]

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        """Developer-friendly representation for debugging."""
        return (
            f"<AsyncHandler object='{self.object_name}' size={len(self.data)}>"
        )
