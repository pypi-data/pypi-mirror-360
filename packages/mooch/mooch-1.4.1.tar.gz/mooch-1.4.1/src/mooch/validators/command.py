from __future__ import annotations

import shutil


def check(*commands: str | list[str]) -> None:
    """Check if the specified command-line programs are available in the system's PATH.

    Args:
        commands (list[str]): A list of command names to check for availability.

    Raises:
        RuntimeError: If any of the specified commands are not found in the system's PATH.

    """
    flatten = []
    for f in commands:
        if isinstance(f, list):
            flatten.extend(f)
        else:
            flatten.append(f)
    missing = [cmd for cmd in flatten if shutil.which(cmd) is None]
    if missing:
        msg = f"Missing required command(s): {', '.join(missing)}"
        raise RuntimeError(msg)
