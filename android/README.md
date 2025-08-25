# Smart Drug Cabinet System - Android App

## 🏥 Overview
A comprehensive Smart Drug Cabinet System mobile application built with modern Android development practices. This app integrates RFID/QR code scanning, Bluetooth/WiFi connectivity, and HL7 medical data standards to provide a complete medication management solution.

## 🚀 Features

### 📱 Core Functionality
- **Dashboard**: Real-time statistics and quick actions
- **Drug Inventory**: Complete inventory management with RFID tracking
- **Multi-Modal Scanning**: QR code, RFID/NFC, and manual input
- **Drug Administration**: Electronic medication administration records (eMAR)
- **Patient Management**: Patient database and verification
- **Device Management**: RFID readers, Bluetooth devices, and WiFi monitoring

### 🔧 Technical Features
- **RFID Integration**: Contactless drug tracking and scanning
- **Bluetooth Connectivity**: Wireless device management
- **WiFi Monitoring**: Network quality assessment
- **HL7 Support**: Healthcare data exchange standards
- **Biometric Authentication**: Secure access control
- **Real-time Sync**: Cloud-based data synchronization

## 🛠️ Technology Stack

### Frontend
- **Kotlin**: Primary programming language
- **Jetpack Compose**: Modern UI framework
- **Material Design 3**: Latest design system
- **Coroutines**: Asynchronous programming
- **Flow**: Reactive data streams

### Backend Integration
- **Retrofit**: Network communication
- **OkHttp**: HTTP client with logging
- **Gson**: JSON parsing
- **Room Database**: Local persistence
- **DataStore**: Preferences storage

### Hardware Integration
- **NFC/RFID**: Contactless scanning
- **Camera**: QR code scanning
- **Bluetooth**: Device connectivity
- **Biometric**: Authentication

## 📦 Installation

### Prerequisites
- Android Studio Arctic Fox or later
- Kotlin 1.8.0+
- Android Gradle Plugin 8.0+
- Minimum SDK 24 (Android 7.0)
- Target SDK 36 (Android 13)

### Build Instructions
1. Clone the repository
2. Start the Django backend server:
   ```bash
   cd backstage
   python manage.py runserver 0.0.0.0:8000
   ```
3. Update `ApiConfig.kt` with your network configuration if using physical device
4. Open in Android Studio
5. Sync Gradle dependencies
6. Build the project: `./gradlew assembleDebug`
7. Install on device or emulator

### Backend Setup
The Django backend must be running for the app to function properly:

1. Navigate to the `backstage` directory
2. Install dependencies: `pip install -r requirements.txt` (if available)
3. Run migrations: `python manage.py migrate`
4. Start the server: `python manage.py runserver 0.0.0.0:8000`
5. The API will be available at `http://localhost:8000/api/`

For physical device testing, update the `DEVICE_BASE_URL` in `ApiConfig.kt` with your computer's local IP address.

## 🔐 Permissions Required

The app requires the following permissions:
- **Camera**: For QR code scanning
- **Bluetooth**: Device connectivity
- **NFC**: RFID tag reading
- **Internet**: API communication
- **Biometric**: Authentication
- **Storage**: Data caching

## 🏗️ Architecture

### MVVM Pattern
```
├── UI Layer (Compose)
├── ViewModel Layer
├── Repository Layer
├── Data Source Layer
└── Domain Layer
```

### Key Components
- **Screens**: UI components (Dashboard, Inventory, Scan, etc.)
- **ViewModels**: State management and business logic
- **Repositories**: Data abstraction
- **Services**: Network and hardware integration
- **Models**: Data structures

## 📊 API Integration

### Backend Configuration
The Android app integrates with the Django backend API. The base URL is configured in `ApiConfig.kt`:

- **Emulator**: `http://10.0.2.2:8000/api/`
- **Physical Device**: `http://192.168.1.100:8000/api/` (update with your local IP)

### API Endpoints

#### Data Conversion
- **POST** `conversions` - Create new data conversion
- **GET** `conversions/list` - Get all conversions
- **GET** `conversions/{id}/status` - Get conversion status
- **POST** `conversions/{id}/process` - Process conversion
- **GET** `conversions/{id}/drug-records` - Get drug records

#### Drug Inventory
- **GET** `drugs/inventory` - Get drug inventory with filters
- **POST** `drugs/scan` - Scan drug via RFID
- **PUT** `drugs/update-stock` - Update drug stock

#### Patient Management
- **GET** `patients/list` - Get all patients
- **GET** `patients/{id}` - Get patient details
- **POST** `patients/verify` - Verify patient identity

#### Administration Records
- **POST** `administration/record` - Record drug administration
- **GET** `administration/history` - Get administration history

#### Device Management
- **GET** `devices/rfid/status` - Get RFID device status
- **POST** `devices/bluetooth/connect` - Connect Bluetooth device
- **GET** `devices/bluetooth/list` - Get Bluetooth devices

### Configuration
Update `ApiConfig.kt` to switch between emulator and physical device:
```kotlin
ApiConfig.setEnvironment(isEmulator = true) // or false for physical device
```

### Data Formats
- **JSON**: RESTful API communication
- **HL7**: Healthcare data exchange
- **XML**: Legacy system integration

## 🔒 Security Features

- **Biometric Authentication**: Fingerprint/face recognition
- **Data Encryption**: Protected health information
- **Audit Trail**: Complete activity logging
- **HIPAA Compliance**: Healthcare standards

## 🧪 Testing

### Unit Tests
- ViewModel logic
- Repository functions
- Utility methods

### Integration Tests
- API communication
- Database operations
- Hardware integration

### UI Tests
- User flows
- Screen navigation
- User interactions

## 📱 Screen Guide

### Dashboard
- Real-time inventory statistics
- Quick action buttons
- Device status overview
- Recent activity feed

### Inventory Management
- Drug list with search/filter
- Stock level monitoring
- Expiration date tracking
- Location-based organization

### Scanning
- QR code scanner
- RFID/NFC reader
- Manual input option
- Real-time validation

### Administration
- Patient selection
- Drug administration
- Dosage tracking
- History records

### Devices
- RFID reader status
- Bluetooth device list
- WiFi quality monitoring
- Connection management

## 🚨 Troubleshooting

### Common Issues
1. **Build Errors**: Ensure all dependencies are synced
2. **Permission Issues**: Check app permissions in settings
3. **Network Problems**: Verify backend server is running
4. **Hardware Issues**: Ensure device supports NFC/Bluetooth

### Debug Mode
Enable debug mode in `build.gradle.kts`:
```kotlin
buildConfigField("boolean", "DEBUG", "true")
```

## 📄 License

This project is part of the Smart Drug Cabinet System for Grand Brilliance Group Holdings Limited.

## 👨‍💻 Developer Notes

### Code Style
- Follow Kotlin coding conventions
- Use Material Design 3 components
- Implement proper error handling
- Write comprehensive documentation

### Performance
- Use coroutines for async operations
- Implement proper lifecycle management
- Optimize database queries
- Minimize network calls

### Accessibility
- Support screen readers
- Provide proper content descriptions
- Ensure color contrast compliance
- Support multiple screen sizes

---

**Built with ❤️ for Grand Brilliance Group Holdings Limited**