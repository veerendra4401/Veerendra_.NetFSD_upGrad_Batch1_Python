"""
logger.py - Centralized Logging Module
Automated ITIL Service Desk System
Provides structured logging with INFO, WARNING, ERROR, CRITICAL levels.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "data")
LOG_FILE = os.path.join(LOG_DIR, "logs.txt")
MAX_BYTES = 5 * 1024 * 1024   # 5 MB
BACKUP_COUNT = 3


class ITILFormatter(logging.Formatter):
    """Custom formatter that prefixes log level with an ITIL-friendly tag."""

    LEVEL_TAGS = {
        logging.DEBUG:    "[DEBUG]   ",
        logging.INFO:     "[INFO]    ",
        logging.WARNING:  "[WARNING] ",
        logging.ERROR:    "[ERROR]   ",
        logging.CRITICAL: "[CRITICAL]",
    }

    def format(self, record: logging.LogRecord) -> str:
        tag = self.LEVEL_TAGS.get(record.levelno, "[LOG]     ")
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        message = super().format(record)
        return f"{timestamp} {tag} {record.name} | {record.getMessage()}"


def get_logger(name: str = "ITIL-ServiceDesk") -> logging.Logger:
    """
    Return a configured logger instance.
    Creates log directory/file if they don't exist.
    Uses RotatingFileHandler so logs don't grow unbounded.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = ITILFormatter()

    # ── File Handler (rotating) ──────────────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # ── Console Handler ──────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Module-level default logger
log = get_logger()
