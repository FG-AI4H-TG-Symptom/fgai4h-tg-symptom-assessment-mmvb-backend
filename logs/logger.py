import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s ] [%(levelname)-5.5s]  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger():
    return logging.getLogger()
