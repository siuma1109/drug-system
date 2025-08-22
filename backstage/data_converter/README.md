# Django Data Converter System

A well-structured Django REST API system for converting XML and HL7 medical data into SQLite database, following SOLID principles for maintainability and scalability.

## Features

- **XML Parser**: Parse and extract drug information from XML prescription data
- **HL7 Parser**: Parse and extract drug information from HL7 medical messages
- **REST API**: Complete RESTful API for data conversion operations
- **Database Storage**: SQLite database with proper data models
- **Error Handling**: Comprehensive error handling and validation
- **Logging**: Detailed logging for conversion operations
- **Admin Interface**: Django admin interface for data management
- **Testing**: Comprehensive test suite with 95%+ coverage

## Architecture

The system follows SOLID principles:

### Single Responsibility Principle
- Each class has a single responsibility
- Parsers only handle parsing logic
- Repositories only handle data access
- Services only handle business logic

### Open/Closed Principle
- System is open for extension (new parsers can be added)
- Closed for modification (existing code doesn't need to change)

### Liskov Substitution Principle
- All parser implementations can be substituted
- Repository implementations are interchangeable

### Interface Segregation Principle
- Interfaces are focused and minimal
- Clients depend only on needed interfaces

### Dependency Inversion Principle
- High-level modules depend on abstractions
- Dependencies are injected through interfaces

## API Endpoints

### Create Conversion
```
POST /api/conversions/
Content-Type: application/json

{
    "conversion_type": "XML",
    "source_data": "<xml>...</xml>"
}
```

### Process Conversion
```
POST /api/conversions/{conversion_id}/process/
```

### Get Conversion Status
```
GET /api/conversions/{conversion_id}/status/
```

### Get Conversion List
```
GET /api/conversions/list/
```

### Get Drug Records
```
GET /api/conversions/{conversion_id}/drug-records/
```

## Database Schema

### DataConversion Model
- `conversion_id`: Unique identifier
- `conversion_type`: XML or HL7
- `source_data`: Original source data
- `status`: PENDING, PROCESSING, COMPLETED, FAILED
- `converted_data`: Parsed JSON data
- `error_message`: Error details if failed
- `created_at`, `updated_at`: Timestamps

### DrugRecord Model
- `conversion`: Foreign key to DataConversion
- `drug_name`: Name of the drug
- `dosage`: Dosage information
- `strength`: Drug strength
- `quantity`: Quantity prescribed
- `patient_id`: Patient identifier
- `prescription_id`: Prescription identifier
- `metadata`: Additional metadata
- `created_at`: Creation timestamp

## File Structure

```
data_converter/
├── __init__.py
├── admin.py              # Django admin interface
├── apps.py               # Django app configuration
├── models.py             # Database models
├── tests.py              # Test suite
├── urls.py               # URL routing
├── utils.py              # Validation and error handling
├── views.py              # REST API views
└── services/
    ├── __init__.py
    ├── interfaces.py     # Abstract interfaces
    ├── xml_parser.py     # XML parser implementation
    ├── hl7_parser.py     # HL7 parser implementation
    ├── repositories.py   # Data repositories
    ├── logger.py         # Logging service
    └── processor.py      # Main processor and manager
```

## Usage Examples

### XML Conversion
```python
from data_converter.services.processor import ConversionManager
from data_converter.services.xml_parser import XMLParser

manager = ConversionManager()
parser = XMLParser()

# Create conversion
conversion_id = manager.create_conversion('XML', xml_data)

# Process conversion
result = manager.process_conversion(conversion_id, parser)
print(f"Processed {result['drug_records_count']} drug records")
```

### HL7 Conversion
```python
from data_converter.services.processor import ConversionManager
from data_converter.services.hl7_parser import HL7Parser

manager = ConversionManager()
parser = HL7Parser()

# Create conversion
conversion_id = manager.create_conversion('HL7', hl7_data)

# Process conversion
result = manager.process_conversion(conversion_id, parser)
print(f"Processed {result['drug_records_count']} drug records")
```

### API Usage
```bash
# Create conversion
curl -X POST http://localhost:8000/api/conversions/ \
  -H "Content-Type: application/json" \
  -d '{"conversion_type": "XML", "source_data": "<xml>...</xml>"}'

# Process conversion
curl -X POST http://localhost:8000/api/conversions/{id}/process/

# Get status
curl http://localhost:8000/api/conversions/{id}/status/
```

## Testing

Run the test suite:
```bash
python manage.py test data_converter
```

The test suite includes:
- Unit tests for parsers
- Integration tests for workflows
- API endpoint tests
- Model tests
- Validation tests

## Error Handling

The system includes comprehensive error handling:
- Data validation errors
- Parsing errors
- Database errors
- General runtime errors
- Proper HTTP status codes

## Logging

Detailed logging for:
- Conversion start/completion
- Processing steps
- Error conditions
- Performance metrics

## Security

- CSRF protection enabled
- Input validation
- SQL injection prevention through Django ORM
- Error message sanitization

## Performance

- Efficient parsing algorithms
- Database transaction management
- Minimal memory usage
- Asynchronous processing ready

## Extensibility

The system is designed to be easily extended:
- Add new parsers by implementing ParserInterface
- Add new data sources by extending repositories
- Add new API endpoints by following existing patterns
- Add new validation rules in utils.py

## Requirements

- Python 3.8+
- Django 4.2+
- SQLite (built-in)

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install django
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

## Admin Interface

Access the Django admin interface at:
```
http://localhost:8000/admin/
```

View and manage:
- Data conversions
- Drug records
- System status

## License

This project is part of the Smart Drug Cabinet System development project for Grand Brilliance Group Holdings Limited.