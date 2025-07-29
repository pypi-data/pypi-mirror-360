import shutil

import pytest

from mooch.validators import command


def test_check_all_commands_exist(monkeypatch):
    # Simulate all commands exist
    monkeypatch.setattr(shutil, "which", lambda cmd: f"/usr/bin/{cmd}")
    # Should not raise
    command.check(["python", "ls", "echo"])


def test_check_some_commands_missing(monkeypatch):
    # Simulate only 'python' exists
    def fake_which(cmd):
        return f"/usr/bin/{cmd}" if cmd == "python" else None

    monkeypatch.setattr(shutil, "which", fake_which)
    with pytest.raises(RuntimeError) as excinfo:
        command.check(["python", "foobar", "baz"])
    assert "foobar" in str(excinfo.value)
    assert "baz" in str(excinfo.value)


def test_check_no_commands(monkeypatch):
    # Should not raise if empty list
    command.check([])


def test_check_all_commands_missing(monkeypatch):
    # Simulate no commands exist
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    with pytest.raises(RuntimeError) as excinfo:
        command.check(["foo", "bar"])
    assert "foo" in str(excinfo.value)
    assert "bar" in str(excinfo.value)
