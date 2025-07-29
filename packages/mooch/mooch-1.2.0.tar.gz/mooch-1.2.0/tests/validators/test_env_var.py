import pytest

from mooch.validators import env_var


def test_check_all_vars_present(monkeypatch):
    monkeypatch.setenv("VAR1", "value1")
    monkeypatch.setenv("VAR2", "value2")
    # Should not raise
    env_var.check(["VAR1", "VAR2"])


def test_check_missing_vars(monkeypatch):
    monkeypatch.delenv("VAR1", raising=False)
    monkeypatch.setenv("VAR2", "value2")
    with pytest.raises(RuntimeError) as excinfo:
        env_var.check(["VAR1", "VAR2"])
    assert "Missing required environment variable(s): VAR1" in str(excinfo.value)


def test_check_multiple_missing_vars(monkeypatch):
    monkeypatch.delenv("VAR1", raising=False)
    monkeypatch.delenv("VAR2", raising=False)
    with pytest.raises(RuntimeError) as excinfo:
        env_var.check(["VAR1", "VAR2"])
    assert "Missing required environment variable(s): VAR1, VAR2" in str(excinfo.value)


def test_check_empty_required_vars():
    # Should not raise if no required vars
    env_var.check([])
