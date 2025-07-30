from __future__ import annotations

import platform


def check(*allowed: str | list[str]) -> None:
    """Check if the current machine architecture is among the allowed architectures.

    Args:
        allowed (list[str]): A list of allowed architecture names (case-insensitive).

    Raises:
        RuntimeError: If the current machine architecture is not in the allowed list.

    """
    current_arch = platform.machine().lower()
    flatten = []
    for f in allowed:
        if isinstance(f, list):
            flatten.extend(f)
        else:
            flatten.append(f)
    allowed = [arch.lower() for arch in flatten]
    if current_arch not in allowed:
        msg = f"Allowed architecture: {allowed}. Detected: {current_arch}"
        raise RuntimeError(msg)
