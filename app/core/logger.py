"""
Custom logging configuration for the application.
Ensures consistent log formatting across all agents and services.
"""
import logging
import sys
from app.core.config import settings

def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a configured logger instance.

    Args:
        name (str): The name of the logger, typically __name__.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Prevent adding multiple handlers if logger already attached
    if logger.hasHandlers():
        return logger
    
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger