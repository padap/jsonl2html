"""
jsonl2html.logger
"""
import logging
from .config import Config


def setup_logger(config: Config) -> None:
    """Setup logger with configuration as singleton"""
    logger = logging.getLogger("jsonl2html")

    # Only configure if not already configured
    if not logger.handlers:
        log_level = getattr(logging, config.logging_level.upper())
        logger.setLevel(log_level)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
