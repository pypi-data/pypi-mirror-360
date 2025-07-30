import time

from mooch import ColoredProgressBar

if __name__ == "__main__":
    pb = ColoredProgressBar(
        total=5,
    )

    for _ in range(88):
        time.sleep(0.5)
        pb.update()
