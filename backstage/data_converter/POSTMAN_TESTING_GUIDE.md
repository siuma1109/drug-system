# Postman Testing Guide for Drug System Conversion API

## API Base URL
```
http://localhost:8000/api/converter/
```

## 1. Create Conversion (POST)

### JSON Body Request
**URL:** `POST /api/converter/conversions`

**Headers:**
- `Content-Type: application/json`

**Body (JSON):**
```json
{
    "conversion_type": "XML",
    "source_data": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<prescriptions>\n    <prescription>\n        <patient>\n            <id>PAT001</id>\n            <name>John Doe</name>\n            <age>45</age>\n            <gender>M</gender>\n        </patient>\n        <medication>\n            <drug_name>Aspirin</drug_name>\n            <dosage>81mg</dosage>\n            <strength>81mg</strength>\n            <quantity>30</quantity>\n            <instructions>Take one tablet daily</instructions>\n            <prescription_id>RX001</prescription_id>\n        </medication>\n    </prescription>\n</prescriptions>"
}
```

### Form Data Request
**URL:** `POST /api/converter/conversions`

**Headers:**
- `Content-Type: multipart/form-data`

**Body (Form Data):**
- `conversion_type`: `XML`
- `source_data`: `<?xml version="1.0" encoding="UTF-8"?><prescriptions><prescription><patient><id>PAT001</id><name>John Doe</name><age>45</age><gender>M</gender></patient><medication><drug_name>Aspirin</drug_name><dosage>81mg</dosage><strength>81mg</strength><quantity>30</quantity><instructions>Take one tablet daily</instructions><prescription_id>RX001</prescription_id></medication></prescription></prescriptions>`

### HL7 Example
**Body (JSON):**
```json
{
    "conversion_type": "HL7",
    "source_data": "MSH|^~\\&|HIS|LAB|LAB|202401011200||ORM^O01|MSG00001|P|2.3\\rPID|||PAT001||DOE^JOHN||19790101|M|||123 MAIN ST^^ANYTOWN^CA^12345\\rPV1||I|ICU^^HOSPITAL|||123456^DOCTOR^JOHN\\rORC|NW|RX001|RX001|||QD|1|20240101\\rRXO|ASPIRIN^81MG^TAB|30|TAB|||Take one tablet daily"
}
```

## 2. Get Conversion List (GET)

**URL:** `GET /api/converter/conversions/list`

**Response:**
```json
{
    "conversions": [
        {
            "conversion_id": "uuid-here",
            "conversion_type": "XML",
            "status": "PENDING",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "drug_records_count": 0
        }
    ],
    "total_count": 1
}
```

## 3. Get Conversion Status (GET)

**URL:** `GET /api/converter/conversions/{conversion_id}/status`

**Response:**
```json
{
    "conversion_id": "uuid-here",
    "status": "PENDING",
    "conversion_type": "XML",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "drug_records_count": 0,
    "error_message": null
}
```

## 4. Process Conversion (POST)

**URL:** `POST /api/converter/conversions/{conversion_id}/process`

**Response:**
```json
{
    "conversion_id": "uuid-here",
    "status": "COMPLETED",
    "drug_records_count": 1,
    "processing_time": 0.5,
    "parsed_data": {
        "patient": {
            "id": "PAT001",
            "name": "John Doe",
            "age": "45",
            "gender": "M"
        },
        "medication": {
            "drug_name": "Aspirin",
            "dosage": "81mg",
            "strength": "81mg",
            "quantity": 30,
            "instructions": "Take one tablet daily",
            "prescription_id": "RX001"
        }
    }
}
```

## 5. Get Drug Records (GET)

**URL:** `GET /api/converter/conversions/{conversion_id}/drug-records`

**Response:**
```json
{
    "conversion_id": "uuid-here",
    "drug_records": [
        {
            "id": 1,
            "drug_name": "Aspirin",
            "dosage": "81mg",
            "strength": "81mg",
            "quantity": 30,
            "patient_id": "PAT001",
            "prescription_id": "RX001",
            "created_at": "2024-01-01T12:00:00Z",
            "metadata": {
                "patient_name": "John Doe",
                "age": "45",
                "gender": "M",
                "instructions": "Take one tablet daily"
            }
        }
    ],
    "total_count": 1
}
```

## Testing Workflow

1. **Start Django Server:**
   ```bash
   python manage.py runserver
   ```

2. **Create Conversion:**
   - Use POST `/api/converter/conversions` with XML or HL7 data

3. **Check Status:**
   - Use GET `/api/converter/conversions/{conversion_id}/status`

4. **Process Conversion:**
   - Use POST `/api/converter/conversions/{conversion_id}/process`

5. **View Results:**
   - Use GET `/api/converter/conversions/{conversion_id}/drug-records`

## Database Storage

The system stores all conversion details in the following database tables:

### data_conversions table:
- `conversion_id`: Unique identifier
- `conversion_type`: XML or HL7
- `source_data`: Original source data
- `status`: PENDING, PROCESSING, COMPLETED, FAILED
- `converted_data`: Parsed JSON data
- `error_message`: Error details if failed
- `created_at`, `updated_at`: Timestamps

### drug_records table:
- `drug_name`: Name of the drug
- `dosage`: Dosage information
- `strength`: Drug strength
- `quantity`: Quantity prescribed
- `patient_id`: Patient identifier
- `prescription_id`: Prescription identifier
- `metadata`: Additional patient and prescription details
- `conversion_id`: Link to parent conversion

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (invalid data)
- `404`: Not Found
- `405`: Method Not Allowed
- `500`: Internal Server Error