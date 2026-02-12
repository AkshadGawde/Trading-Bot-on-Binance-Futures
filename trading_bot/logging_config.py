"""
Centralized logging configuration module.
Provides consistent logging across the application with both file and console output.
"""

import logging
import os
from datetime import datetime
from trading_bot.config import LOG_DIR, LOG_FORMAT, LOG_DATE_FORMAT


class LoggerManager:
    """Manages centralized logging configuration for the application."""
    
    _logger = None
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger instance with consistent configuration.
        
        Args:
            name: Logger name (typically __name__ from calling module)
            
        Returns:
            Configured logger instance
        """
        if cls._logger is None:
            cls._logger = cls._setup_logger(name)
        return cls._logger
    
    @classmethod
    def _setup_logger(cls, name: str) -> logging.Logger:
        """
        Set up logger with file and console handlers.
        
        Args:
            name: Logger name
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler - INFO level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler - DEBUG level
        log_filename = os.path.join(
            LOG_DIR,
            f"trading_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return LoggerManager.get_logger(name)
