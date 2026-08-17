from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


RETRYABLE_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
)


def run_with_retry(
    operation: Callable[[], T],
    *,
    attempts: int = 3,
    delay_seconds: float = 5.0,
) -> T:
    """
    Retry a callable a small number of times for transient failures.

    We intentionally do not retry every exception because permanent
    validation or authentication failures should fail fast.
    """

    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return operation()

        except RETRYABLE_EXCEPTIONS as exc:
            last_error = exc

            if attempt == attempts:
                break

            wait_time = delay_seconds * attempt

            print(
                f"Transient error on attempt {attempt}/{attempts}: {exc}"
            )
            print(f"Retrying in {wait_time:.1f} seconds...")

            time.sleep(wait_time)

    if last_error is not None:
        raise last_error

    raise RuntimeError("Operation failed without a captured exception.")