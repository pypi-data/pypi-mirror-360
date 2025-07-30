from __future__ import annotations

import sys
import time

from .utilities import format_time


class ProgressBar:
    """Progress bar with optional color gradient, ETA, percentage, and step display.

    Args:
        total (int): The total number of steps for completion.
        width (int, optional): The width of the progress bar in characters. Default is 50.
        prefix (str, optional): String to display before the progress bar. Default is "".
        suffix (str, optional): String to display after the progress bar. Default is "".
        symbol (str, optional): Character used to fill the progress bar. Default is "█".

    Methods:
        update(step: int = 1) -> None:
            Increment the progress bar by the given number of steps and render the update.

        finish() -> None:
            Set current step to last and render the final state of the progress bar.

    """

    def __init__(
        self,
        total: int,
        *,
        width: int = 50,
        prefix: str = "Progress ",
        suffix: str = "",
        symbol: str = "█",
    ):
        self.total: int = total
        self.width: int = width
        self.prefix: str = prefix
        self.suffix: str = suffix
        self.symbol: str = symbol
        self.empty_symbol: str = " "
        self._stream = sys.stdout
        self._last_line_len = 0
        self._start_time = None
        self._finish_time = None

        # Variable Data
        self.current_step: int = 0
        self.elapsed_seconds: float = 0.0
        self.progress: float = 0.0
        self.remaining_seconds: float = 0.0
        self.remaining_steps: int = 0

        self.start()

    def start(self) -> None:
        if self._start_time is not None:
            msg = "Progress bar has already been started."
            raise RuntimeError(msg)

        self._start_time = time.time()
        self._stream.write("\033[?25l")  # Hide terminal cursor
        self._stream.flush()
        self._render()

    def update(self, stepsize: int = 1) -> None:
        if self._start_time is None:
            msg = "Progress bar has not been started yet."
            raise RuntimeError(msg)
        if self._finish_time is not None:
            self.current_step += stepsize
            self.elapsed_seconds = time.time() - self._start_time
            self._render_overrun()
            return

        self.current_step += stepsize
        self.elapsed_seconds = time.time() - self._start_time
        self.progress = min(self.current_step / self.total, 1.0)
        self.remaining_steps = self.total - self.current_step
        self.remaining_seconds = float(self.elapsed_seconds / self.current_step * self.remaining_steps)

        if self.current_step >= self.total:
            self.finish()
            return

        self._render()

    def finish(self) -> None:
        self.current_step = self.total
        self._render()
        self._finish_time = time.time()
        self._last_line_len = 0
        self._stream.write("\n")
        self._stream.flush()

    def _render(self) -> None:
        bar = self._generate_bar()
        percentage = self._generate_percentage()
        steps_status = self._generate_steps_status()
        eta = self._generate_eta()

        line = f"\r{self.prefix}[{bar}] {percentage}{steps_status}{eta}{self.suffix}"
        line = line.ljust(self._last_line_len)
        self._last_line_len = len(line)
        self._stream.write(line)
        self._stream.flush()

    def _render_overrun(self) -> None:
        line = f"\rWarning: Progress bar overrun. Current Step: {self.current_step} of {self.total}."
        line = line.ljust(self._last_line_len)
        self._last_line_len = len(line)
        self._stream.write(line)
        self._stream.flush()

    def _generate_bar(self) -> str:
        filled_length = int(self.width * self.progress)
        empty_length = self.width - filled_length
        return self.symbol * filled_length + self.empty_symbol * empty_length

    def _generate_percentage(self) -> str:
        return f" {int(self.progress * 100):3d}%"

    def _generate_steps_status(self) -> str:
        return f" {str(self.current_step).rjust(len(str(self.total)))}/{self.total}"

    def _generate_eta(self) -> str:
        if self.current_step > 0:
            return f" ETA {format_time(self.remaining_seconds)}"
        return " ETA N/A"
