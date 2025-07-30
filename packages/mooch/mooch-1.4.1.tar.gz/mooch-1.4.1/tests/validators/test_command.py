import shutil

import pytest

from mooch.validators import command

fake_valid_commands = ["python", "ls", "echo"]

@pytest.fixture()
def setup_fake_which(monkeypatch):
    def fake_which(cmd):
        return f"/usr/bin/{cmd}" if cmd in fake_valid_commands else None
    
    monkeypatch.setattr(shutil, "which", fake_which)

def test_check_all_commands_exist_list(setup_fake_which):
    command.check(fake_valid_commands)


def test_check_some_commands_missing(setup_fake_which):
    with pytest.raises(RuntimeError) as excinfo:
        command.check(["python", "ls", "foobar", "baz"])
    assert "foobar" in str(excinfo.value)
    assert "baz" in str(excinfo.value)


def test_check_no_commands(setup_fake_which):
    command.check([])



def test_check_all_commands_missing(setup_fake_which):
    with pytest.raises(RuntimeError) as excinfo:
        command.check(["foo", "bar"])
    assert "foo" in str(excinfo.value)
    assert "bar" in str(excinfo.value)


def test_check_variadic_args(setup_fake_which):
    command.check("python", "ls", "echo")

def test_check_mixed_args(setup_fake_which):
    command.check(["python", "ls"], "echo")
    command.check("python", ["ls"], "echo")

def test_check_variadic_args_with_missing(setup_fake_which):
    with pytest.raises(RuntimeError) as excinfo:
        command.check(["python", "ls", "foobar", "baz"])
    assert "foobar" in str(excinfo.value)
    assert "baz" in str(excinfo.value)
