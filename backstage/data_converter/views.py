import json
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
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
