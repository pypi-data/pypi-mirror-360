import logging
from typing import NoReturn

from mooch.decorators import log_entry_exit, retry, silent

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@log_entry_exit
@retry(times=2, delay=1, fallback="Nick", fail_on_none=True)
def get_name() -> NoReturn:
    logger.info("function raises an error but returns fallback value")
    raise RuntimeError("fail")


# print(get_name())  # Should print "Nick""


@log_entry_exit
@silent(fallback=123, log_exceptions=False)
def get_age(name) -> NoReturn:
    logger.info("function raises an error but returns fallback value")
    raise RuntimeError("fail")


print(get_age("Nick"))  # Should print 123
