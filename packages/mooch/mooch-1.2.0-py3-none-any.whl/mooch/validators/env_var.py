import os


def check(required_vars: list[str]) -> None:
    """Check if all required environment variables are set.

    Args:
        required_vars (list[str]): A list of environment variable names to check.

    Raises:
        RuntimeError: If any of the required environment variables are missing.

    """
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        msg = f"Missing required environment variable(s): {', '.join(missing)}"
        raise RuntimeError(msg)
