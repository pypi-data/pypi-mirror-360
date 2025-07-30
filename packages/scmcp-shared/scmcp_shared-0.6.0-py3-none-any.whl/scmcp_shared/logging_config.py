import logging
import sys

from .util import get_env


def setup_logger(name="sc-mcp-server", log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    if log_file is None:
        log_file = get_env("LOG_FILE")
    if log_file:
        log_handler = logging.FileHandler(log_file)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)

        logger.info(f"logging output: {log_file}")
    else:
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.info("loggin file output: stdout")
    return logger
