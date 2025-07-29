import pytest

from mooch.validators import python_version


@pytest.mark.parametrize(
    ("required", "actual", "should_raise"),
    [
        ("3.8", "3.8", False),
        ("3.7", "3.8", False),
        ("3.8", "3.7", True),
        ("3.9", "3.8", True),
        ("2.7", "3.8", False),
        ("3.8", "3.9", False),
        ("3.8", "2.7", True),
        ("4.0", "3.8", True),
        ("3.13", "3.13", False),
    ],
)
def test_python_version(monkeypatch, required, actual, should_raise):
    monkeypatch.setattr("platform.python_version", lambda: actual)
    if should_raise:
        with pytest.raises(RuntimeError) as excinfo:
            python_version.check(required)
        assert f"Python {required}+ required." in str(excinfo.value)
    else:
        python_version.check(required)
