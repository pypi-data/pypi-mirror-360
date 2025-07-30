"""Logging configuration for the sentence completion program."""
import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler

def setup_logger(log_file: Optional[str] = None) -> logging.Logger:
    """Set up and configure the logger.
    
    Args:
        log_file: Optional path to log file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("sentence_completion")
    logger.setLevel(logging.INFO)
    
    # Create formatters
    console_formatter = logging.Formatter(
        "%(message)s",
        datefmt="[%X]"
    )
    
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Add rich console handler
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    return logger

# Create default logger
logger = setup_logger() 