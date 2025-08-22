import uuid
import time
from typing import Dict, Any, List
from django.db import transaction
from .interfaces import DataProcessorInterface, ParserInterface
from .repositories import ConversionRepository, DrugRepository
from .logger import ConversionLogger


class DataProcessor(DataProcessorInterface):
    """Main data processor following Single Responsibility Principle"""
    
    def __init__(self):
        self.conversion_repo = ConversionRepository()
        self.drug_repo = DrugRepository()
        self.logger = ConversionLogger()
    
    def process(self, conversion_id: str, source_data: str, parser: ParserInterface) -> Dict[str, Any]:
        """Process the data conversion"""
        start_time = time.time()
        
        try:
            # Log conversion start
            conversion_type = self._determine_conversion_type(parser)
            self.logger.log_conversion_start(conversion_id, conversion_type)
            
            # Update status to processing
            self.conversion_repo.update_conversion_status(conversion_id, 'PROCESSING')
            
            # Validate data
            if not parser.validate(source_data):
                raise ValueError("Invalid data format")
            
            # Parse data
            parsed_data = parser.parse(source_data)
            self.logger.log_data_processing(conversion_id, "parsing_completed", {"data_size": len(source_data)})
            
            # Extract drug and patient data
            extraction_result = parser.extract_drug_data(parsed_data)
            drug_records = extraction_result.get('drug_records', [])
            patients = extraction_result.get('patients', [])
            self.logger.log_data_processing(conversion_id, "drug_extraction_completed", {"drug_records_count": len(drug_records), "patients_count": len(patients)})
            
            # Save to database
            with transaction.atomic():
                # Save drug records (this will also create patients)
                saved_records = self.drug_repo.create_drug_records(conversion_id, extraction_result)
                
                # Update conversion status
                self.conversion_repo.update_conversion_status(
                    conversion_id, 
                    'COMPLETED',
                    converted_data={
                        'parsed_data': parsed_data,
                        'drug_records_count': len(saved_records),
                        'patients_count': len(patients),
                        'processing_time': time.time() - start_time
                    }
                )
            
            # Log completion
            duration = time.time() - start_time
            self.logger.log_conversion_complete(conversion_id, 'COMPLETED', duration)
            
            return {
                'conversion_id': conversion_id,
                'status': 'COMPLETED',
                'drug_records_count': len(saved_records),
                'patients_count': len(patients),
                'processing_time': duration,
                'parsed_data': parsed_data
            }
            
        except Exception as e:
            # Handle error
            error_message = str(e)
            duration = time.time() - start_time
            
            self.conversion_repo.update_conversion_status(
                conversion_id, 
                'FAILED', 
                error_message=error_message
            )
            
            self.logger.log_error(conversion_id, error_message)
            self.logger.log_conversion_complete(conversion_id, 'FAILED', duration)
            
            return {
                'conversion_id': conversion_id,
                'status': 'FAILED',
                'error': error_message,
                'processing_time': duration
            }
    
    def _determine_conversion_type(self, parser: ParserInterface) -> str:
        """Determine conversion type based on parser"""
        parser_name = parser.__class__.__name__.lower()
        if 'xml' in parser_name:
            return 'XML'
        elif 'hl7' in parser_name:
            return 'HL7'
        else:
            return 'UNKNOWN'


class ConversionManager:
    """High-level conversion manager following Facade Pattern"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.conversion_repo = ConversionRepository()
    
    def create_conversion(self, conversion_type: str, source_data: str) -> str:
        """Create a new conversion"""
        conversion_id = str(uuid.uuid4())
        self.conversion_repo.create_conversion(conversion_id, conversion_type, source_data)
        return conversion_id
    
    def process_conversion(self, conversion_id: str, parser) -> Dict[str, Any]:
        """Process an existing conversion"""
        conversion = self.conversion_repo.get_conversion(conversion_id)
        return self.processor.process(conversion_id, conversion.source_data, parser)
    
    def get_conversion_status(self, conversion_id: str) -> Dict[str, Any]:
        """Get conversion status"""
        conversion = self.conversion_repo.get_conversion_by_id_safe(conversion_id)
        if not conversion:
            return {'error': 'Conversion not found'}
        
        return {
            'conversion_id': conversion.conversion_id,
            'status': conversion.status,
            'conversion_type': conversion.conversion_type,
            'created_at': conversion.created_at.isoformat(),
            'updated_at': conversion.updated_at.isoformat(),
            'drug_records_count': conversion.drug_records.count(),
            'error_message': conversion.error_message if conversion.status == 'FAILED' else None
        }