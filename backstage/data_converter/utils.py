from typing import List, Dict, Any
from django.core.exceptions import ValidationError


class DataValidator:
    """Data validation utilities following Single Responsibility Principle"""
    
    @staticmethod
    def validate_xml_data(data: str) -> List[str]:
        """Validate XML data format"""
        errors = []
        
        if not data or not data.strip():
            errors.append("XML data cannot be empty")
            return errors
        
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(data)
        except ET.ParseError as e:
            errors.append(f"Invalid XML format: {str(e)}")
        except Exception as e:
            errors.append(f"XML parsing error: {str(e)}")
        
        return errors
    
    @staticmethod
    def validate_hl7_data(data: str) -> List[str]:
        """Validate HL7 data format"""
        errors = []
        
        if not data or not data.strip():
            errors.append("HL7 data cannot be empty")
            return errors
        
        lines = [line.strip() for line in data.split('\r|\n') if line.strip()]
        
        if not lines:
            errors.append("HL7 data must contain at least one segment")
            return errors
        
        # Check for MSH segment (required in HL7 messages)
        if not lines[0].startswith('MSH'):
            errors.append("HL7 message must start with MSH segment")
        
        # Validate segment structure
        for i, line in enumerate(lines):
            if '|' not in line:
                errors.append(f"Segment {i+1} must contain field separators (|)")
        
        return errors
    
    @staticmethod
    def validate_conversion_data(conversion_type: str, source_data: str) -> List[str]:
        """Validate conversion data based on type"""
        if conversion_type.upper() == 'XML':
            return DataValidator.validate_xml_data(source_data)
        elif conversion_type.upper() == 'HL7':
            return DataValidator.validate_hl7_data(source_data)
        else:
            return [f"Unsupported conversion type: {conversion_type}"]
    
    @staticmethod
    def validate_drug_record(drug_data: Dict[str, Any]) -> List[str]:
        """Validate drug record data"""
        errors = []
        
        if not drug_data.get('drug_name'):
            errors.append("Drug name is required")
        
        if drug_data.get('quantity') is not None:
            try:
                quantity = int(drug_data['quantity'])
                if quantity < 0:
                    errors.append("Quantity must be non-negative")
            except (ValueError, TypeError):
                errors.append("Quantity must be a valid integer")
        
        return errors


class ConversionErrorHandler:
    """Error handling utilities for conversion operations"""
    
    @staticmethod
    def handle_validation_error(conversion_id: str, errors: List[str]) -> Dict[str, Any]:
        """Handle validation errors"""
        return {
            'conversion_id': conversion_id,
            'status': 'FAILED',
            'error': 'Validation failed',
            'validation_errors': errors,
            'error_code': 'VALIDATION_ERROR'
        }
    
    @staticmethod
    def handle_parsing_error(conversion_id: str, error_message: str) -> Dict[str, Any]:
        """Handle parsing errors"""
        return {
            'conversion_id': conversion_id,
            'status': 'FAILED',
            'error': 'Parsing failed',
            'error_message': error_message,
            'error_code': 'PARSING_ERROR'
        }
    
    @staticmethod
    def handle_database_error(conversion_id: str, error_message: str) -> Dict[str, Any]:
        """Handle database errors"""
        return {
            'conversion_id': conversion_id,
            'status': 'FAILED',
            'error': 'Database operation failed',
            'error_message': error_message,
            'error_code': 'DATABASE_ERROR'
        }
    
    @staticmethod
    def handle_general_error(conversion_id: str, error_message: str) -> Dict[str, Any]:
        """Handle general errors"""
        return {
            'conversion_id': conversion_id,
            'status': 'FAILED',
            'error': 'General error',
            'error_message': error_message,
            'error_code': 'GENERAL_ERROR'
        }


class ConversionResponseFormatter:
    """Response formatting utilities"""
    
    @staticmethod
    def format_success_response(conversion_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format success response"""
        return {
            'success': True,
            'conversion_id': conversion_id,
            'data': data,
            'timestamp': data.get('processing_time', 0)
        }
    
    @staticmethod
    def format_error_response(conversion_id: str, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format error response"""
        return {
            'success': False,
            'conversion_id': conversion_id,
            'error': error_data,
            'timestamp': error_data.get('processing_time', 0)
        }
    
    @staticmethod
    def format_list_response(conversions: List[Dict[str, Any]], total_count: int) -> Dict[str, Any]:
        """Format list response"""
        return {
            'success': True,
            'conversions': conversions,
            'total_count': total_count,
            'timestamp': len(conversions)
        }