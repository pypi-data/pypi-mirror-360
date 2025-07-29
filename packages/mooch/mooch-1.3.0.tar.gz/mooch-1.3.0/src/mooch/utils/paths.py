import sys
from pathlib import Path


def desktop_path() -> Path:
    """Return the filesystem path to the user's Desktop directory.

    On Windows, uses the Windows Shell API to retrieve the Desktop path.
    On other platforms, assumes the Desktop is located at '~/Desktop'.

    Returns:
        Path: The path to the Desktop directory.

    """
    if sys.platform.startswith("win"):
        import ctypes.wintypes  # noqa: PLC0415

        CSIDL_DESKTOPDIRECTORY = 0x10  # noqa: N806
        SHGFP_TYPE_CURRENT = 0  # noqa: N806

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOPDIRECTORY, None, SHGFP_TYPE_CURRENT, buf)
        path = Path(buf.value)
    else:
        path = Path.home() / "Desktop"
    return path
