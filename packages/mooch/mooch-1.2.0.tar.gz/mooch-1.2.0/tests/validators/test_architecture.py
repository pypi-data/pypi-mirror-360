import pytest

from mooch.validators import architecture


def test_architecture_allowed(monkeypatch):
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    architecture.check(["x86_64", "arm64"])  # Should not raise


def test_architecture_blocked(monkeypatch):
    monkeypatch.setattr("platform.machine", lambda: "i386")
    with pytest.raises(RuntimeError, match="Allowed architecture"):
        architecture.check(["x86_64", "arm64"])
