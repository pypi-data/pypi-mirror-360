import time

from mooch import ProgressBar

if __name__ == "__main__":
    pb = ProgressBar(
        total=5,
        prefix="Progress",
    )

    for _ in range(5):
        time.sleep(0.1)
        pb.update()
