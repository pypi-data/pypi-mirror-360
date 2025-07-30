import sys


def check() -> None:
    """Check if the current Python interpreter is running inside a virtual environment.

    Raises:
        RuntimeError: If a virtual environment is not activated.

    """
    result = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    if not result:
        msg = "Virtual environment is not activated."
        raise RuntimeError(msg)
