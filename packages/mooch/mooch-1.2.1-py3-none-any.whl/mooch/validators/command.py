import shutil


def check(commands: list[str]) -> None:
    """Check if the specified command-line programs are available in the system's PATH.

    Args:
        commands (list[str]): A list of command names to check for availability.

    Raises:
        RuntimeError: If any of the specified commands are not found in the system's PATH.

    """
    missing = [cmd for cmd in commands if shutil.which(cmd) is None]
    if missing:
        msg = f"Missing required command(s): {', '.join(missing)}"
        raise RuntimeError(msg)
