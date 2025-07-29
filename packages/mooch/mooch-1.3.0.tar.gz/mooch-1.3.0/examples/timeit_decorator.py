import logging
import time

from mooch.decorators import timeit

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@timeit
def random_function(arg1, arg2):
    print(arg1)
    print(arg2)
    time.sleep(1.5)


if __name__ == "__main__":
    random_function("Hello", "World")
