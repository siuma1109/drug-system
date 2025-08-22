import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from .interfaces import ParserInterface


class XMLParser(ParserInterface):
    """XML parser implementation following Single Responsibility Principle"""
    
    def __init__(self):
        self.supported_formats = ['prescription', 'medication', 'patient']
    
    def validate(self, data: str) -> bool:
        """Validate XML data format"""
        try:
            ET.fromstring(data)
            return True
        except ET.ParseError:
            return False
    
    def parse(self, data: str) -> Dict[str, Any]:
        """Parse XML data and return structured format"""
        if not self.validate(data):
            raise ValueError("Invalid XML data")
        
        try:
            root = ET.fromstring(data)
            return self._parse_xml_node(root)
        except Exception as e:
            raise ValueError(f"XML parsing error: {str(e)}")
    
    def _parse_xml_node(self, node: ET.Element) -> Dict[str, Any]:
        """Recursively parse XML node"""
        result = {}
        
        # Add attributes
        if node.attrib:
            result['@attributes'] = node.attrib
        
        # Handle child nodes
        children = list(node)
        if children:
            for child in children:
                child_data = self._parse_xml_node(child)
                for tag, data in child_data.items():
                    if tag in result:
                        # Handle multiple children with same tag
                        if not isinstance(result[tag], list):
                            result[tag] = [result[tag]]
                        result[tag].append(data)
                    else:
                        result[tag] = data
        
        # Add text content if no children
        elif node.text and node.text.strip():
            result = node.text.strip()
        
        return {node.tag: result}
    
    def extract_drug_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract drug and patient data from parsed XML"""
        result = {
            'patients': [],
            'drug_records': []
        }
        
        def extract_drugs_recursive(data: Dict[str, Any], path: str = ""):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, dict):
                    # Check if this looks like a drug record
                    if self._is_drug_record(value):
                        drug_record = self._normalize_drug_record(value)
                        result['drug_records'].append(drug_record)
                    else:
                        extract_drugs_recursive(value, current_path)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            extract_drugs_recursive(item, current_path)
        
        extract_drugs_recursive(parsed_data)
        
        # Handle specific XML structure for prescriptions
        if 'prescriptions' in parsed_data:
            prescriptions_data = parsed_data['prescriptions']
            if 'prescription' in prescriptions_data:
                prescription_list = prescriptions_data['prescription']
                if not isinstance(prescription_list, list):
                    prescription_list = [prescription_list]
                
                for prescription in prescription_list:
                    if isinstance(prescription, dict):
                        # Extract patient information
                        patient_info = prescription.get('patient', {})
                        if patient_info and isinstance(patient_info, dict):
                            patient_data = self._normalize_patient_data(patient_info)
                            if patient_data['patient_id']:
                                result['patients'].append(patient_data)
                        
                        # Handle medication information
                        medication_info = prescription.get('medication', {})
                        if isinstance(medication_info, dict):
                            drug_record = self._normalize_drug_record(medication_info, patient_info, prescription)
                            result['drug_records'].append(drug_record)
        
        # Handle single prescription structure
        elif 'prescription' in parsed_data:
            prescription = parsed_data['prescription']
            if isinstance(prescription, dict):
                # Extract patient information
                patient_info = prescription.get('patient', {})
                if patient_info and isinstance(patient_info, dict):
                    patient_data = self._normalize_patient_data(patient_info)
                    if patient_data['patient_id']:
                        result['patients'].append(patient_data)
                
                # Handle medication information
                medication_info = prescription.get('medications', {})
                if isinstance(medication_info, dict):
                    medications_list = medication_info.get('medication', [])
                    if not isinstance(medications_list, list):
                        medications_list = [medications_list] if medications_list else []
                    
                    for medication in medications_list:
                        if isinstance(medication, dict):
                            drug_record = self._normalize_drug_record(medication, patient_info, prescription)
                            result['drug_records'].append(drug_record)
        
        return result
    
    def _is_drug_record(self, data: Dict[str, Any]) -> bool:
        """Check if data represents a drug record"""
        # Check for drug-specific fields
        drug_fields = ['name', 'dosage', 'strength', 'quantity']
        has_drug_fields = any(field in data for field in drug_fields)
        
        # Check for drug keywords in keys
        drug_keywords = ['drug', 'medication', 'medicine']
        has_drug_keywords = any(keyword in str(data).lower() for keyword in drug_keywords)
        
        # Must have drug fields and not be a patient record
        return has_drug_fields and has_drug_keywords and 'patient_id' not in data
    
    def _normalize_patient_data(self, patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize patient data to standard format"""
        patient_id = patient_info.get('id', '')
        name = patient_info.get('name', '')
        
        # Parse name into first and last name
        first_name = ''
        last_name = ''
        full_name = name
        
        if name and ' ' in name:
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        return {
            'patient_id': patient_id,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': full_name,
            'age': self._parse_int(patient_info.get('age')),
            'gender': patient_info.get('gender', ''),
            'address': patient_info.get('address', ''),
            'phone_number': patient_info.get('phone', ''),
            'metadata': {
                'source_format': 'XML',
                'raw_data': patient_info
            }
        }
    
    def _normalize_drug_record(self, data: Dict[str, Any], patient_info: Dict[str, Any] = None, prescription_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Normalize drug record to standard format"""
        normalized = {
            'drug_name': data.get('name') or data.get('drug_name') or data.get('medication_name', ''),
            'dosage': data.get('dosage') or data.get('dose', ''),
            'strength': data.get('strength') or data.get('potency', ''),
            'quantity': self._parse_int(data.get('quantity')),
            'patient_id': data.get('patient_id') or (patient_info.get('id', '') if patient_info else ''),
            'prescription_id': data.get('prescription_id') or data.get('id', ''),
            'metadata': {
                'source_format': 'XML',
                'raw_data': data
            }
        }
        
        # Add patient information to metadata
        if patient_info:
            normalized['metadata']['patient_info'] = patient_info
        elif 'patient' in data and isinstance(data['patient'], dict):
            normalized['metadata']['patient_info'] = data['patient']
        
        # Add prescription information to metadata
        if prescription_info:
            normalized['metadata']['prescription_info'] = prescription_info
        
        return normalized
    
    def _parse_int(self, value: Any) -> int:
        """Parse integer value safely"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None