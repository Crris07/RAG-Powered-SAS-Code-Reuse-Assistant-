"""Logging configuration for SAS RAG Assistant"""

import logging
import logging.handlers
from pathlib import Path

from src.core.config import get_config

# Create logs directory
LOGS_DIR = Path("./logs")
LOGS_DIR.mkdir(exist_ok=True)


def setup_logging():
    """Configure logging for the application"""
    config = get_config()

    # Get logger
    logger = logging.getLogger("sas_rag")
    logger.setLevel(config.log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.log_level)

    # File handler
    log_file = LOGS_DIR / "app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(config.log_level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(f"sas_rag.{name}")
