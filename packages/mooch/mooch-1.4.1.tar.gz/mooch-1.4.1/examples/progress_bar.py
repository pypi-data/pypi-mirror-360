import time

from mooch import ColoredProgressBar

# Basic Example
pb = ColoredProgressBar(100)
for _ in range(100):
    time.sleep(0.1)
    pb.update()

# Finish Early
pb = ColoredProgressBar(100)
for i in range(100):
    time.sleep(0.1)
    pb.update()
    if i == 50:
        pb.finish()
        break

# Delayed Start
pb = ColoredProgressBar(100, auto_start=False)
time.sleep(1)  # Simulate some work before starting
pb.start()
for _ in range(100):
    time.sleep(0.1)
    pb.update()

# Overrun Example
pb = ColoredProgressBar(5)
for _ in range(5):  # Intentionally overrun
    time.sleep(0.1)
pb.update()  # This will trigger the overrun warning
