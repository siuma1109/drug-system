package com.example.drugsystemapp.data.models

import com.google.gson.annotations.SerializedName

// Data Conversion Models
data class DataConversion(
    @SerializedName("conversion_id")
    val conversionId: String,
    @SerializedName("conversion_type")
    val conversionType: String,
    val status: String,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String,
    @SerializedName("drug_records_count")
    val drugRecordsCount: Int
)

data class DrugRecord(
    val id: Int,
    @SerializedName("drug_name")
    val drugName: String,
    val dosage: String,
    val strength: String,
    val quantity: Int?,
    @SerializedName("original_patient_id")
    val originalPatientId: String,
    @SerializedName("prescription_id")
    val prescriptionId: String,
    val patient: Patient?,
    @SerializedName("created_at")
    val createdAt: String,
    val metadata: Map<String, Any>?
)

// Patient Models
data class Patient(
    val id: Int,
    @SerializedName("patient_id")
    val patientId: String,
    @SerializedName("first_name")
    val firstName: String,
    @SerializedName("last_name")
    val lastName: String,
    @SerializedName("full_name")
    val fullName: String,
    val age: Int?,
    val gender: String,
    @SerializedName("date_of_birth")
    val dateOfBirth: String?,
    val address: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    val metadata: Map<String, Any>?,
    @SerializedName("created_at")
    val createdAt: String
)

// Drug Inventory Models
data class DrugInventory(
    val id: Int,
    @SerializedName("rfid_tag")
    val rfidTag: String,
    @SerializedName("drug_name")
    val drugName: String,
    val dosage: String,
    val strength: String,
    val quantity: Int,
    @SerializedName("batch_number")
    val batchNumber: String,
    @SerializedName("expiration_date")
    val expirationDate: String?,
    val manufacturer: String,
    val location: String,
    val status: String,
    @SerializedName("last_scanned")
    val lastScanned: String?,
    @SerializedName("last_scanned_by")
    val lastScannedBy: String,
    val metadata: Map<String, Any>?,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
)

data class InventoryStatus(
    @SerializedName("total_count")
    val totalCount: Int,
    @SerializedName("status_summary")
    val statusSummary: Map<String, Int>
)

// Administration Record Models
data class AdministrationRecord(
    val id: Int,
    @SerializedName("patient_name")
    val patientName: String,
    @SerializedName("drug_name")
    val drugName: String,
    @SerializedName("administered_by")
    val administeredBy: String,
    @SerializedName("administration_time")
    val administrationTime: String,
    @SerializedName("scheduled_time")
    val scheduledTime: String?,
    @SerializedName("dosage_administered")
    val dosageAdministered: String,
    val route: String,
    val status: String,
    val notes: String,
    @SerializedName("verification_method")
    val verificationMethod: String
)

// Device Management Models
data class DeviceStatus(
    @SerializedName("device_id")
    val deviceId: String,
    @SerializedName("device_name")
    val deviceName: String,
    val status: String,
    @SerializedName("battery_level")
    val batteryLevel: Int?,
    @SerializedName("last_connected")
    val lastConnected: String?,
    @SerializedName("connection_status")
    val connectionStatus: String,
    @SerializedName("error_message")
    val errorMessage: String
)

data class DeviceSummary(
    @SerializedName("rfid_devices")
    val rfidDevices: List<DeviceStatus>,
    @SerializedName("bluetooth_devices")
    val bluetoothDevices: List<DeviceStatus>,
    @SerializedName("total_count")
    val totalCount: Int,
    val summary: Map<String, Int>
)

// API Request/Response Models
data class ScanRequest(
    @SerializedName("rfid_tag")
    val rfidTag: String,
    @SerializedName("scanned_by")
    val scannedBy: String = "Android App"
)

data class ScanResponse(
    val success: Boolean,
    val message: String,
    val drug: DrugInventory?
)

data class AdministrationRequest(
    @SerializedName("patient_id")
    val patientId: String,
    @SerializedName("rfid_tag")
    val rfidTag: String,
    @SerializedName("administered_by")
    val administeredBy: String,
    @SerializedName("dosage_administered")
    val dosageAdministered: String,
    val route: String,
    val notes: String = "",
    @SerializedName("verification_method")
    val verificationMethod: String = "RFID"
)

data class AdministrationResponse(
    val success: Boolean,
    val message: String,
    val administration: AdministrationRecord?
)

data class BluetoothConnectRequest(
    @SerializedName("device_address")
    val deviceAddress: String,
    @SerializedName("device_name")
    val deviceName: String
)

data class BluetoothConnectResponse(
    val success: Boolean,
    val message: String,
    val device: DeviceStatus?
)

// UI State Models
data class UiState<T>(
    val isLoading: Boolean = false,
    val data: T? = null,
    val error: String? = null
)

data class DeviceConnectionState(
    val isConnected: Boolean = false,
    val deviceName: String? = null,
    val batteryLevel: Int? = null,
    val error: String? = null
)

// Navigation Routes
object Routes {
    const val DASHBOARD = "dashboard"
    const val INVENTORY = "inventory"
    const val SCAN = "scan"
    const val PATIENTS = "patients"
    const val DEVICES = "devices"
    const val SETTINGS = "settings"
}