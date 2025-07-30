def gradient_color(progress: float, gradient_edge: float = 0.4, gradient_edge2: float = 0.65) -> str:
    """Gradient: soft red → warm gold → deep green (19,154,21)."""
    if progress < gradient_edge:
        t = progress / gradient_edge
        r = round(230 + (240 - 230) * t)
        g = round(90 + (200 - 90) * t)
        b = round(90 + (100 - 90) * t)

    elif progress < gradient_edge2:
        t = (progress - gradient_edge) / (gradient_edge2 - gradient_edge)
        r = round(240 + (120 - 240) * t)
        g = round(200 + (180 - 200) * t)
        b = round(100 + (80 - 100) * t)

    else:
        t = (progress - gradient_edge2) / (1 - gradient_edge2)
        r = round(120 + (19 - 120) * t)
        g = round(180 + (154 - 180) * t)
        b = round(80 + (21 - 80) * t)

    return f"\033[38;2;{r};{g};{b}m"


def format_time(seconds: float) -> str:
    if seconds < 10:  # noqa: PLR2004
        return f"{seconds:.1f}s"
    seconds = round(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)

    if hours:
        return f"{hours}h {mins}m {secs}s"
    if mins:
        return f"{mins}m {secs}s"
    return f"{secs}s"
