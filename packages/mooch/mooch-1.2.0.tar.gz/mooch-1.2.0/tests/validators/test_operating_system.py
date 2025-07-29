import pytest

from mooch.validators import operating_system


@pytest.mark.parametrize(
    ("required_systems", "platform_sys", "should_raise"),
    [
        (["Windows"], "Windows", False),
        (["windows"], "Windows", False),
        (["Linux"], "linux", False),
        (["Windows"], "linux", True),
        (["Darwin"], "darwin", False),
        ([""], "Windows", True),
    ],
)
def test_windows_os_platform(monkeypatch, required_systems, platform_sys, should_raise):
    monkeypatch.setattr("platform.system", lambda: platform_sys)
    required_systems = [os.lower() for os in required_systems]
    platform_sys = platform_sys.lower()

    if should_raise:
        with pytest.raises(RuntimeError) as excinfo:
            operating_system.check(required_systems)
        assert f"Allowed OS: {required_systems}. Detected: {platform_sys}" in str(excinfo.value)
        assert platform_sys in str(excinfo.value)
    else:
        operating_system.check(required_systems)
