#!/usr/bin/env python3
"""
Test script to verify HL7 parser functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.hl7_parser import HL7Parser

def test_hl7_parser():
    # The HL7 message provided by the user
    hl7_message = """MSH|^~\\&|EPIC|^LINDAS TEST ORGANIZATION|||||VXU^V04^VXU_V04|225|P|2.5.1||||AL|PID|1||E46749^^^^MR^||DOE^JOHN^C^JR^^^L|SMITH|20140515|M|SMITH^JOHN|2106-3^WHITE^HL70005|115 MAINSTREET^^GOODTOWN^KY^42010^USA^L^010||^PRN^PH^^^270^6009800||EN^ENGLISH^HL70296||||523968712|||2186-5^NOT HISPANIC OR LATINO^HL70012||||||||N|
PD1|||LINDAS TEST ORGANIZATION^^SIISCLIENT818|^^^^^^^^^^^^MR|||||||02^Reminder/recall-any method^HL70215|||||A^Active^HL70441|20150202^20150202 NK1|1|DOE^MARY|MTH^MOTHER^HL70063|
PV1||R||||||||||||||||||V02^20150202|
ORC|RE||9645^SIISCLIENT001||||||20150202111146|2001^HARVEY^MARVIN^K| RXA|0|1|20150202|20150202|20^DTaP^CVX^90700^DTAP^CPT|.5|ML^mL^ISO+||00^New immunization record^NIP001|JONES^MARK|^^^SIISCLIENT818||||A7894-2|20161115|PMC^SANOFI PASTEUR^MVX||||ARXR|ID^INTRADERMAL^HL70162|LD^LEFT DELTOID^HL70163
OBX|1|CE|64994-7^VACCINE FUNDING PROGRAM ELIGIBILITY CATEGORY^LN|1| V02^MEDICAID^HL70064||||||F|||20150202|||VXC40^ELIGIBILITY CAPTURED AT THE IMMUNIZATION LEVEL^CDCPHINVSOBX|2|CE|30956-7^VACCINE TYPE^LN|2|88^FLU^CVX||||||F|||20150202102525 OBX|3|TS|29768-9^Date vaccine information statement published^LN|2|20120702||||||FOBX|4|TS|29769-7^Date vaccine information statement presented^LN|2|20120202||||||F
RXA|0|1|20141215|20141115|141^influenza, SEASONAL 36^CVX^90658^Influenza Split^CPT|999|||01^HISTORICAL INFORMATION – SOURCE UNSPECIFIED^ NIP001||||||||||||A"""

    # Debug: Print the raw message to see its structure
    print("Debug - Raw HL7 message structure:")
    print("Length:", len(hl7_message))
    print("First 200 chars:", hl7_message[:200])
    print("Contains \\r:", '\\r' in hl7_message)
    print("Contains \\n:", '\\n' in hl7_message)
    print("Segments found manually:", hl7_message.count('|PID') + hl7_message.count('|PD1') + hl7_message.count('|PV1') + hl7_message.count('|ORC') + hl7_message.count('|OBX') + hl7_message.count('|RXA'))
    print()

    parser = HL7Parser()
    
    print("Testing HL7 Parser...")
    print("=" * 50)
    
    # Test validation
    print("1. Validation:")
    is_valid = parser.validate(hl7_message)
    print(f"   Message is valid: {is_valid}")
    
    if not is_valid:
        print("   ❌ Validation failed")
        return
    
    # Test parsing
    print("\n2. Parsing:")
    try:
        # Debug: Test segment splitting directly
        segments = parser._split_segments(hl7_message)
        print(f"   Debug - Raw segments found: {len(segments)}")
        for i, seg in enumerate(segments):
            print(f"     Segment {i}: {seg[:50]}...")
        
        parsed_data = parser.parse(hl7_message)
        print("   ✅ Parsing successful")
        print(f"   Message type: {parsed_data.get('message_type', {})}")
        print(f"   Segments found: {list(parsed_data.get('segments', {}).keys())}")
    except Exception as e:
        print(f"   ❌ Parsing failed: {e}")
        return
    
    # Test data extraction
    print("\n3. Data Extraction:")
    try:
        # Debug: Check what segments are actually parsed
        print("   Debug - All segments in parsed data:")
        for seg_name, seg_data in parsed_data.get('segments', {}).items():
            print(f"     {seg_name}: {type(seg_data)}")
            if isinstance(seg_data, dict):
                print(f"       Fields: {list(seg_data.get('fields', {}).keys())}")
                # Show some field values for key segments
                if seg_name == 'MSH':
                    print(f"       MSH field 11: {seg_data.get('fields', {}).get('11', 'NOT_FOUND')}")
                    print(f"       MSH field 12: {seg_data.get('fields', {}).get('12', 'NOT_FOUND')}")
                elif seg_name == 'PV1':
                    print(f"       PV1 field 2: {seg_data.get('fields', {}).get('2', 'NOT_FOUND')}")
                    print(f"       PV1 field 20: {seg_data.get('fields', {}).get('20', 'NOT_FOUND')}")
        
        # Check specifically for PID segment
        pid_segment = parsed_data.get('segments', {}).get('PID')
        print(f"   Debug - PID segment: {pid_segment}")
        
        # Check all raw segments for debugging
        print("   Debug - All raw segments:")
        for i, seg in enumerate(segments):
            print(f"     Raw segment {i}: {seg}")
        
        # Test the embedded segment extraction directly
        if segments:
            first_segment = segments[0]
            print(f"   Debug - Testing embedded segment extraction on first segment:")
            embedded = parser._extract_embedded_segments(first_segment)
            print(f"     Embedded segments result: {embedded}")
        
        extraction_result = parser.extract_drug_data(parsed_data, segments)
        print("   ✅ Data extraction successful")
        
        patients = extraction_result.get('patients', [])
        drug_records = extraction_result.get('drug_records', [])
        
        print(f"   Patients found: {len(patients)}")
        for i, patient in enumerate(patients):
            print(f"     Patient {i+1}: {patient}")
        
        print(f"   Drug records found: {len(drug_records)}")
        for i, drug in enumerate(drug_records):
            print(f"     Drug {i+1}: {drug['drug_name']} - {drug['dosage']}")
        
    except Exception as e:
        print(f"   ❌ Data extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n4. Summary:")
    print("   ✅ All tests passed!")
    print(f"   - Patient ID extracted: {patients[0]['patient_id'] if patients else 'None'}")
    print(f"   - Patient name: {patients[0]['full_name'] if patients else 'None'}")
    print(f"   - Drug records: {len(drug_records)}")

if __name__ == "__main__":
    test_hl7_parser()