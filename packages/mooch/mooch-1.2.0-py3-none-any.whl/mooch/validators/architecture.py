import platform


def check(allowed: list[str]) -> None:
    """Check if the current machine architecture is among the allowed architectures.

    Args:
        allowed (list[str]): A list of allowed architecture names (case-insensitive).

    Raises:
        RuntimeError: If the current machine architecture is not in the allowed list.

    """
    current_arch = platform.machine().lower()
    allowed = [arch.lower() for arch in allowed]
    if current_arch not in allowed:
        msg = f"Allowed architecture: {allowed}. Detected: {current_arch}"
        raise RuntimeError(msg)
