"""
NCD INAI - Logging Configuration
Centralized logging setup for production environments
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_colors: bool = True
) -> None:
    """
    Setup application-wide logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs only to console
        enable_colors: Enable colored output for console (default: True)
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if logging to file
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    if enable_colors:
        console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        console_formatter = logging.Formatter(log_format, datefmt=date_format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        
        # File logs don't need colors
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Logging configured - Level: {log_level}")
    if log_file:
        logger.info(f"📁 Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Pre-configured loggers for common modules
app_logger = get_logger("ncd_inai.app")
db_logger = get_logger("ncd_inai.database")
storage_logger = get_logger("ncd_inai.storage")
ai_logger = get_logger("ncd_inai.ai")
api_logger = get_logger("ncd_inai.api")
