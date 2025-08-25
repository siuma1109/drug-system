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


class DrugInventory(models.Model):
    """Drug inventory model for RFID tracking"""
    RFID_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('RECALLED', 'Recalled'),
    ]
    
    rfid_tag = models.CharField(max_length=100, unique=True)
    drug_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100, blank=True)
    strength = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0)
    batch_number = models.CharField(max_length=100, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=RFID_STATUS_CHOICES, default='ACTIVE')
    last_scanned = models.DateTimeField(null=True, blank=True)
    last_scanned_by = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drug_inventory'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.drug_name} (RFID: {self.rfid_tag})"


class AdministrationRecord(models.Model):
    """Drug administration records"""
    ADMINISTRATION_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('ADMINISTERED', 'Administered'),
        ('MISSED', 'Missed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUSED', 'Refused'),
    ]
    
    ROUTE_CHOICES = [
        ('ORAL', 'Oral'),
        ('IV', 'Intravenous'),
        ('IM', 'Intramuscular'),
        ('SC', 'Subcutaneous'),
        ('TOPICAL', 'Topical'),
        ('INHALATION', 'Inhalation'),
        ('OTHER', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='administrations')
    drug = models.ForeignKey(DrugInventory, on_delete=models.CASCADE, related_name='administrations')
    administered_by = models.CharField(max_length=100, blank=True)
    administration_time = models.DateTimeField()
    scheduled_time = models.DateTimeField(null=True, blank=True)
    dosage_administered = models.CharField(max_length=100, blank=True)
    route = models.CharField(max_length=20, choices=ROUTE_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=ADMINISTRATION_STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True)
    verification_method = models.CharField(max_length=50, blank=True)  # RFID, Barcode, Manual
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'administration_records'
        ordering = ['-administration_time']
    
    def __str__(self):
        return f"{self.drug.drug_name} - {self.patient.full_name}"


class DeviceStatus(models.Model):
    """Device status tracking for RFID and Bluetooth devices"""
    DEVICE_TYPE_CHOICES = [
        ('RFID_READER', 'RFID Reader'),
        ('BLUETOOTH_DEVICE', 'Bluetooth Device'),
        ('BARCODE_SCANNER', 'Barcode Scanner'),
    ]
    
    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('ERROR', 'Error'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    device_id = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    device_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OFFLINE')
    battery_level = models.IntegerField(null=True, blank=True)
    last_connected = models.DateTimeField(null=True, blank=True)
    last_disconnected = models.DateTimeField(null=True, blank=True)
    connection_status = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'device_status'
        ordering = ['-last_connected']
    
    def __str__(self):
        return f"{self.device_name} ({self.device_type})"
