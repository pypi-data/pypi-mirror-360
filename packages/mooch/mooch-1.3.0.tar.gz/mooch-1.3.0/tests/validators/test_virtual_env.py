import sys

import pytest

from mooch.validators.virtual_env import check


def test_check_virtualenv_real_prefix(monkeypatch):
    # Simulate sys.real_prefix exists (old virtualenv)
    monkeypatch.setattr(sys, "real_prefix", "/some/path", raising=False)
    # base_prefix and prefix should not matter in this case
    check()  # Should not raise


def test_check_virtualenv_base_prefix_diff(monkeypatch):
    # Simulate sys.base_prefix != sys.prefix (venv)
    monkeypatch.setattr(sys, "base_prefix", "/base", raising=False)
    monkeypatch.setattr(sys, "prefix", "/venv", raising=False)
    # Remove real_prefix if present
    if hasattr(sys, "real_prefix"):
        monkeypatch.delattr(sys, "real_prefix", raising=False)
    check()  # Should not raise


def test_check_virtualenv_not_activated(monkeypatch):
    # Simulate no real_prefix and base_prefix == prefix
    if hasattr(sys, "real_prefix"):
        monkeypatch.delattr(sys, "real_prefix", raising=False)
    monkeypatch.setattr(sys, "base_prefix", "/same", raising=False)
    monkeypatch.setattr(sys, "prefix", "/same", raising=False)
    with pytest.raises(RuntimeError, match="Virtual environment is not activated."):
        check()
