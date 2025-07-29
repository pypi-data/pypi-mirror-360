from __future__ import annotations

import platform


def check(*allowed: str | list[str]) -> None:
    """Check if the current operating system is in the list of allowed operating systems.

    Args:
        allowed (list[str]): A list of allowed operating system names (case-insensitive).

    Raises:
        RuntimeError: If the current operating system is not in the allowed list.

    """
    current_os = platform.system().lower()
    flatten = []
    for f in allowed:
        if isinstance(f, list):
            flatten.extend(f)
        else:
            flatten.append(f)

    allowed = [os.lower() for os in flatten]
    if current_os not in allowed:
        msg = f"Allowed OS: {allowed}. Detected: {current_os}"
        raise RuntimeError(msg)
