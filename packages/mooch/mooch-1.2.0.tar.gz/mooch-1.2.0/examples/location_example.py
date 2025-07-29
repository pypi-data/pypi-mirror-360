import logging

from mooch.location.location import Location

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    logger.debug("Starting location example...")
    location = Location(90210).load()

    print(location.city)


if __name__ == "__main__":
    main()
