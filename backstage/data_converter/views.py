import json
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string
from .services.processor import ConversionManager
from .services.xml_parser import XMLParser
from .services.hl7_parser import HL7Parser
from .services.interfaces import ParserInterface


class DataConversionView:
    """REST API view for data conversion following Single Responsibility Principle"""

    def __init__(self):
        self.manager = ConversionManager()
        self.parsers = {"XML": XMLParser(), "HL7": HL7Parser()}

    def create_conversion(self, request: HttpRequest) -> JsonResponse:
        """Create a new data conversion"""
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()

            # Validate required fields
            if "conversion_type" not in data:
                return JsonResponse(
                    {"error": "conversion_type is required"}, status=400
                )

            if "source_data" not in data:
                return JsonResponse({"error": "source_data is required"}, status=400)

            conversion_type = data["conversion_type"].upper()
            if conversion_type not in self.parsers:
                return JsonResponse(
                    {"error": f"Unsupported conversion type: {conversion_type}"},
                    status=400,
                )

            source_data = data["source_data"]
            
            # Validate data format based on type
            parser = self.parsers[conversion_type]
            if not parser.validate(source_data):
                error_msg = f"Invalid {conversion_type} data format"
                if conversion_type == "XML":
                    error_msg = "Invalid XML format. Please check your XML structure and syntax."
                elif conversion_type == "HL7":
                    error_msg = "Invalid HL7 format. Please ensure proper HL7 message structure with MSH segment."
                
                return JsonResponse(
                    {
                        "error": error_msg,
                        "conversion_type": conversion_type,
                        "validation_failed": True
                    },
                    status=400,
                )

            # Create conversion
            conversion_id = self.manager.create_conversion(
                conversion_type, source_data
            )

            return JsonResponse(
                {
                    "conversion_id": conversion_id,
                    "status": "PENDING",
                    "message": "Conversion created successfully",
                    "conversion_type": conversion_type,
                    "data_validated": True
                },
                status=201,
            )

        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "Invalid request data format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def process_conversion(
        self, request: HttpRequest, conversion_id: str
    ) -> JsonResponse:
        """Process a data conversion"""
        try:
            # Get conversion to determine type
            conversion = self.manager.conversion_repo.get_conversion_by_id_safe(
                conversion_id
            )
            if not conversion:
                return JsonResponse({"error": "Conversion not found"}, status=404)

            # Get appropriate parser
            parser = self.parsers.get(conversion.conversion_type)
            if not parser:
                return JsonResponse(
                    {"error": f"No parser available for {conversion.conversion_type}"},
                    status=400,
                )

            # Process conversion
            result = self.manager.process_conversion(conversion_id, parser)

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get_conversion_status(
        self, request: HttpRequest, conversion_id: str
    ) -> JsonResponse:
        """Get conversion status"""
        try:
            status = self.manager.get_conversion_status(conversion_id)

            if "error" in status:
                return JsonResponse(status, status=404)

            return JsonResponse(status)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get_conversion_list(self, request: HttpRequest) -> JsonResponse:
        """Get list of all conversions"""
        try:
            from .models import DataConversion

            conversions = DataConversion.objects.all().order_by("-created_at")
            conversion_list = []

            for conversion in conversions:
                conversion_list.append(
                    {
                        "conversion_id": conversion.conversion_id,
                        "conversion_type": conversion.conversion_type,
                        "status": conversion.status,
                        "created_at": conversion.created_at.isoformat(),
                        "updated_at": conversion.updated_at.isoformat(),
                        "drug_records_count": conversion.drug_records.count(),
                    }
                )

            return JsonResponse(
                {"conversions": conversion_list, "total_count": len(conversion_list)}
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get_drug_records(
        self, request: HttpRequest, conversion_id: str
    ) -> JsonResponse:
        """Get drug records for a conversion"""
        try:
            from .models import DrugRecord

            drug_records = DrugRecord.objects.filter(
                conversion__conversion_id=conversion_id
            ).select_related('patient')
            records_list = []

            for record in drug_records:
                patient_info = None
                if record.patient:
                    patient_info = {
                        "patient_id": record.patient.patient_id,
                        "first_name": record.patient.first_name,
                        "last_name": record.patient.last_name,
                        "full_name": record.patient.full_name,
                        "age": record.patient.age,
                        "gender": record.patient.gender,
                        "date_of_birth": record.patient.date_of_birth.isoformat() if record.patient.date_of_birth else None,
                        "address": record.patient.address,
                        "phone_number": record.patient.phone_number,
                    }
                
                records_list.append(
                    {
                        "id": record.id,
                        "drug_name": record.drug_name,
                        "dosage": record.dosage,
                        "strength": record.strength,
                        "quantity": record.quantity,
                        "original_patient_id": record.original_patient_id,
                        "prescription_id": record.prescription_id,
                        "patient": patient_info,
                        "created_at": record.created_at.isoformat(),
                        "metadata": record.metadata,
                    }
                )

            return JsonResponse(
                {
                    "conversion_id": conversion_id,
                    "drug_records": records_list,
                    "total_count": len(records_list),
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# Create view instance
conversion_view = DataConversionView()


# URL route handlers
@csrf_exempt
def create_conversion_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    return conversion_view.create_conversion(request)


@csrf_exempt
def process_conversion_view(request, conversion_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    return conversion_view.process_conversion(request, conversion_id)


@csrf_exempt
def get_conversion_status_view(request, conversion_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    return conversion_view.get_conversion_status(request, conversion_id)


@csrf_exempt
def get_conversion_list_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    return conversion_view.get_conversion_list(request)


@csrf_exempt
def get_drug_records_view(request, conversion_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    return conversion_view.get_drug_records(request, conversion_id)


# Drug Inventory Management Views
@csrf_exempt
def get_drug_inventory_view(request):
    """Get current drug inventory"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import DrugInventory
        
        # Get query parameters
        status_filter = request.GET.get('status')
        location_filter = request.GET.get('location')
        
        inventory = DrugInventory.objects.all()
        
        if status_filter:
            inventory = inventory.filter(status=status_filter)
        if location_filter:
            inventory = inventory.filter(location=location_filter)
        
        inventory_list = []
        for item in inventory:
            inventory_list.append({
                'id': item.id,
                'rfid_tag': item.rfid_tag,
                'drug_name': item.drug_name,
                'dosage': item.dosage,
                'strength': item.strength,
                'quantity': item.quantity,
                'batch_number': item.batch_number,
                'expiration_date': item.expiration_date.isoformat() if item.expiration_date else None,
                'manufacturer': item.manufacturer,
                'location': item.location,
                'status': item.status,
                'last_scanned': item.last_scanned.isoformat() if item.last_scanned else None,
                'last_scanned_by': item.last_scanned_by,
                'metadata': item.metadata,
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'inventory': inventory_list,
            'total_count': len(inventory_list),
            'status_summary': {
                'active': inventory.filter(status='ACTIVE').count(),
                'low_stock': inventory.filter(status='LOW_STOCK').count(),
                'expired': inventory.filter(status='EXPIRED').count(),
                'out_of_stock': inventory.filter(status='OUT_OF_STOCK').count(),
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def scan_drug_view(request):
    """Scan drug via RFID"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import DrugInventory
        
        data = json.loads(request.body)
        rfid_tag = data.get('rfid_tag')
        scanned_by = data.get('scanned_by', 'Unknown')
        
        if not rfid_tag:
            return JsonResponse({'error': 'RFID tag is required'}, status=400)
        
        # Find the drug by RFID tag
        try:
            drug = DrugInventory.objects.get(rfid_tag=rfid_tag)
            
            # Update scan information
            drug.last_scanned = timezone.now()
            drug.last_scanned_by = scanned_by
            
            # Auto-update status based on quantity
            if drug.quantity <= 0:
                drug.status = 'OUT_OF_STOCK'
            elif drug.quantity <= 10:
                drug.status = 'LOW_STOCK'
            elif drug.expiration_date and drug.expiration_date <= timezone.now().date():
                drug.status = 'EXPIRED'
            else:
                drug.status = 'ACTIVE'
            
            drug.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Drug scanned successfully',
                'drug': {
                    'id': drug.id,
                    'rfid_tag': drug.rfid_tag,
                    'drug_name': drug.drug_name,
                    'dosage': drug.dosage,
                    'strength': drug.strength,
                    'quantity': drug.quantity,
                    'status': drug.status,
                    'location': drug.location,
                    'expiration_date': drug.expiration_date.isoformat() if drug.expiration_date else None,
                    'last_scanned': drug.last_scanned.isoformat(),
                }
            })
            
        except DrugInventory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Drug not found with this RFID tag',
                'rfid_tag': rfid_tag
            }, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_drug_stock_view(request):
    """Update drug quantities"""
    if request.method != "PUT":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import DrugInventory
        
        data = json.loads(request.body)
        rfid_tag = data.get('rfid_tag')
        quantity_change = data.get('quantity_change', 0)
        operation = data.get('operation', 'set')  # 'set', 'add', 'subtract'
        updated_by = data.get('updated_by', 'Unknown')
        
        if not rfid_tag:
            return JsonResponse({'error': 'RFID tag is required'}, status=400)
        
        try:
            drug = DrugInventory.objects.get(rfid_tag=rfid_tag)
            
            # Update quantity based on operation
            if operation == 'set':
                drug.quantity = quantity_change
            elif operation == 'add':
                drug.quantity += quantity_change
            elif operation == 'subtract':
                drug.quantity = max(0, drug.quantity - quantity_change)
            
            # Update status based on new quantity
            if drug.quantity <= 0:
                drug.status = 'OUT_OF_STOCK'
            elif drug.quantity <= 10:
                drug.status = 'LOW_STOCK'
            elif drug.expiration_date and drug.expiration_date <= timezone.now().date():
                drug.status = 'EXPIRED'
            else:
                drug.status = 'ACTIVE'
            
            drug.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Drug stock updated successfully',
                'drug': {
                    'id': drug.id,
                    'rfid_tag': drug.rfid_tag,
                    'drug_name': drug.drug_name,
                    'quantity': drug.quantity,
                    'status': drug.status,
                    'updated_at': drug.updated_at.isoformat(),
                }
            })
            
        except DrugInventory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Drug not found with this RFID tag',
                'rfid_tag': rfid_tag
            }, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Patient Management Views
@csrf_exempt
def get_patient_list_view(request):
    """Get list of all patients"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import Patient
        
        patients = Patient.objects.all().order_by('-created_at')
        patient_list = []
        
        for patient in patients:
            patient_list.append({
                'id': patient.id,
                'patient_id': patient.patient_id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'full_name': patient.full_name,
                'age': patient.age,
                'gender': patient.gender,
                'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                'address': patient.address,
                'phone_number': patient.phone_number,
                'created_at': patient.created_at.isoformat(),
            })
        
        return JsonResponse({
            'patients': patient_list,
            'total_count': len(patient_list)
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_patient_details_view(request, patient_id):
    """Get patient details"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import Patient
        
        patient = Patient.objects.get(id=patient_id)
        
        return JsonResponse({
            'patient': {
                'id': patient.id,
                'patient_id': patient.patient_id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'full_name': patient.full_name,
                'age': patient.age,
                'gender': patient.gender,
                'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                'address': patient.address,
                'phone_number': patient.phone_number,
                'metadata': patient.metadata,
                'created_at': patient.created_at.isoformat(),
                'updated_at': patient.updated_at.isoformat(),
            }
        })
    
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def verify_patient_view(request):
    """Verify patient identity"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import Patient
        
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        verification_method = data.get('verification_method', 'manual')
        
        if not patient_id:
            return JsonResponse({'error': 'Patient ID is required'}, status=400)
        
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            
            # Simulate verification process
            verification_result = {
                'success': True,
                'verified': True,
                'patient_id': patient.patient_id,
                'patient_name': patient.full_name,
                'verification_method': verification_method,
                'verification_timestamp': timezone.now().isoformat(),
                'message': 'Patient identity verified successfully'
            }
            
            return JsonResponse(verification_result)
            
        except Patient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'verified': False,
                'patient_id': patient_id,
                'message': 'Patient not found'
            }, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Administration Records Views
@csrf_exempt
def record_administration_view(request):
    """Record drug administration"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import AdministrationRecord, Patient, DrugInventory
        
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        rfid_tag = data.get('rfid_tag')
        administered_by = data.get('administered_by', 'Unknown')
        dosage_administered = data.get('dosage_administered')
        route = data.get('route')
        notes = data.get('notes', '')
        verification_method = data.get('verification_method', 'manual')
        
        if not patient_id or not rfid_tag:
            return JsonResponse({'error': 'Patient ID and RFID tag are required'}, status=400)
        
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            drug = DrugInventory.objects.get(rfid_tag=rfid_tag)
            
            # Create administration record
            administration = AdministrationRecord.objects.create(
                patient=patient,
                drug=drug,
                administered_by=administered_by,
                administration_time=timezone.now(),
                dosage_administered=dosage_administered,
                route=route,
                status='ADMINISTERED',
                notes=notes,
                verification_method=verification_method
            )
            
            # Update drug quantity
            if drug.quantity > 0:
                drug.quantity -= 1
                if drug.quantity <= 0:
                    drug.status = 'OUT_OF_STOCK'
                elif drug.quantity <= 10:
                    drug.status = 'LOW_STOCK'
                drug.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Administration recorded successfully',
                'administration': {
                    'id': administration.id,
                    'patient_name': patient.full_name,
                    'drug_name': drug.drug_name,
                    'administered_by': administration.administered_by,
                    'administration_time': administration.administration_time.isoformat(),
                    'dosage_administered': administration.dosage_administered,
                    'route': administration.route,
                    'status': administration.status,
                }
            })
            
        except (Patient.DoesNotExist, DrugInventory.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'message': f'Patient or drug not found: {str(e)}'
            }, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_administration_history_view(request):
    """Get administration history"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import AdministrationRecord
        
        # Get query parameters
        patient_id = request.GET.get('patient_id')
        drug_name = request.GET.get('drug_name')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        administrations = AdministrationRecord.objects.all().select_related('patient', 'drug')
        
        if patient_id:
            administrations = administrations.filter(patient__patient_id=patient_id)
        if drug_name:
            administrations = administrations.filter(drug__drug_name__icontains=drug_name)
        if date_from:
            administrations = administrations.filter(administration_time__gte=date_from)
        if date_to:
            administrations = administrations.filter(administration_time__lte=date_to)
        
        administration_list = []
        for admin in administrations:
            administration_list.append({
                'id': admin.id,
                'patient_name': admin.patient.full_name,
                'drug_name': admin.drug.drug_name,
                'administered_by': admin.administered_by,
                'administration_time': admin.administration_time.isoformat(),
                'scheduled_time': admin.scheduled_time.isoformat() if admin.scheduled_time else None,
                'dosage_administered': admin.dosage_administered,
                'route': admin.route,
                'status': admin.status,
                'notes': admin.notes,
                'verification_method': admin.verification_method,
            })
        
        return JsonResponse({
            'administrations': administration_list,
            'total_count': len(administration_list)
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Device Management Views
@csrf_exempt
def get_rfid_status_view(request):
    """Get RFID device status"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import DeviceStatus
        
        # Get RFID devices
        rfid_devices = DeviceStatus.objects.filter(device_type='RFID_READER')
        
        device_list = []
        for device in rfid_devices:
            device_list.append({
                'device_id': device.device_id,
                'device_name': device.device_name,
                'status': device.status,
                'battery_level': device.battery_level,
                'last_connected': device.last_connected.isoformat() if device.last_connected else None,
                'connection_status': device.connection_status,
                'error_message': device.error_message,
            })
        
        return JsonResponse({
            'rfid_devices': device_list,
            'total_count': len(device_list),
            'summary': {
                'online': rfid_devices.filter(status='ONLINE').count(),
                'offline': rfid_devices.filter(status='OFFLINE').count(),
                'error': rfid_devices.filter(status='ERROR').count(),
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def connect_bluetooth_device_view(request):
    """Connect to Bluetooth device"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import DeviceStatus
        
        data = json.loads(request.body)
        device_address = data.get('device_address')
        device_name = data.get('device_name', 'Unknown Device')
        
        if not device_address:
            return JsonResponse({'error': 'Device address is required'}, status=400)
        
        # Simulate connection process
        device_id = f"BT_{device_address.replace(':', '')}"
        
        # Create or update device status
        device, created = DeviceStatus.objects.get_or_create(
            device_id=device_id,
            defaults={
                'device_type': 'BLUETOOTH_DEVICE',
                'device_name': device_name,
                'status': 'ONLINE',
                'last_connected': timezone.now(),
                'connection_status': 'Connected successfully',
                'battery_level': random.randint(20, 100),
            }
        )
        
        if not created:
            device.status = 'ONLINE'
            device.last_connected = timezone.now()
            device.connection_status = 'Reconnected successfully'
            device.battery_level = random.randint(20, 100)
            device.error_message = ''
            device.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Bluetooth device connected successfully',
            'device': {
                'device_id': device.device_id,
                'device_name': device.device_name,
                'status': device.status,
                'battery_level': device.battery_level,
                'connection_status': device.connection_status,
                'last_connected': device.last_connected.isoformat(),
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_bluetooth_devices_view(request):
    """Get list of Bluetooth devices"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from .models import DeviceStatus
        
        # Get Bluetooth devices
        bluetooth_devices = DeviceStatus.objects.filter(device_type='BLUETOOTH_DEVICE')
        
        device_list = []
        for device in bluetooth_devices:
            device_list.append({
                'device_id': device.device_id,
                'device_name': device.device_name,
                'status': device.status,
                'battery_level': device.battery_level,
                'last_connected': device.last_connected.isoformat() if device.last_connected else None,
                'connection_status': device.connection_status,
                'error_message': device.error_message,
            })
        
        return JsonResponse({
            'bluetooth_devices': device_list,
            'total_count': len(device_list),
            'summary': {
                'online': bluetooth_devices.filter(status='ONLINE').count(),
                'offline': bluetooth_devices.filter(status='OFFLINE').count(),
                'error': bluetooth_devices.filter(status='ERROR').count(),
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
