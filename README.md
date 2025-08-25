# Drug System

A comprehensive medical data processing system that converts XML and HL7 medical data into structured database records, designed for healthcare data integration and drug management.

## Key Features

### 🏥 Medical Data Processing
- **XML Parser**: Processes XML prescription data and extracts drug information
- **HL7 Parser**: Handles HL7 medical messages for immunization and drug administration records
- **Patient Demographics**: Extracts and stores patient information from medical records
- **Drug Records**: Creates comprehensive drug administration and prescription records

### 🛡️ Enterprise-Grade Architecture
- **SOLID Principles**: Clean, maintainable code following software engineering best practices
- **REST API**: Complete RESTful API for data conversion operations
- **Database Storage**: SQLite database with proper data models and relationships
- **Error Handling**: Comprehensive error handling and validation
- **Logging**: Detailed logging for conversion operations and debugging

### 📊 Data Capabilities
- **Real Data Extraction**: Processes actual medical record numbers, patient names, and drug information
- **Date Formatting**: Proper conversion of medical date formats (YYYYMMDD → YYYY-MM-DD)
- **Embedded Data**: Handles complex HL7 messages with embedded patient segments
- **Metadata Tracking**: Complete source tracking and audit trails

## System Architecture

The system follows SOLID principles with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   REST API      │    │   Business      │    │   Data Access   │
│   Layer         │◄──►│   Logic Layer   │◄──►│   Layer         │
│                 │    │                 │    │                 │
│ • Django Views  │    │ • Processors    │    │ • Repositories  │
│ • URL Routing   │    │ • Managers      │    │ • Models        │
│ • Validation    │    │ • Services      │    │ • Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   Processing    │    │   Storage       │
│   Interface     │    │   Engine        │    │   Layer         │
│                 │    │                 │    │                 │
│ • HTTP Requests │    │ • XML Parser    │    │ • SQLite        │
│ • JSON Responses│    │ • HL7 Parser    │    │ • Data Models   │
│ • Error Handling│    │ • Validation    │    │ • Relationships │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Data Converters
- **XML Parser**: Processes XML prescription data with structured drug information
- **HL7 Parser**: Handles complex HL7 medical messages including immunization records
- **Patient Data Extraction**: Extracts demographics from embedded PID segments
- **Drug Record Creation**: Creates comprehensive drug administration records

### 2. Database Models
- **Patient Model**: Stores patient demographics, medical record numbers, and contact information
- **DrugRecord Model**: Tracks drug administration, dosage, and prescription details
- **DataConversion Model**: Manages conversion processes and status tracking
- **Metadata**: Complete audit trails and source tracking

### 3. API Endpoints
- `POST /api/conversions/` - Create new data conversion
- `POST /api/conversions/{id}/process/` - Process conversion data
- `GET /api/conversions/{id}/status/` - Check conversion status
- `GET /api/conversions/{id}/drug-records/` - Retrieve processed drug records
- `GET /api/conversions/list/` - List all conversions

## Data Processing Examples

### XML Prescription Processing
```xml
<prescription>
  <patient>
    <name>John Doe</name>
    <id>PAT001</id>
  </patient>
  <medication>
    <name>Amoxicillin</name>
    <dosage>500mg</dosage>
    <quantity>30</quantity>
  </medication>
</prescription>
```

### HL7 Immunization Processing
```
MSH|^~\&|SENDING_APPLICATION|SENDING_FACILITY|RECEIVING_APPLICATION|RECEIVING_FACILITY|201305171259|12|VXU^V04|2244455|P|2.3||||||
PID|1||123456||DUCK^DAISY^L||19690912|F|||123 NORTHWOOD ST APT 9^^NEW CITY^NC^27262-9944|||||||||||||||||||
ORC|OK|664443333^EEE|33994499||||^^^20220301||20220301101531|DAVE^DAVID^DAVE^D||444999^DAVID JR^JAMES^DAVID^^^^^LAB&PROVID&ISO^L^^^PROVID^FACILITY_CODE&1.2.888.444999.1.13.308.2.7.2.696969&ISO|1021209999^^^10299^^^^^WD999 09 LABORATORY NAME|^^^^^333^8022999||||CCC528Y73^CCC-528Y73||||||
RXA|0|999|20220301|20220301|217^PFIZER 12 YEARS \T\ UP SARS-COV-2 VACCINE^LIM_CVX|0.3|ML||00^New immunization record^NIP001|459920^DUCK^DAISY^L^^^^^LAB&PROVID&ISO^L^^^PROVID^FACILITY_CODE&1.2.888.444999.1.13.308.2.7.2.696969&ISO|1021209999^^^10299^^^^^WD999 09 LABORATORY NAME||||FK9999|20220531|PPR|||CP|A|20220301101531
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163|||
```

## Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2+

### Setup
```bash
# Navigate to project directory
cd drug-system

# Install dependencies
sudo apt install python3-django

# Run migrations
python3 backstage/manage.py makemigrations
python3 backstage/manage.py migrate

# Create superuser
python3 backstage/manage.py createsuperuser

# Run development server
python3 backstage/manage.py runserver
```

### Testing the System
```bash
# Run HL7 parser test
python3 backstage/data_converter/test_hl7_parser.py

# Run Django test suite
python3 backstage/manage.py test data_converter
```

## API Usage

### Create Conversion
```bash
curl -X POST http://localhost:8000/api/conversions/ \
  -H "Content-Type: application/json" \
  -d '{
    "conversion_type": "HL7",
    "source_data": "MSH|^~\\&|EPIC|..."
  }'
```

### Process Conversion
```bash
curl -X POST http://localhost:8000/api/conversions/{id}/process/
```

### Check Status
```bash
curl http://localhost:8000/api/conversions/{id}/status/
```

## Project Structure

```
drug-system/
├── README.md
└── backstage/
    ├── manage.py
    ├── db.sqlite3
    ├── app/                    # Django app configuration
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── data_converter/         # Main application
        ├── models.py           # Database models
        ├── views.py            # REST API views
        ├── urls.py             # URL routing
        ├── admin.py            # Django admin
        ├── services/           # Business logic
        │   ├── hl7_parser.py   # HL7 message parser
        │   ├── xml_parser.py   # XML data parser
        │   ├── processor.py    # Main processor
        │   ├── repositories.py # Data access
        │   └── interfaces.py  # Abstract interfaces
        └── tests.py            # Test suite
```

## Key Achievements

✅ **Real Data Processing**: Successfully processes actual medical records with real patient IDs and drug names

✅ **Complex HL7 Handling**: Handles embedded PID segments and complex immunization messages

✅ **Date Format Conversion**: Properly converts medical date formats (YYYYMMDD → YYYY-MM-DD)

✅ **Complete Records**: Creates both patient and drug records with proper relationships

✅ **Enterprise Architecture**: Clean, maintainable code following SOLID principles

✅ **Comprehensive Testing**: Full test coverage with real medical data validation

## Security Features

- **Input Validation**: Comprehensive validation of all incoming data
- **SQL Injection Prevention**: Django ORM protects against SQL injection
- **CSRF Protection**: Built-in Django CSRF protection
- **Error Sanitization**: Secure error message handling
- **Audit Trails**: Complete logging of all operations

## Performance Optimizations

- **Efficient Parsing**: Optimized algorithms for XML and HL7 processing
- **Database Transactions**: Proper transaction management for data integrity
- **Memory Management**: Minimal memory footprint for large datasets
- **Asynchronous Ready**: Architecture supports async processing

## Extensibility

The system is designed for easy extension:

- **New Parsers**: Add new data format parsers by implementing the ParserInterface
- **New Data Sources**: Extend repositories for additional data storage options
- **New API Endpoints**: Follow existing patterns for new functionality
- **New Validation Rules**: Add validation logic in the utils module

## Mobile Integration

### Android Companion App

A dedicated Android application is being developed to provide mobile access to the Smart Drug Cabinet System. The app will enhance the system with real-time drug management and hardware integration capabilities.

#### Key Features

- **Real-time Drug Inventory**: View current drug stock levels and expiration dates
- **RFID Scanning**: Scan drug packages using integrated RFID technology
- **Bluetooth Device Integration**: Connect to medical devices for vital signs monitoring
- **Patient Verification**: Verify patient identity before drug administration
- **Offline Mode**: Continue operations without network connectivity
- **Push Notifications**: Receive alerts for low stock, expiring drugs, and administration reminders

#### Technology Stack

- **Development Environment**: Android Studio with Java
- **Architecture**: MVVM (Model-View-ViewModel) pattern
- **Networking**: Retrofit for API communication
- **Database**: Room database for local storage
- **Hardware Integration**: Android Bluetooth API, RFID SDK integration
- **UI/UX**: Material Design components with custom themes

#### API Integration

The Android app communicates with the Django backend through RESTful APIs:

```
Base URL: http://localhost:8000/api/

Authentication:
POST /auth/login/ - User authentication
POST /auth/refresh/ - Token refresh

Drug Management:
GET /drugs/inventory/ - Get current drug inventory
POST /drugs/scan/ - Scan drug via RFID
PUT /drugs/update-stock/ - Update drug quantities

Patient Management:
GET /patients/list/ - Get patient list
GET /patients/{id}/ - Get patient details
POST /patients/verify/ - Verify patient identity

Administration:
POST /administration/record/ - Record drug administration
GET /administration/history/ - Get administration history

Device Management:
GET /devices/rfid/status/ - RFID device status
POST /devices/bluetooth/connect/ - Connect Bluetooth device
GET /devices/bluetooth/list/ - List paired devices
```

### 🌐 API Endpoints Reference

#### Drug Management APIs
```bash
GET    /api/drugs/inventory           # Get current drug inventory
POST   /api/drugs/scan               # Scan drug via RFID
PUT    /api/drugs/update-stock        # Update drug quantities
```

#### Patient Management APIs
```bash
GET    /api/patients/list            # Get patient list
GET    /api/patients/{id}            # Get patient details
POST   /api/patients/verify          # Verify patient identity
```

#### Administration APIs
```bash
POST   /api/administration/record     # Record drug administration
GET    /api/administration/history    # Get administration history
```

#### Device Management APIs
```bash
GET    /api/devices/rfid/status       # Get RFID device status
POST   /api/devices/bluetooth/connect # Connect Bluetooth device
GET    /api/devices/bluetooth/list    # List paired devices
```
