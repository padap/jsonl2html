"""
jsonl2html.logger
"""
import logging
from datetime import datetime
import os
from .config import Config


def setup_logger(config: Config) -> None:
    """Setup logger with configuration as singleton"""
    logger = logging.getLogger("jsonl2html")

    # Only configure if not already configured
    if not logger.handlers:
        log_level = getattr(logging, config.logging_level.upper())
        logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

        # Console handler with configured log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler for debug logs with date-based filename
        log_dir = os.path.join(os.path.expanduser("~"),
                               ".jsonl2html",
                               "logs"
                               )

        os.makedirs(log_dir, exist_ok=True)

        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f"{date_str}.log")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
