import logging

from mooch.decorators.logging import log_entry_exit

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@log_entry_exit
def random_function(arg1, arg2):
    print(arg1)
    print(arg2)


if __name__ == "__main__":
    random_function("Hello", "World")
