import re
from typing import Dict, Any, List
from .interfaces import ParserInterface


class HL7Parser(ParserInterface):
    """HL7 parser implementation following Single Responsibility Principle"""
    
    def __init__(self):
        self.segment_delimiter = '\r|\n'
        self.field_delimiter = '|'
        self.component_delimiter = '^'
        self.subcomponent_delimiter = '&'
        self.repetition_delimiter = '~'
        self.escape_character = '\\'
    
    def validate(self, data: str) -> bool:
        """Validate HL7 data format"""
        if not data.strip():
            return False
        
        # Check for basic HL7 structure (MSH segment)
        lines = self._split_segments(data)
        if not lines:
            return False
        
        # First line should start with MSH
        return lines[0].startswith('MSH')
    
    def parse(self, data: str) -> Dict[str, Any]:
        """Parse HL7 data and return structured format"""
        if not self.validate(data):
            raise ValueError("Invalid HL7 data")
        
        try:
            lines = self._split_segments(data)
            parsed_message = {
                'message_type': self._extract_message_type(lines[0]),
                'segments': {}
            }
            
            for line in lines:
                segment_name = line[:3]
                segment_data = self._parse_segment(line)
                
                if segment_name in parsed_message['segments']:
                    if not isinstance(parsed_message['segments'][segment_name], list):
                        parsed_message['segments'][segment_name] = [parsed_message['segments'][segment_name]]
                    parsed_message['segments'][segment_name].append(segment_data)
                else:
                    parsed_message['segments'][segment_name] = segment_data
            
            return parsed_message
        except Exception as e:
            raise ValueError(f"HL7 parsing error: {str(e)}")
    
    def _parse_segment(self, segment: str) -> Dict[str, Any]:
        """Parse individual HL7 segment"""
        fields = segment.split(self.field_delimiter)
        segment_name = fields[0]
        
        parsed_segment = {
            'segment_name': segment_name,
            'fields': {}
        }
        
        for i, field in enumerate(fields[1:], start=1):  # Skip segment name
            if field:
                parsed_field = self._parse_field(field)
                parsed_segment['fields'][str(i)] = parsed_field
        
        return parsed_segment
    
    def _parse_field(self, field: str) -> Dict[str, Any]:
        """Parse HL7 field with components"""
        if self.component_delimiter in field:
            components = field.split(self.component_delimiter)
            return {
                'type': 'composite',
                'components': [self._parse_component(comp) for comp in components]
            }
        else:
            return {
                'type': 'primitive',
                'value': field
            }
    
    def _parse_component(self, component: str) -> Dict[str, Any]:
        """Parse HL7 component with subcomponents"""
        if self.subcomponent_delimiter in component:
            subcomponents = component.split(self.subcomponent_delimiter)
            return {
                'type': 'composite',
                'subcomponents': subcomponents
            }
        else:
            return {
                'type': 'primitive',
                'value': component
            }
    
    def _extract_message_type(self, msh_segment: str) -> Dict[str, str]:
        """Extract message type from MSH segment"""
        fields = msh_segment.split(self.field_delimiter)
        if len(fields) > 8:
            message_type_field = fields[8]
            if self.component_delimiter in message_type_field:
                components = message_type_field.split(self.component_delimiter)
                return {
                    'message_type': components[0] if len(components) > 0 else '',
                    'trigger_event': components[1] if len(components) > 1 else ''
                }
            else:
                return {
                    'message_type': message_type_field,
                    'trigger_event': ''
                }
        return {'message_type': '', 'trigger_event': ''}
    
    def extract_drug_data(self, parsed_data: Dict[str, Any], raw_segments: List[str] = None) -> Dict[str, Any]:
        """Extract drug and patient data from parsed HL7"""
        result = {
            'patients': [],
            'drug_records': []
        }
        
        # Extract prescription information from ORC segments
        prescription_info = self._extract_prescription_info(parsed_data)
        
        # Extract patient information from PID segment
        patient_data = self._extract_patient_data(parsed_data, raw_segments)
        if patient_data['patient_id']:
            result['patients'].append(patient_data)
        
        # Look for RXA (Pharmacy/Treatment Administration) segments for vaccines/medications
        if 'RXA' in parsed_data['segments']:
            rxa_segments = parsed_data['segments']['RXA']
            if not isinstance(rxa_segments, list):
                rxa_segments = [rxa_segments]
            
            for i, rxa in enumerate(rxa_segments):
                drug_record = self._parse_rxa_segment(rxa)
                if drug_record and drug_record['drug_name']:
                    # Add patient ID
                    drug_record['patient_id'] = patient_data['patient_id']
                    drug_record['metadata']['patient_info'] = patient_data
                    
                    # Add prescription ID from corresponding ORC segment
                    if i < len(prescription_info):
                        drug_record['prescription_id'] = prescription_info[i].get('prescription_id', '')
                        drug_record['metadata']['prescription_info'] = prescription_info[i]
                    result['drug_records'].append(drug_record)
        
        # Look for RXE (Pharmacy/Treatment Encoded Order) segments as fallback
        elif 'RXE' in parsed_data['segments']:
            rxe_segments = parsed_data['segments']['RXE']
            if not isinstance(rxe_segments, list):
                rxe_segments = [rxe_segments]
            
            for i, rxe in enumerate(rxe_segments):
                drug_record = self._parse_rxe_segment(rxe)
                if drug_record and drug_record['drug_name']:
                    # Add patient ID
                    drug_record['patient_id'] = patient_data['patient_id']
                    drug_record['metadata']['patient_info'] = patient_data
                    
                    # Add prescription ID from corresponding ORC segment
                    if i < len(prescription_info):
                        drug_record['prescription_id'] = prescription_info[i].get('prescription_id', '')
                        drug_record['metadata']['prescription_info'] = prescription_info[i]
                    result['drug_records'].append(drug_record)
        
        # Look for RXR (Pharmacy/Treatment Route) segments
        if 'RXR' in parsed_data['segments']:
            rxr_segments = parsed_data['segments']['RXR']
            if not isinstance(rxr_segments, list):
                rxr_segments = [rxr_segments]
            
            # Match RXR segments with drug records
            for i, rxr in enumerate(rxr_segments):
                if i < len(result['drug_records']):
                    route_info = self._parse_rxr_segment(rxr)
                    result['drug_records'][i]['metadata']['route_info'] = route_info
        
        return result
    
    def _parse_rxa_segment(self, rxa_segment: Dict[str, Any]) -> Dict[str, Any]:
        """Parse RXA segment for drug/vaccine information"""
        fields = rxa_segment['fields']
        
        # Extract drug name from composite field (field 5)
        drug_name = ''
        field5 = self._get_field_value(fields, '5', '')
        
        if isinstance(field5, dict) and field5.get('type') == 'composite':
            # Extract from composite field like "141^influenza, SEASONAL 36^CVX^90658^Influenza Split^CPT"
            # Component 1: CVX code (141)
            # Component 2: Drug name (influenza, SEASONAL 36) 
            # Component 3: Code system (CVX)
            # Component 4: Alternate code (90658)
            # Component 5: Alternate name (Influenza Split)
            components = field5.get('components', [])
            if len(components) > 1:
                # Prefer component 1 (drug name) over component 0 (code)
                drug_name = self._extract_component_value(components[1])
            elif len(components) > 0:
                drug_name = self._extract_component_value(components[0])
            if len(components) > 4 and not drug_name:
                # Fallback to component 4 (alternate name)
                drug_name = self._extract_component_value(components[4])
        elif isinstance(field5, str) and '^' in field5:
            # Extract from string like "20^DTaP^CVX^90700^DTAP^CPT"
            parts = field5.split('^')
            drug_name = parts[1] if len(parts) > 1 else parts[0]
        else:
            drug_name = str(field5)
        
        # Extract administration date (field 3) - when administered
        admin_date = self._get_field_value(fields, '3', '')
        parsed_admin_date = self._parse_date(admin_date) or ''
        
        # Extract dosage/quantity (field 6) - amount administered
        dosage = self._get_field_value(fields, '6', '')
        
        # Extract completion status (field 21) - completion status
        completion_status = self._get_field_value(fields, '21', '')
        
        # Extract administration information (field 9) - route, site, etc.
        admin_info = self._get_field_value(fields, '9', '')
        
        drug_record = {
            'drug_name': drug_name,
            'dosage': dosage,
            'strength': '',
            'quantity': self._parse_int(dosage),
            'administration_date': parsed_admin_date,
            'completion_status': completion_status,
            'patient_id': '',
            'prescription_id': '',
            'metadata': {
                'source_format': 'HL7',
                'segment_type': 'RXA',
                'administration_date': admin_date,
                'raw_data': rxa_segment,
                'administration_info': admin_info
            }
        }
        
        return drug_record
    
    def _parse_rxe_segment(self, rxe_segment: Dict[str, Any]) -> Dict[str, Any]:
        """Parse RXE segment for drug information"""
        fields = rxe_segment['fields']
        
        # Extract drug name from composite field (field 1)
        drug_name = ''
        field1 = self._get_field_value(fields, '1', '')
        if isinstance(field1, dict) and field1.get('type') == 'composite':
            # Extract from composite field like "^Aspirin^81MG^TAB"
            components = field1.get('components', [])
            if len(components) > 1:
                drug_name = components[1].get('value', '') if isinstance(components[1], dict) else str(components[1])
        elif isinstance(field1, str) and '^' in field1:
            # Extract from string like "^Aspirin^81MG^TAB"
            parts = field1.split('^')
            drug_name = parts[1] if len(parts) > 1 else field1
        else:
            drug_name = str(field1)
        
        drug_record = {
            'drug_name': drug_name,
            'dosage': self._get_field_value(fields, '4', ''),
            'strength': self._get_field_value(fields, '2', ''),
            'quantity': self._parse_int(self._get_field_value(fields, '5', '')),
            'patient_id': '',
            'prescription_id': '',
            'metadata': {
                'source_format': 'HL7',
                'segment_type': 'RXE',
                'raw_data': rxe_segment
            }
        }
        
        return drug_record
    
    def _parse_rxr_segment(self, rxr_segment: Dict[str, Any]) -> Dict[str, Any]:
        """Parse RXR segment for route information"""
        fields = rxr_segment['fields']
        
        return {
            'administration_route': self._get_field_value(fields, '1', ''),
            'administration_site': self._get_field_value(fields, '2', ''),
            'metadata': {
                'route_info': rxr_segment
            }
        }
    
    def _extract_prescription_info(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract prescription information from ORC segments"""
        prescription_info = []
        
        if 'ORC' not in parsed_data['segments']:
            return prescription_info
        
        orc_segments = parsed_data['segments']['ORC']
        if not isinstance(orc_segments, list):
            orc_segments = [orc_segments]
        
        for orc in orc_segments:
            fields = orc['fields']
            
            info = {
                'prescription_id': self._get_field_value(fields, '2', ''),
                'order_control': self._get_field_value(fields, '1', ''),
                'filler_order_number': self._get_field_value(fields, '3', ''),
                'order_status': self._get_field_value(fields, '5', ''),
                'quantity_timing': self._get_field_value(fields, '7', ''),
                'metadata': {
                    'orc_segment': orc
                }
            }
            prescription_info.append(info)
        
        return prescription_info
    
    def _extract_patient_data(self, parsed_data: Dict[str, Any], raw_segments: List[str] = None) -> Dict[str, Any]:
        """Extract patient information from PID or PV1 segment"""
        patient_data = {'patient_id': ''}
        
        # Try to extract from PID segment first
        if 'PID' in parsed_data['segments']:
            pid_segment = parsed_data['segments']['PID']
            if isinstance(pid_segment, list):
                pid_segment = pid_segment[0]
            
            fields = pid_segment['fields']
            
            # Extract patient ID (field 2 or 3) - In HL7, field 3 is typically patient ID
            patient_id = self._get_field_value(fields, '3', '') or self._get_field_value(fields, '2', '')
            
            # Extract patient name (field 5) - In HL7, field 5 is patient name
            patient_name_field = self._get_field_value(fields, '5', '')
            name_data = self._parse_patient_name(patient_name_field)
            
            # Extract date of birth (field 7) - In HL7, field 7 is date of birth
            dob_field = self._get_field_value(fields, '7', '')
            date_of_birth = self._parse_date(dob_field) or ''
            
            # Extract gender (field 8) - In HL7, field 8 is gender
            gender = self._get_field_value(fields, '8', '')
            
            # Extract address (field 11) - In HL7, field 11 is address
            address_field = self._get_field_value(fields, '11', '')
            address = self._parse_address(address_field)
            
            # Extract phone number (field 13 or 14) - In HL7, these are phone numbers
            phone_number = self._get_field_value(fields, '13', '') or self._get_field_value(fields, '14', '')
            
            patient_data = {
                'patient_id': patient_id,
                'first_name': name_data['first_name'],
                'last_name': name_data['last_name'],
                'full_name': name_data['full_name'],
                'date_of_birth': date_of_birth,
                'gender': gender,
                'address': address,
                'phone_number': phone_number,
                'metadata': {
                    'source_format': 'HL7',
                    'source_segment': 'PID',
                    'raw_data': pid_segment
                }
            }
        
        # If no PID segment found, try to extract PID data from raw segments
        elif raw_segments and len(raw_segments) > 0:
            # Look for PID data in the first raw segment (which contains MSH + embedded PID)
            first_segment = raw_segments[0]
            if '|PID|' in first_segment:
                # Extract PID data from raw segment
                pid_match = re.search(r'\|PID\|(.+?)(?=\|[A-Z]{3}\||$)', first_segment)
                if pid_match:
                    pid_data = pid_match.group(1)
                    
                    # Parse the PID data manually
                    pid_fields = pid_data.split('|')
                    if len(pid_fields) >= 8:
                        # Extract patient information from PID fields
                        # PID field structure: PID|1|PatientID||LastName^FirstName^Middle^Suffix|...|DOB|Gender|...
                        patient_id = pid_fields[2] if len(pid_fields) > 2 else ''  # Field 3: Patient ID
                        patient_name_field = pid_fields[4] if len(pid_fields) > 4 else ''  # Field 5: Patient Name
                        dob_field = pid_fields[6] if len(pid_fields) > 6 else ''  # Field 7: Date of Birth
                        gender = pid_fields[7] if len(pid_fields) > 7 else ''  # Field 8: Gender
                        
                        # Parse the patient name
                        name_data = self._parse_patient_name(patient_name_field)
                        date_of_birth = self._parse_date(dob_field) or ''
                        
                        patient_data = {
                            'patient_id': patient_id,
                            'first_name': name_data['first_name'],
                            'last_name': name_data['last_name'],
                            'full_name': name_data['full_name'],
                            'date_of_birth': date_of_birth,
                            'gender': gender,
                            'address': '',
                            'phone_number': '',
                            'metadata': {
                                'source_format': 'HL7',
                                'source_segment': 'PID_EMBEDDED',
                                'raw_data': {'pid_data': pid_data}
                            }
                        }
        
        # If no patient data from PID or MSH, try PV1 segment
        if not patient_data.get('patient_id') and 'PV1' in parsed_data['segments']:
            pv1_segment = parsed_data['segments']['PV1']
            if isinstance(pv1_segment, list):
                pv1_segment = pv1_segment[0]
            
            fields = pv1_segment['fields']
            
            # In PV1, patient information might be in different fields
            # Field 19: Visit Number (could contain patient ID)
            # Field 20: Financial Class (might contain patient info)
            
            patient_id = self._get_field_value(fields, '19', '')
            
            # Try to extract patient info from field 20 (composite field)
            field20 = self._get_field_value(fields, '20', '')
            if isinstance(field20, dict) and field20.get('type') == 'composite':
                components = field20.get('components', [])
                if len(components) > 0:
                    patient_id = self._extract_component_value(components[0]) or patient_id
            
            # Create minimal patient data from PV1
            patient_data = {
                'patient_id': patient_id or 'PV1_PATIENT',
                'first_name': '',
                'last_name': '',
                'full_name': 'Patient from PV1',
                'date_of_birth': '1900-01-01',
                'gender': '',
                'address': '',
                'phone_number': '',
                'metadata': {
                    'source_format': 'HL7',
                    'source_segment': 'PV1',
                    'raw_data': pv1_segment
                }
            }
        
        return patient_data
    
    def _parse_patient_name(self, patient_name_field) -> Dict[str, str]:
        """Parse patient name from various formats"""
        first_name = ''
        last_name = ''
        full_name = ''
        
        if not patient_name_field:
            return {'first_name': '', 'last_name': '', 'full_name': ''}
        
        if isinstance(patient_name_field, dict) and patient_name_field.get('type') == 'composite':
            # Handle composite name field
            components = patient_name_field.get('components', [])
            if len(components) > 0:
                last_name = self._extract_component_value(components[0])
            if len(components) > 1:
                first_name = self._extract_component_value(components[1])
            full_name = f"{first_name} {last_name}".strip()
        elif isinstance(patient_name_field, str) and '^' in patient_name_field:
            # Handle HL7 name format: Last^First^Middle^Suffix^Prefix^Degree
            name_parts = patient_name_field.split('^')
            if len(name_parts) > 0:
                last_name = name_parts[0]
            if len(name_parts) > 1:
                first_name = name_parts[1]
            full_name = f"{first_name} {last_name}".strip()
        else:
            full_name = str(patient_name_field)
        
        return {'first_name': first_name, 'last_name': last_name, 'full_name': full_name}
    
    def _extract_component_value(self, component) -> str:
        """Extract value from a component"""
        if isinstance(component, dict):
            return component.get('value', '')
        return str(component) if component else ''
    
    def _parse_address(self, address_field) -> str:
        """Parse address from HL7 address field"""
        if not address_field:
            return ''
        
        if isinstance(address_field, dict) and address_field.get('type') == 'composite':
            # Handle composite address field: Street^City^State^Zip^Country
            components = address_field.get('components', [])
            address_parts = []
            for i, component in enumerate(components):
                if i < 4:  # Street, City, State, Zip
                    value = self._extract_component_value(component)
                    if value:
                        address_parts.append(value)
            return ', '.join(address_parts)
        elif isinstance(address_field, str) and '^' in address_field:
            # Handle HL7 address format
            address_parts = address_field.split('^')
            relevant_parts = address_parts[:4]  # Street, City, State, Zip
            return ', '.join(filter(None, relevant_parts))
        else:
            return str(address_field)
    
    def _parse_date(self, date_str: str) -> str:
        """Parse HL7 date format"""
        if not date_str or len(date_str) < 8:
            return None
        
        # Basic HL7 date format: YYYYMMDD
        try:
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            # Validate the date components
            if year.isdigit() and month.isdigit() and day.isdigit():
                year_int = int(year)
                month_int = int(month)
                day_int = int(day)
                # Basic validation
                if 1900 <= year_int <= 2100 and 1 <= month_int <= 12 and 1 <= day_int <= 31:
                    return f"{year_int}-{month_int:02d}-{day_int:02d}"
            return None
        except:
            return None
    
    def _extract_patient_info(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patient information from PID segment (legacy method)"""
        if 'PID' not in parsed_data['segments']:
            return {}
        
        pid_segment = parsed_data['segments']['PID']
        if isinstance(pid_segment, list):
            pid_segment = pid_segment[0]
        
        fields = pid_segment['fields']
        
        return {
            'patient_id': self._get_field_value(fields, '2', ''),
            'patient_name': self._get_field_value(fields, '5', ''),
            'date_of_birth': self._parse_date(self._get_field_value(fields, '7', '')) or '1900-01-01',
            'gender': self._get_field_value(fields, '8', ''),
            'address': self._get_field_value(fields, '11', ''),
            'phone_number': self._get_field_value(fields, '13', '')
        }
    
    def _get_field_value(self, fields: Dict[str, Any], field_number: str, default: str = '') -> Any:
        """Get field value safely"""
        if field_number in fields:
            field = fields[field_number]
            if isinstance(field, dict):
                if field.get('type') == 'primitive':
                    return field.get('value', default)
                elif field.get('type') == 'composite' and 'components' in field:
                    return field  # Return the entire composite field for processing
            return field
        return default
    
    def _split_segments(self, data: str) -> List[str]:
        """Split HL7 data into segments"""
        # Handle both \r\n and \n as segment delimiters
        segments = []
        current_segment = ""
        
        # First, check if we have traditional line breaks
        if '\r' in data or '\n' in data:
            for char in data:
                if char == '\r':
                    # End of segment
                    if current_segment.strip():
                        segments.append(current_segment.strip())
                    current_segment = ""
                elif char == '\n':
                    # End of segment
                    if current_segment.strip():
                        segments.append(current_segment.strip())
                    current_segment = ""
                else:
                    current_segment += char
            
            # Add the last segment if it exists
            if current_segment.strip():
                segments.append(current_segment.strip())
        else:
            # Handle single-line HL7 format - split by segment names
            # Look for patterns like |PID|, |PD1|, |PV1|, etc.
            import re
            
            # Split the message by segment delimiters (3-letter segment names preceded by |)
            # First, find all segment start positions
            segment_pattern = r'\|([A-Z]{3})\|'
            matches = list(re.finditer(segment_pattern, data))
            
            if matches:
                # Start from the beginning (MSH segment)
                start_pos = 0
                
                for match in matches:
                    segment_name = match.group(1)
                    segment_start = match.start() + 1  # Include the |
                    
                    # Add the previous segment
                    if start_pos < segment_start:
                        segment_content = data[start_pos:segment_start]
                        if segment_content.strip():
                            # Check if this segment contains embedded segments
                            # For example, MSH segment might contain PID data
                            embedded_segments = self._extract_embedded_segments(segment_content)
                            if embedded_segments:
                                segments.extend(embedded_segments)
                            else:
                                segments.append(segment_content.strip())
                    
                    start_pos = segment_start
                
                # Add the last segment
                if start_pos < len(data):
                    last_segment = data[start_pos:]
                    if last_segment.strip():
                        segments.append(last_segment.strip())
            else:
                # Fallback: treat the whole message as one segment
                segments = [data.strip()] if data.strip() else []
        
        return segments
    
    def _extract_embedded_segments(self, segment_content: str) -> List[str]:
        """Extract embedded segments from a segment content"""
        embedded_segments = []
        
        # Check if this is an MSH segment that might contain embedded PID data
        if segment_content.startswith('MSH'):
            # Look for |PID| pattern within the MSH segment
            pid_match = re.search(r'\|PID\|(.+)', segment_content)
            if pid_match:
                pid_data = pid_match.group(1)
                # Extract the part before PID as MSH
                msh_end = pid_match.start()
                msh_segment = segment_content[:msh_end]
                embedded_segments.append(msh_segment.strip())
                
                # Create PID segment - but we need to find the end of the PID data
                # Look for the next segment start or end of string
                next_segment_match = re.search(r'\|[A-Z]{3}\|', pid_data)
                if next_segment_match:
                    pid_data = pid_data[:next_segment_match.start()]
                
                pid_segment = 'PID|' + pid_data
                embedded_segments.append(pid_segment.strip())
                
                return embedded_segments
        
        # If no embedded segments found, return None
        return None
    
    def _parse_int(self, value: str) -> int:
        """Parse integer value safely"""
        if not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None