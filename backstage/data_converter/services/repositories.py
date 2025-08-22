import uuid
from datetime import datetime
from typing import Dict, Any, List
from django.db import transaction
from ..models import DataConversion, DrugRecord, Patient
from .interfaces import ConversionRepositoryInterface, DrugRepositoryInterface


class ConversionRepository(ConversionRepositoryInterface):
    """Repository implementation for data conversions following Repository Pattern"""
    
    def create_conversion(self, conversion_id: str, conversion_type: str, source_data: str) -> DataConversion:
        """Create a new conversion record"""
        return DataConversion.objects.create(
            conversion_id=conversion_id,
            conversion_type=conversion_type,
            source_data=source_data,
            status='PENDING'
        )
    
    def update_conversion_status(self, conversion_id: str, status: str, 
                                converted_data: Dict = None, error_message: str = None) -> None:
        """Update conversion status"""
        conversion = DataConversion.objects.get(conversion_id=conversion_id)
        conversion.status = status
        
        if converted_data:
            conversion.converted_data = converted_data
        
        if error_message:
            conversion.error_message = error_message
        
        conversion.save()
    
    def get_conversion(self, conversion_id: str) -> DataConversion:
        """Get conversion by ID"""
        return DataConversion.objects.get(conversion_id=conversion_id)
    
    def get_conversion_by_id_safe(self, conversion_id: str) -> DataConversion:
        """Get conversion by ID safely (returns None if not found)"""
        try:
            return DataConversion.objects.get(conversion_id=conversion_id)
        except DataConversion.DoesNotExist:
            return None


class PatientRepository:
    """Repository implementation for patient records following Repository Pattern"""
    
    def get_or_create_patient(self, patient_data: Dict[str, Any]) -> Patient:
        """Get existing patient or create new one"""
        patient_id = patient_data.get('patient_id', '')
        
        if not patient_id:
            return None
        
        # Try to get existing patient
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            # Update existing patient with new data
            self._update_patient_data(patient, patient_data)
            return patient
        except Patient.DoesNotExist:
            # Create new patient
            return self._create_patient(patient_data)
    
    def _create_patient(self, patient_data: Dict[str, Any]) -> Patient:
        """Create a new patient record"""
        return Patient.objects.create(
            patient_id=patient_data.get('patient_id', ''),
            first_name=patient_data.get('first_name', ''),
            last_name=patient_data.get('last_name', ''),
            full_name=patient_data.get('full_name', ''),
            age=patient_data.get('age'),
            gender=patient_data.get('gender', ''),
            date_of_birth=patient_data.get('date_of_birth'),
            address=patient_data.get('address', ''),
            phone_number=patient_data.get('phone_number', ''),
            metadata=patient_data.get('metadata', {})
        )
    
    def _update_patient_data(self, patient: Patient, patient_data: Dict[str, Any]):
        """Update existing patient data"""
        update_fields = []
        
        if patient_data.get('first_name') and patient.first_name != patient_data.get('first_name'):
            patient.first_name = patient_data.get('first_name')
            update_fields.append('first_name')
        
        if patient_data.get('last_name') and patient.last_name != patient_data.get('last_name'):
            patient.last_name = patient_data.get('last_name')
            update_fields.append('last_name')
        
        if patient_data.get('full_name') and patient.full_name != patient_data.get('full_name'):
            patient.full_name = patient_data.get('full_name')
            update_fields.append('full_name')
        
        if patient_data.get('age') is not None and patient.age != patient_data.get('age'):
            patient.age = patient_data.get('age')
            update_fields.append('age')
        
        if patient_data.get('gender') and patient.gender != patient_data.get('gender'):
            patient.gender = patient_data.get('gender')
            update_fields.append('gender')
        
        if patient_data.get('date_of_birth') and patient.date_of_birth != patient_data.get('date_of_birth'):
            patient.date_of_birth = patient_data.get('date_of_birth')
            update_fields.append('date_of_birth')
        
        if patient_data.get('address') and patient.address != patient_data.get('address'):
            patient.address = patient_data.get('address')
            update_fields.append('address')
        
        if patient_data.get('phone_number') and patient.phone_number != patient_data.get('phone_number'):
            patient.phone_number = patient_data.get('phone_number')
            update_fields.append('phone_number')
        
        if update_fields:
            patient.save(update_fields=update_fields)
    
    def get_patient_by_id(self, patient_id: str) -> Patient:
        """Get patient by ID"""
        try:
            return Patient.objects.get(patient_id=patient_id)
        except Patient.DoesNotExist:
            return None


class DrugRepository(DrugRepositoryInterface):
    """Repository implementation for drug records following Repository Pattern"""
    
    def __init__(self):
        self.patient_repo = PatientRepository()
    
    @transaction.atomic
    def create_drug_records(self, conversion_id: str, extraction_result: Dict[str, Any]) -> List[DrugRecord]:
        """Create drug records from parsed data"""
        conversion = DataConversion.objects.get(conversion_id=conversion_id)
        drug_records = []
        
        # Create patients first
        patients = {}
        for patient_data in extraction_result.get('patients', []):
            patient = self.patient_repo.get_or_create_patient(patient_data)
            if patient:
                patients[patient.patient_id] = patient
        
        # Create drug records
        for drug_info in extraction_result.get('drug_records', []):
            patient = patients.get(drug_info.get('patient_id', ''))
            
            drug_record = DrugRecord.objects.create(
                conversion=conversion,
                patient=patient,
                drug_name=drug_info.get('drug_name', ''),
                dosage=drug_info.get('dosage', ''),
                strength=drug_info.get('strength', ''),
                quantity=drug_info.get('quantity'),
                original_patient_id=drug_info.get('patient_id', ''),
                prescription_id=drug_info.get('prescription_id', ''),
                metadata=drug_info.get('metadata', {})
            )
            drug_records.append(drug_record)
        
        return drug_records
    
    def get_drug_records_by_conversion(self, conversion_id: str) -> List[DrugRecord]:
        """Get all drug records for a conversion"""
        return DrugRecord.objects.filter(conversion__conversion_id=conversion_id)
    
    def get_drug_records_by_patient(self, patient_id: str) -> List[DrugRecord]:
        """Get all drug records for a patient"""
        return DrugRecord.objects.filter(patient_id=patient_id)
    
    def get_drug_records_by_patient_object(self, patient: Patient) -> List[DrugRecord]:
        """Get all drug records for a patient object"""
        return DrugRecord.objects.filter(patient=patient)