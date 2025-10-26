"""
Logging configuration.
"""
import logging
from config.config import LOG_CONFIG


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with consistent configuration."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(LOG_CONFIG["level"])
        
        # File handler
        fh = logging.FileHandler(LOG_CONFIG["file"])
        fh.setLevel(LOG_CONFIG["level"])
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(LOG_CONFIG["level"])
        
        # Formatter
        formatter = logging.Formatter(LOG_CONFIG["format"])
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger