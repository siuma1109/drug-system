from django.db import models
from django.db.models import JSONField
import json


class DataConversion(models.Model):
    CONVERSION_TYPES = [
        ('XML', 'XML'),
        ('HL7', 'HL7'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    conversion_id = models.CharField(max_length=100, unique=True)
    conversion_type = models.CharField(max_length=10, choices=CONVERSION_TYPES)
    source_data = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    converted_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_conversions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.conversion_id} - {self.conversion_type}"


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Unknown'),
    ]
    
    patient_id = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    full_name = models.CharField(max_length=200, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name or self.patient_id} - {self.patient_id}"
    
    def save(self, *args, **kwargs):
        # Auto-generate full_name if not provided
        if not self.full_name and self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)


class DrugRecord(models.Model):
    conversion = models.ForeignKey(DataConversion, on_delete=models.CASCADE, related_name='drug_records')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='drug_records', null=True, blank=True)
    drug_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100, blank=True)
    strength = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    original_patient_id = models.CharField(max_length=100, blank=True)  # Keep for reference
    prescription_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'drug_records'
        ordering = ['-created_at']
    
    def __str__(self):
        patient_name = self.patient.full_name if self.patient else self.original_patient_id
        return f"{self.drug_name} - {patient_name}"
