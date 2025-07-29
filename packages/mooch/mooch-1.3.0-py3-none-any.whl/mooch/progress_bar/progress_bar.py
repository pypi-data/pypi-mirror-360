from __future__ import annotations

import atexit
import sys
import time


class ProgressBar:
    """Progress bar with optional color gradient, ETA, percentage, and step display.

    Args:
        total (int): The total number of steps for completion.
        width (int, optional): The width of the progress bar in characters. Default is 50.
        prefix (str, optional): String to display before the progress bar. Default is "".
        suffix (str, optional): String to display after the progress bar. Default is "".
        show_percent (bool, optional): Whether to display the percentage completed. Default is True.
        show_steps (bool, optional): Whether to display the current step and total steps. Default is True.
        show_eta (bool, optional): Whether to display the estimated time remaining. Default is True.
        enable_color (bool, optional): Whether to enable color gradient in the progress bar. Default is True.
        hide_cursor (bool, optional): Whether to hide the cursor while the progress bar is active. Default is True.

    Methods:
        update(step: int = 1) -> None:
            Increment the progress bar by the given number of steps and render the update.

        done() -> None:
            Mark the progress as complete and render the final state.

    """

    def __init__(  # noqa: PLR0913
        self,
        total: int,
        *,
        width: int = 50,
        prefix: str = "",
        suffix: str = "",
        show_percent: bool = True,
        show_steps: bool = True,
        show_eta: bool = True,
        enable_color: bool = True,
        hide_cursor: bool = True,
    ):
        self.total = total
        self.width = width
        self.prefix: str = prefix
        self.suffix: str = suffix
        self.show_percent: bool = show_percent
        self.show_steps: bool = show_steps
        self.show_eta: bool = show_eta
        self.enable_color: bool = enable_color

        self._stream = sys.stdout
        self.hide_cursor = hide_cursor
        self._symbol: str = "█"
        self._empty_symbol: str = " "
        self._start_time = time.time()
        self._current = 0
        self._reset_color = "\033[0m" if self.enable_color else ""
        self._last_line_len = 0

        self._hide_cursor()
        atexit.register(self._show_cursor)

    def _hide_cursor(self) -> None:
        if not self.hide_cursor or self._stream.closed:
            return

        self._stream.write("\033[?25l")
        self._stream.flush()

    def _show_cursor(self) -> None:
        if not self.hide_cursor or self._stream.closed:
            return
        self._stream.write("\033[?25h")
        self._stream.flush()

    def update(self, step: int = 1) -> None:
        self._current += step
        self._render()

    def _render(self) -> None:
        now = time.time()
        elapsed = now - self._start_time
        progress = min(self._current / self.total, 1.0)
        filled = int(self.width * progress)
        empty = self.width - filled

        if self.enable_color:
            bar_blocks = []
            for i in range(filled):
                progress_pos = i / self.width
                color = self._get_color(progress_pos)
                bar_blocks.append(f"{color}{self._symbol}")
            bar = "".join(bar_blocks) + self._reset_color + self._empty_symbol * empty
        else:
            bar = self._symbol * filled + self._empty_symbol * empty

        percent = f" {int(progress * 100):3d}%" if self.show_percent else ""
        steps = f" {str(self._current).rjust(len(str(self.total)))}/{self.total}" if self.show_steps else ""

        eta = ""
        if self.show_eta and self._current > 0:
            rate = elapsed / self._current
            remaining = self.total - self._current
            eta_seconds = float(rate * remaining)
            eta = f" ETA {self._format_time(eta_seconds)}"

        line = f"\r{self.prefix} [{bar}]{percent}{steps}{eta} {self.suffix}"

        visible_line = line.ljust(self._last_line_len)
        self._last_line_len = len(line)  # update for next time

        self._stream.write(visible_line)
        self._stream.flush()

        if self._current >= self.total:
            self._stream.write("\n")
            self._stream.flush()
            self._show_cursor()  # Show cursor on completion

    def done(self) -> None:
        self._current = self.total
        self._render()

    def _format_time(self, seconds: float) -> str:
        if seconds < 10:
            return f"{seconds:.1f}s"
        seconds = round(seconds)
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)

        if hours:
            return f"{hours}h {mins}m {secs}s"
        if mins:
            return f"{mins}m {secs}s"
        return f"{secs}s"

    def _get_color(self, progress: float) -> str:
        """Gradient: soft red → warm gold → deep green (19,154,21)."""
        if progress < 0.4:  # noqa: PLR2004
            t = progress / 0.4
            r = round(230 + (240 - 230) * t)
            g = round(90 + (200 - 90) * t)
            b = round(90 + (100 - 90) * t)

        elif progress < 0.65:  # noqa: PLR2004
            t = (progress - 0.4) / 0.25
            r = round(240 + (120 - 240) * t)
            g = round(200 + (180 - 200) * t)
            b = round(100 + (80 - 100) * t)

        else:
            t = (progress - 0.65) / 0.35
            r = round(120 + (19 - 120) * t)
            g = round(180 + (154 - 180) * t)
            b = round(80 + (21 - 80) * t)

        return f"\033[38;2;{r};{g};{b}m"
