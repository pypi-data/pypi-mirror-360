import pytest

from mooch.progress_bar.utilities import format_time, gradient_color


@pytest.mark.parametrize(
    ("progress", "expected_prefix"),
    [
        (0.0, "\033[38;2;230;90;90m"),
        (0.2, "\033[38;2;235;145;95m"),
        (0.4, "\033[38;2;240;200;100m"),
        (0.525, "\033[38;2;180;190;90m"),
        (0.65, "\033[38;2;120;180;80m"),
        (0.825, "\033[38;2;70;167;51m"),
        (1.0, "\033[38;2;19;154;21m"),
    ],
)
def test_gradient_color(progress, expected_prefix):
    result = gradient_color(progress, gradient_edge=0.4, gradient_edge2=0.65)
    assert result == expected_prefix


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0.0, "0.0s"),
        (1.23, "1.2s"),
        (9.99, "10.0s"),
        (10, "10s"),
        (59, "59s"),
        (60, "1m 0s"),
        (61, "1m 1s"),
        (3599, "59m 59s"),
        (3600, "1h 0m 0s"),
        (3661, "1h 1m 1s"),
        (7322, "2h 2m 2s"),
    ],
)
def test_format_time(seconds, expected):
    assert format_time(seconds) == expected
