import platform


def check(allowed: list[str]) -> None:
    """Check if the current operating system is in the list of allowed operating systems.

    Args:
        allowed (list[str]): A list of allowed operating system names (case-insensitive).

    Raises:
        RuntimeError: If the current operating system is not in the allowed list.

    """
    current_os = platform.system().lower()
    allowed = [os.lower() for os in allowed]
    if current_os not in allowed:
        msg = f"Allowed OS: {allowed}. Detected: {current_os}"
        raise RuntimeError(msg)
