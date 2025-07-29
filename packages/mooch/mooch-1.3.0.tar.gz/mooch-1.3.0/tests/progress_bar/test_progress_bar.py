import re
import time

from mooch.progress_bar.progress_bar import ProgressBar


def test_progress_bar_basic_update_and_done(capsys):
    pb = ProgressBar(total=5, width=10, enable_color=False, hide_cursor=False)
    for _ in range(5):
        pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "100%" in last_line
    assert "5/5" in last_line


def test_progress_bar_basic_update_partial(capsys):
    pb = ProgressBar(total=5, width=10, enable_color=False, hide_cursor=False)
    for _ in range(4):
        pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "80%" in last_line
    assert "4/5" in last_line


def test_progress_bar_prefix_suffix(capsys):
    pb = ProgressBar(total=3, prefix="Start", suffix="End", enable_color=False, hide_cursor=False)
    pb.update()
    pb.done()
    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "Start" in last_line
    assert "End" in last_line


def test_progress_bar_eta_true(capsys):
    pb = ProgressBar(total=2, show_eta=True, enable_color=False, hide_cursor=False)
    pb.update()
    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line


def test_progress_bar_eta_false(capsys):
    pb = ProgressBar(total=2, show_eta=False, enable_color=False, hide_cursor=False)
    pb.update()
    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" not in last_line


def test_progress_bar_color_true(capsys):
    pb = ProgressBar(total=10, enable_color=True, hide_cursor=False)
    for _ in range(10):
        pb.update()
    output, _ = capsys.readouterr()
    assert "\033[38;2;" in output or "\033[0m" in output


def test_progress_bar_color_false(capsys):
    pb = ProgressBar(total=10, enable_color=False, hide_cursor=False)
    for _ in range(10):
        pb.update()
    output, _ = capsys.readouterr()
    assert "\033[38;2;" not in output
    assert "\033[0m" not in output


def test_progress_bar_multiple_steps(capsys):
    pb = ProgressBar(total=10, width=10, enable_color=False, hide_cursor=False)
    pb.update(3)
    pb.update(2)
    pb.update(5)
    output, _ = capsys.readouterr()
    assert "10/10" in output
    assert "100%" in output


def test_progress_bar_eta_time_hours(capsys):
    pb = ProgressBar(total=9001, show_eta=True, enable_color=False, hide_cursor=False)
    time.sleep(1)
    pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line
    assert re.search(r"\b2h \d+m \d+s\b", last_line)


def test_progress_bar_eta_time_mins(capsys):
    pb = ProgressBar(total=90, show_eta=True, enable_color=False, hide_cursor=False)
    time.sleep(1)
    pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line
    assert re.search(r"\b1m \d+s\b", last_line)


def test_progress_bar_eta_time_secs(capsys):
    pb = ProgressBar(total=45, show_eta=True, enable_color=False, hide_cursor=False)
    time.sleep(1)
    pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line
    assert re.search(r"\b\d+s\b", last_line)


def test_progress_bar_eta_time_less_than_ten_secs(capsys):
    pb = ProgressBar(total=5, show_eta=True, enable_color=False, hide_cursor=False)
    time.sleep(0.7)
    pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line
    assert re.search(r"\b\d+\.\d{1}s\b", last_line)
