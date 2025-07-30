from __future__ import annotations

from mooch.progress_bar.progress_bar import ProgressBar
from mooch.progress_bar.utilities import gradient_color


class ColoredProgressBar(ProgressBar):
    RESET_COLOR = "\033[0m"

    def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
        super().__init__(*args, **kwargs)

    def _generate_bar(self) -> str:
        filled_length = int(self.width * self.progress)
        empty_length = self.width - filled_length
        bar_blocks = []
        for i in range(filled_length):
            progress_pos = i / self.width
            color = gradient_color(progress_pos)
            bar_blocks.append(f"{color}{self.symbol}")

        return "".join(bar_blocks) + self.RESET_COLOR + self.empty_symbol * empty_length

    def _generate_percentage(self) -> str:
        color = gradient_color(self.progress)
        return f"{color}{int(self.progress * 100):3d}%{self.RESET_COLOR}"
