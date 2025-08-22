from abc import ABC, abstractmethod
from typing import Dict, Any, List
import uuid
from datetime import datetime


class ParserInterface(ABC):
    """Abstract base class for data parsers following Interface Segregation Principle"""
    
    @abstractmethod
    def parse(self, data: str) -> Dict[str, Any]:
        """Parse the input data and return structured format"""
        pass
    
    @abstractmethod
    def validate(self, data: str) -> bool:
        """Validate the input data format"""
        pass


class DataProcessorInterface(ABC):
    """Abstract base class for data processors"""
    
    @abstractmethod
    def process(self, conversion_id: str, source_data: str, parser: ParserInterface) -> Dict[str, Any]:
        """Process the data conversion"""
        pass


class ConversionRepositoryInterface(ABC):
    """Abstract base class for conversion repository"""
    
    @abstractmethod
    def create_conversion(self, conversion_id: str, conversion_type: str, source_data: str) -> Any:
        """Create a new conversion record"""
        pass
    
    @abstractmethod
    def update_conversion_status(self, conversion_id: str, status: str, converted_data: Dict = None, error_message: str = None) -> None:
        """Update conversion status"""
        pass
    
    @abstractmethod
    def get_conversion(self, conversion_id: str) -> Any:
        """Get conversion by ID"""
        pass


class DrugRepositoryInterface(ABC):
    """Abstract base class for drug repository"""
    
    @abstractmethod
    def create_drug_records(self, conversion_id: str, drug_data: List[Dict[str, Any]]) -> List[Any]:
        """Create drug records from parsed data"""
        pass


class ConversionLoggerInterface(ABC):
    """Abstract base class for conversion logging"""
    
    @abstractmethod
    def log_conversion_start(self, conversion_id: str, conversion_type: str) -> None:
        """Log conversion start"""
        pass
    
    @abstractmethod
    def log_conversion_complete(self, conversion_id: str, status: str, duration: float) -> None:
        """Log conversion completion"""
        pass
    
    @abstractmethod
    def log_error(self, conversion_id: str, error_message: str) -> None:
        """Log conversion error"""
        pass