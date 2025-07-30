from __future__ import annotations

import os


def check(*required_vars: str | list[str]) -> None:
    """Check if all required environment variables are set.

    Args:
        required_vars (list[str]): A list of environment variable names to check.

    Raises:
        RuntimeError: If any of the required environment variables are missing.

    """
    flatten = []
    for f in required_vars:
        if isinstance(f, list):
            flatten.extend(f)
        else:
            flatten.append(f)
    missing = [var for var in flatten if not os.getenv(var)]
    if missing:
        msg = f"Missing required environment variable(s): {', '.join(missing)}"
        raise RuntimeError(msg)
