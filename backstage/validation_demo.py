#!/usr/bin/env python3

import json
import requests
import time

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_validation():
    """Test the validation functionality"""
    print("=== Testing Data Format Validation ===\n")
    
    # Test 1: Valid XML
    print("1. Testing valid XML...")
    valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <prescription>
        <patient>
            <id>PAT001</id>
            <name>John Doe</name>
        </patient>
        <medications>
            <medication>
                <name>Aspirin</name>
                <dosage>81mg</dosage>
                <quantity>30</quantity>
            </medication>
        </medications>
    </prescription>"""
    
    response = requests.post(
        f"{BASE_URL}/conversions",
        json={
            "conversion_type": "XML",
            "source_data": valid_xml
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Valid XML accepted. Conversion ID: {data['conversion_id']}")
        print(f"   Data validated: {data['data_validated']}")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    print()
    
    # Test 2: Invalid XML
    print("2. Testing invalid XML...")
    invalid_xml = "<invalid>xml"
    
    response = requests.post(
        f"{BASE_URL}/conversions",
        json={
            "conversion_type": "XML",
            "source_data": invalid_xml
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = response.json()
        print(f"✅ Invalid XML rejected as expected")
        print(f"   Error: {data['error']}")
        print(f"   Validation failed: {data['validation_failed']}")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    print()
    
    # Test 3: Valid HL7
    print("3. Testing valid HL7...")
    valid_hl7 = """MSH|^~\\&|HIS|LAB|LAB|LAB|202308221200||ORM^O01|MSG00001|P|2.3|
    PID|||PAT001||DOE^JOHN||19800101|M|||123 MAIN ST^^ANYTOWN^NY^12345||(555)555-5555|||S|CN123456789|123456789
    RXE|^Aspirin^81MG^TAB|81MG|TAB|Q6H|30|202308221200|||12345^DOCTOR^JOHN"""
    
    response = requests.post(
        f"{BASE_URL}/conversions",
        json={
            "conversion_type": "HL7",
            "source_data": valid_hl7
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Valid HL7 accepted. Conversion ID: {data['conversion_id']}")
        print(f"   Data validated: {data['data_validated']}")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    print()
    
    # Test 4: Invalid HL7
    print("4. Testing invalid HL7...")
    invalid_hl7 = "Invalid HL7 data without MSH segment"
    
    response = requests.post(
        f"{BASE_URL}/conversions/",
        json={
            "conversion_type": "HL7",
            "source_data": invalid_hl7
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = response.json()
        print(f"✅ Invalid HL7 rejected as expected")
        print(f"   Error: {data['error']}")
        print(f"   Validation failed: {data['validation_failed']}")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    print("\n=== Validation Test Complete ===")

if __name__ == "__main__":
    print("Django Data Converter - Validation Demo")
    print("Make sure the Django server is running on localhost:8000")
    print()
    
    try:
        test_validation()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server.")
        print("   Please start the Django server with: python manage.py runserver")
    except Exception as e:
        print(f"❌ An error occurred: {e}")