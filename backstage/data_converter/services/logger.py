import logging
import time
from datetime import datetime
from typing import Dict, Any
from .interfaces import ConversionLoggerInterface


class ConversionLogger(ConversionLoggerInterface):
    """Logger implementation for conversion tracking following Single Responsibility Principle"""
    
    def __init__(self):
        self.logger = logging.getLogger('data_converter')
    
    def log_conversion_start(self, conversion_id: str, conversion_type: str) -> None:
        """Log conversion start"""
        self.logger.info(f"Conversion started: {conversion_id} ({conversion_type})")
    
    def log_conversion_complete(self, conversion_id: str, status: str, duration: float) -> None:
        """Log conversion completion"""
        self.logger.info(f"Conversion completed: {conversion_id} ({status}) - Duration: {duration:.2f}s")
    
    def log_error(self, conversion_id: str, error_message: str) -> None:
        """Log conversion error"""
        self.logger.error(f"Conversion error: {conversion_id} - {error_message}")
    
    def log_validation_error(self, conversion_id: str, validation_errors: list) -> None:
        """Log validation errors"""
        for error in validation_errors:
            self.logger.warning(f"Validation error for {conversion_id}: {error}")
    
    def log_data_processing(self, conversion_id: str, step: str, details: Dict[str, Any] = None) -> None:
        """Log data processing steps"""
        message = f"Data processing: {conversion_id} - {step}"
        if details:
            message += f" - {details}"
        self.logger.debug(message)