#!/usr/bin/env python3
"""
Sample data population script for the Drug System
This script creates sample data for testing the mobile API endpoints
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Add the project path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from data_converter.models import Patient, DrugInventory, AdministrationRecord, DeviceStatus

def create_sample_patients():
    """Create sample patient data"""
    patients_data = [
        {
            'patient_id': 'PAT001',
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 45,
            'gender': 'M',
            'date_of_birth': '1978-05-15',
            'address': '123 Main St, New York, NY 10001',
            'phone_number': '+1-555-0123'
        },
        {
            'patient_id': 'PAT002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'age': 32,
            'gender': 'F',
            'date_of_birth': '1991-08-22',
            'address': '456 Oak Ave, Los Angeles, CA 90210',
            'phone_number': '+1-555-0456'
        },
        {
            'patient_id': 'PAT003',
            'first_name': 'Robert',
            'last_name': 'Johnson',
            'age': 67,
            'gender': 'M',
            'date_of_birth': '1956-12-03',
            'address': '789 Pine Rd, Chicago, IL 60601',
            'phone_number': '+1-555-0789'
        }
    ]
    
    for patient_data in patients_data:
        Patient.objects.get_or_create(
            patient_id=patient_data['patient_id'],
            defaults=patient_data
        )
    
    print(f"Created {len(patients_data)} sample patients")

def create_sample_drugs():
    """Create sample drug inventory data"""
    drugs_data = [
        {
            'rfid_tag': 'RFID001',
            'drug_name': 'Amoxicillin',
            'dosage': '500mg',
            'strength': '500mg',
            'quantity': 50,
            'batch_number': 'BATCH001',
            'expiration_date': '2024-12-31',
            'manufacturer': 'Pfizer Inc.',
            'location': 'Cabinet A, Shelf 1'
        },
        {
            'rfid_tag': 'RFID002',
            'drug_name': 'Ibuprofen',
            'dosage': '400mg',
            'strength': '400mg',
            'quantity': 100,
            'batch_number': 'BATCH002',
            'expiration_date': '2025-06-30',
            'manufacturer': 'Johnson & Johnson',
            'location': 'Cabinet A, Shelf 2'
        },
        {
            'rfid_tag': 'RFID003',
            'drug_name': 'Metformin',
            'dosage': '850mg',
            'strength': '850mg',
            'quantity': 8,
            'batch_number': 'BATCH003',
            'expiration_date': '2024-09-15',
            'manufacturer': 'Merck & Co.',
            'location': 'Cabinet B, Shelf 1'
        },
        {
            'rfid_tag': 'RFID004',
            'drug_name': 'Lisinopril',
            'dosage': '10mg',
            'strength': '10mg',
            'quantity': 0,
            'batch_number': 'BATCH004',
            'expiration_date': '2025-03-20',
            'manufacturer': 'Novartis',
            'location': 'Cabinet B, Shelf 2'
        },
        {
            'rfid_tag': 'RFID005',
            'drug_name': 'Atorvastatin',
            'dosage': '20mg',
            'strength': '20mg',
            'quantity': 75,
            'batch_number': 'BATCH005',
            'expiration_date': '2023-11-30',  # Expired
            'manufacturer': 'Pfizer Inc.',
            'location': 'Cabinet C, Shelf 1'
        }
    ]
    
    for drug_data in drugs_data:
        # Auto-set status based on quantity and expiration date
        quantity = drug_data['quantity']
        expiration_date = datetime.strptime(drug_data['expiration_date'], '%Y-%m-%d').date()
        today = datetime.now().date()
        
        if quantity <= 0:
            drug_data['status'] = 'OUT_OF_STOCK'
        elif quantity <= 10:
            drug_data['status'] = 'LOW_STOCK'
        elif expiration_date <= today:
            drug_data['status'] = 'EXPIRED'
        else:
            drug_data['status'] = 'ACTIVE'
        
        DrugInventory.objects.get_or_create(
            rfid_tag=drug_data['rfid_tag'],
            defaults=drug_data
        )
    
    print(f"Created {len(drugs_data)} sample drugs")

def create_sample_devices():
    """Create sample device data"""
    devices_data = [
        {
            'device_id': 'RFID_READER_001',
            'device_type': 'RFID_READER',
            'device_name': 'Main Cabinet RFID Reader',
            'status': 'ONLINE',
            'battery_level': 85,
            'connection_status': 'Connected and operational'
        },
        {
            'device_id': 'RFID_READER_002',
            'device_type': 'RFID_READER',
            'device_name': 'Secondary Cabinet RFID Reader',
            'status': 'OFFLINE',
            'battery_level': None,
            'connection_status': 'Disconnected - maintenance required'
        },
        {
            'device_id': 'BT_THERMOMETER_001',
            'device_type': 'BLUETOOTH_DEVICE',
            'device_name': 'Bluetooth Thermometer',
            'status': 'ONLINE',
            'battery_level': 45,
            'connection_status': 'Connected via Bluetooth'
        },
        {
            'device_id': 'BT_BP_MONITOR_001',
            'device_type': 'BLUETOOTH_DEVICE',
            'device_name': 'Blood Pressure Monitor',
            'status': 'ERROR',
            'battery_level': 15,
            'connection_status': 'Connection error - low battery',
            'error_message': 'Battery level too low for operation'
        }
    ]
    
    for device_data in devices_data:
        DeviceStatus.objects.get_or_create(
            device_id=device_data['device_id'],
            defaults=device_data
        )
    
    print(f"Created {len(devices_data)} sample devices")

def create_sample_administrations():
    """Create sample administration records"""
    try:
        # Get some sample patients and drugs
        patient = Patient.objects.first()
        drug = DrugInventory.objects.first()
        
        if patient and drug:
            administrations_data = [
                {
                    'patient': patient,
                    'drug': drug,
                    'administered_by': 'Dr. Sarah Wilson',
                    'administration_time': datetime.now() - timedelta(hours=2),
                    'dosage_administered': '500mg',
                    'route': 'ORAL',
                    'status': 'ADMINISTERED',
                    'notes': 'Patient tolerated well, no adverse effects',
                    'verification_method': 'RFID'
                },
                {
                    'patient': patient,
                    'drug': drug,
                    'administered_by': 'Nurse John Davis',
                    'administration_time': datetime.now() - timedelta(days=1),
                    'dosage_administered': '500mg',
                    'route': 'ORAL',
                    'status': 'ADMINISTERED',
                    'notes': 'Morning dose administered with breakfast',
                    'verification_method': 'RFID'
                }
            ]
            
            for admin_data in administrations_data:
                AdministrationRecord.objects.create(**admin_data)
            
            print(f"Created {len(administrations_data)} sample administration records")
        else:
            print("No patients or drugs found for creating administration records")
    
    except Exception as e:
        print(f"Error creating administration records: {e}")

def main():
    """Main function to populate sample data"""
    print("Populating sample data for Drug System...")
    
    # Clear existing data (optional)
    # Patient.objects.all().delete()
    # DrugInventory.objects.all().delete()
    # AdministrationRecord.objects.all().delete()
    # DeviceStatus.objects.all().delete()
    
    # Create sample data
    create_sample_patients()
    create_sample_drugs()
    create_sample_devices()
    create_sample_administrations()
    
    print("Sample data population completed!")
    print("\nTest API endpoints:")
    print("GET /api/drugs/inventory - View drug inventory")
    print("POST /api/drugs/scan - Scan drug (RFID001, RFID002, etc.)")
    print("GET /api/patients/list - View patient list")
    print("POST /api/patients/verify - Verify patient (PAT001, PAT002, etc.)")
    print("GET /api/devices/rfid/status - View RFID device status")
    print("POST /api/devices/bluetooth/connect - Connect Bluetooth device")

if __name__ == '__main__':
    main()