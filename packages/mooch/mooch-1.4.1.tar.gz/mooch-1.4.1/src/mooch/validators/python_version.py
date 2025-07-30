import platform

from packaging.version import Version


def check(min_version: str) -> None:
    """Check if the current Python version meets the specified minimum version requirement.

    Args:
        min_version (str): The minimum required Python version (e.g., "3.8").

    Raises:
        RuntimeError: If the current Python version is less than the specified minimum version.

    """
    if Version(platform.python_version()) < Version(min_version):
        msg = f"Python {min_version}+ required."
        raise RuntimeError(msg)
