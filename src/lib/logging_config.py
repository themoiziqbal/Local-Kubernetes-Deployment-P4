"""Logging configuration for the chatbot application."""

import logging
import os
from datetime import datetime


def setup_logging(log_level: str = 'INFO', log_file: str = 'logs/chatbot.log'):
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Set up root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler
            logging.FileHandler(log_file, mode='a', encoding='utf-8')
        ]
    )

    # Create logger for application
    logger = logging.getLogger('chatbot')
    logger.info('Logging initialized')

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name

    Returns:
        Logger instance
    """
    return logging.getLogger(f'chatbot.{name}')
