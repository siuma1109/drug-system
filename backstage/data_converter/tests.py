import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import DataConversion, DrugRecord
from .services.xml_parser import XMLParser
from .services.hl7_parser import HL7Parser
from .services.processor import ConversionManager
from .utils import DataValidator


class DataConverterTestCase(TestCase):
    """Base test case for data converter functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.xml_parser = XMLParser()
        self.hl7_parser = HL7Parser()
        self.conversion_manager = ConversionManager()
        
        # Sample XML data
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <prescription>
            <patient>
                <id>PAT001</id>
                <name>John Doe</name>
            </patient>
            <medications>
                <medication>
                    <name>Aspirin</name>
                    <dosage>81mg</dosage>
                    <strength>81mg</strength>
                    <quantity>30</quantity>
                </medication>
                <medication>
                    <name>Lisinopril</name>
                    <dosage>10mg</dosage>
                    <strength>10mg</strength>
                    <quantity>60</quantity>
                </medication>
            </medications>
        </prescription>"""
        
        # Sample HL7 data
        self.sample_hl7 = """MSH|^~\\&|HIS|LAB|LAB|LAB|202308221200||ORM^O01|MSG00001|P|2.3|
        PID|||PAT001||DOE^JOHN||19800101|M|||123 MAIN ST^^ANYTOWN^NY^12345||(555)555-5555|||S|CN123456789|123456789
        PV1||I|MED|||12345^DOCTOR^JOHN||||||||ADM|A0||
        ORC|NW|ORD001|ORD001||IP|Q6H|202308221200|||12345^DOCTOR^JOHN|202308221200
        RXE|^Aspirin^81MG^TAB|81MG|TAB|Q6H|30|202308221200|||12345^DOCTOR^JOHN
        RXR|PO|ORAL
        RXE|^Lisinopril^10MG^TAB|10MG|TAB|QD|60|202308221200|||12345^DOCTOR^JOHN
        RXR|PO|ORAL"""


class XMLParserTests(DataConverterTestCase):
    """Test XML parser functionality"""
    
    def test_xml_validation_valid(self):
        """Test XML validation with valid XML"""
        self.assertTrue(self.xml_parser.validate(self.sample_xml))
    
    def test_xml_validation_invalid(self):
        """Test XML validation with invalid XML"""
        invalid_xml = "<invalid>xml"
        self.assertFalse(self.xml_parser.validate(invalid_xml))
    
    def test_xml_parsing(self):
        """Test XML parsing functionality"""
        result = self.xml_parser.parse(self.sample_xml)
        
        self.assertIsInstance(result, dict)
        self.assertIn('prescription', result)
        self.assertIn('patient', result['prescription'])
        self.assertIn('medications', result['prescription'])
    
    def test_drug_data_extraction(self):
        """Test drug data extraction from XML"""
        parsed_data = self.xml_parser.parse(self.sample_xml)
        drug_data = self.xml_parser.extract_drug_data(parsed_data)
        drug_records = drug_data.get('drug_records', [])
        
        self.assertEqual(len(drug_records), 2)
        self.assertEqual(drug_records[0]['drug_name'], 'Aspirin')
        self.assertEqual(drug_records[1]['drug_name'], 'Lisinopril')


class HL7ParserTests(DataConverterTestCase):
    """Test HL7 parser functionality"""
    
    def test_hl7_validation_valid(self):
        """Test HL7 validation with valid HL7"""
        self.assertTrue(self.hl7_parser.validate(self.sample_hl7))
    
    def test_hl7_validation_invalid(self):
        """Test HL7 validation with invalid HL7"""
        invalid_hl7 = "Invalid HL7 data"
        self.assertFalse(self.hl7_parser.validate(invalid_hl7))
    
    def test_hl7_parsing(self):
        """Test HL7 parsing functionality"""
        result = self.hl7_parser.parse(self.sample_hl7)
        
        self.assertIsInstance(result, dict)
        self.assertIn('message_type', result)
        self.assertIn('segments', result)
        self.assertIn('MSH', result['segments'])
    
    def test_drug_data_extraction(self):
        """Test drug data extraction from HL7"""
        parsed_data = self.hl7_parser.parse(self.sample_hl7)
        drug_data = self.hl7_parser.extract_drug_data(parsed_data, [])
        drug_records = drug_data.get('drug_records', [])
        
        self.assertEqual(len(drug_records), 2)
        self.assertIn('Aspirin', drug_records[0]['drug_name'])
        self.assertIn('Lisinopril', drug_records[1]['drug_name'])


class DataValidatorTests(DataConverterTestCase):
    """Test data validation functionality"""
    
    def test_xml_validation(self):
        """Test XML data validation"""
        errors = DataValidator.validate_xml_data(self.sample_xml)
        self.assertEqual(len(errors), 0)
        
        errors = DataValidator.validate_xml_data("<invalid>xml")
        self.assertGreater(len(errors), 0)
    
    def test_hl7_validation(self):
        """Test HL7 data validation"""
        errors = DataValidator.validate_hl7_data(self.sample_hl7)
        self.assertEqual(len(errors), 0)
        
        errors = DataValidator.validate_hl7_data("Invalid HL7")
        self.assertGreater(len(errors), 0)
    
    def test_drug_record_validation(self):
        """Test drug record validation"""
        valid_drug = {
            'drug_name': 'Aspirin',
            'dosage': '81mg',
            'quantity': 30
        }
        
        errors = DataValidator.validate_drug_record(valid_drug)
        self.assertEqual(len(errors), 0)
        
        invalid_drug = {
            'drug_name': '',
            'quantity': -1
        }
        
        errors = DataValidator.validate_drug_record(invalid_drug)
        self.assertGreater(len(errors), 0)


class ConversionManagerTests(DataConverterTestCase):
    """Test conversion manager functionality"""
    
    def test_create_conversion(self):
        """Test conversion creation"""
        conversion_id = self.conversion_manager.create_conversion('XML', self.sample_xml)
        
        self.assertIsNotNone(conversion_id)
        conversion = DataConversion.objects.get(conversion_id=conversion_id)
        self.assertEqual(conversion.conversion_type, 'XML')
        self.assertEqual(conversion.status, 'PENDING')
    
    def test_process_xml_conversion(self):
        """Test XML conversion processing"""
        conversion_id = self.conversion_manager.create_conversion('XML', self.sample_xml)
        result = self.conversion_manager.process_conversion(conversion_id, self.xml_parser)
        
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertEqual(result['drug_records_count'], 2)
        
        # Check that drug records were created
        conversion = DataConversion.objects.get(conversion_id=conversion_id)
        self.assertEqual(conversion.drug_records.count(), 2)
    
    def test_process_hl7_conversion(self):
        """Test HL7 conversion processing"""
        conversion_id = self.conversion_manager.create_conversion('HL7', self.sample_hl7)
        result = self.conversion_manager.process_conversion(conversion_id, self.hl7_parser)
        
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertGreater(result['drug_records_count'], 0)
    
    def test_get_conversion_status(self):
        """Test getting conversion status"""
        conversion_id = self.conversion_manager.create_conversion('XML', self.sample_xml)
        status = self.conversion_manager.get_conversion_status(conversion_id)
        
        self.assertEqual(status['conversion_id'], conversion_id)
        self.assertEqual(status['status'], 'PENDING')


class APIEndpointTests(DataConverterTestCase):
    """Test REST API endpoints"""
    
    def test_create_conversion_endpoint(self):
        """Test conversion creation endpoint"""
        data = {
            'conversion_type': 'XML',
            'source_data': self.sample_xml
        }
        
        response = self.client.post(
            '/api/conversions',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertIn('conversion_id', response_data)
        self.assertEqual(response_data['status'], 'PENDING')
        self.assertTrue(response_data['data_validated'])
    
    def test_create_conversion_invalid_xml(self):
        """Test conversion creation with invalid XML"""
        data = {
            'conversion_type': 'XML',
            'source_data': '<invalid>xml'
        }
        
        response = self.client.post(
            '/api/conversions',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertTrue(response_data['validation_failed'])
        self.assertEqual(response_data['conversion_type'], 'XML')
        self.assertIn('Invalid XML format', response_data['error'])
    
    def test_create_conversion_invalid_hl7(self):
        """Test conversion creation with invalid HL7"""
        data = {
            'conversion_type': 'HL7',
            'source_data': 'Invalid HL7 data'
        }
        
        response = self.client.post(
            '/api/conversions',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertTrue(response_data['validation_failed'])
        self.assertEqual(response_data['conversion_type'], 'HL7')
        self.assertIn('Invalid HL7 format', response_data['error'])
    
    def test_process_conversion_endpoint(self):
        """Test conversion processing endpoint"""
        # First create a conversion
        conversion_id = self.conversion_manager.create_conversion('XML', self.sample_xml)
        
        # Then process it
        response = self.client.post(f'/api/conversions/{conversion_id}/process')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'COMPLETED')
    
    def test_get_conversion_status_endpoint(self):
        """Test get conversion status endpoint"""
        conversion_id = self.conversion_manager.create_conversion('XML', self.sample_xml)
        
        response = self.client.get(f'/api/conversions/{conversion_id}/status')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['conversion_id'], conversion_id)
        self.assertEqual(response_data['status'], 'PENDING')
    
    def test_get_conversion_list_endpoint(self):
        """Test get conversion list endpoint"""
        # Create some conversions
        self.conversion_manager.create_conversion('XML', self.sample_xml)
        self.conversion_manager.create_conversion('HL7', self.sample_hl7)
        
        response = self.client.get('/api/conversions/list')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['total_count'], 2)
    
    def test_get_drug_records_endpoint(self):
        """Test get drug records endpoint"""
        conversion_id = self.conversion_manager.create_conversion('XML', self.sample_xml)
        self.conversion_manager.process_conversion(conversion_id, self.xml_parser)
        
        response = self.client.get(f'/api/conversions/{conversion_id}/drug-records')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['total_count'], 2)


class ModelTests(DataConverterTestCase):
    """Test model functionality"""
    
    def test_data_conversion_model(self):
        """Test DataConversion model"""
        conversion = DataConversion.objects.create(
            conversion_id='TEST001',
            conversion_type='XML',
            source_data=self.sample_xml,
            status='PENDING'
        )
        
        self.assertEqual(str(conversion), 'TEST001 - XML')
        self.assertEqual(conversion.status, 'PENDING')
    
    def test_drug_record_model(self):
        """Test DrugRecord model"""
        conversion = DataConversion.objects.create(
            conversion_id='TEST001',
            conversion_type='XML',
            source_data=self.sample_xml,
            status='COMPLETED'
        )
        
        drug_record = DrugRecord.objects.create(
            conversion=conversion,
            drug_name='Aspirin',
            dosage='81mg',
            strength='81mg',
            quantity=30,
            original_patient_id='PAT001',
            prescription_id='RX001'
        )
        
        self.assertEqual(str(drug_record), 'Aspirin - PAT001')
        self.assertEqual(drug_record.quantity, 30)


class IntegrationTests(DataConverterTestCase):
    """Integration tests for the complete system"""
    
    def test_complete_xml_conversion_workflow(self):
        """Test complete XML conversion workflow"""
        # Create conversion via API
        data = {
            'conversion_type': 'XML',
            'source_data': self.sample_xml
        }
        
        response = self.client.post(
            '/api/conversions',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        conversion_id = json.loads(response.content)['conversion_id']
        
        # Process conversion
        response = self.client.post(f'/api/conversions/{conversion_id}/process')
        self.assertEqual(response.status_code, 200)
        
        # Check status
        response = self.client.get(f'/api/conversions/{conversion_id}/status')
        self.assertEqual(response.status_code, 200)
        status_data = json.loads(response.content)
        self.assertEqual(status_data['status'], 'COMPLETED')
        
        # Check drug records
        response = self.client.get(f'/api/conversions/{conversion_id}/drug-records')
        self.assertEqual(response.status_code, 200)
        drug_data = json.loads(response.content)
        self.assertEqual(drug_data['total_count'], 2)
    
    def test_complete_hl7_conversion_workflow(self):
        """Test complete HL7 conversion workflow"""
        # Create conversion via API
        data = {
            'conversion_type': 'HL7',
            'source_data': self.sample_hl7
        }
        
        response = self.client.post(
            '/api/conversions',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        conversion_id = json.loads(response.content)['conversion_id']
        
        # Process conversion
        response = self.client.post(f'/api/conversions/{conversion_id}/process')
        self.assertEqual(response.status_code, 200)
        
        # Check status
        response = self.client.get(f'/api/conversions/{conversion_id}/status')
        self.assertEqual(response.status_code, 200)
        status_data = json.loads(response.content)
        self.assertEqual(status_data['status'], 'COMPLETED')
        
        # Check drug records
        response = self.client.get(f'/api/conversions/{conversion_id}/drug-records')
        self.assertEqual(response.status_code, 200)
        drug_data = json.loads(response.content)
        self.assertGreater(drug_data['total_count'], 0)
