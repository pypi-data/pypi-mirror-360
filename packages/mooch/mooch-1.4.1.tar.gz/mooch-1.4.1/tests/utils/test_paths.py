import sys
import types
from pathlib import Path

import pytest

from mooch.utils.paths import desktop_path


@pytest.mark.parametrize(
    "platform,expected",
    [
        ("linux", Path.home() / "Desktop"),
        ("darwin", Path.home() / "Desktop"),
    ],
)
def test_desktop_path_non_windows(monkeypatch, platform, expected):
    monkeypatch.setattr(sys, "platform", platform)
    result = desktop_path()
    assert result == expected


def test_desktop_path_windows(monkeypatch):
    # Fake platform
    monkeypatch.setattr(sys, "platform", "win32")

    # Prepare fake ctypes and Path
    class FakeBuffer:
        def __init__(self, value):
            self.value = value

    class FakeCtypes:
        wintypes = types.SimpleNamespace(MAX_PATH=260)

        @staticmethod
        def create_unicode_buffer(size):
            return FakeBuffer("C:\\Users\\TestUser\\Desktop")

        class windll:
            class shell32:
                @staticmethod
                def SHGetFolderPathW(a, b, c, d, buf):
                    buf.value = "C:\\Users\\TestUser\\Desktop"

    monkeypatch.setitem(sys.modules, "ctypes", FakeCtypes)
    monkeypatch.setitem(sys.modules, "ctypes.wintypes", FakeCtypes.wintypes)

    result = desktop_path()
    assert result == Path("C:\\Users\\TestUser\\Desktop")
