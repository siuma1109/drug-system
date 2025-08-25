package com.example.drugsystemapp.data.repository

import android.content.Context
import com.example.drugsystemapp.data.models.*
import com.example.drugsystemapp.data.network.ApiService
import com.example.drugsystemapp.data.network.RetrofitClient
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class DrugRepository(private val context: Context) {
    
    private val apiService: ApiService by lazy {
        RetrofitClient.getInstance(context).createService(ApiService::class.java)
    }
    
    // Data Conversion Operations
    suspend fun getConversionList(): Flow<UiState<List<DataConversion>>> = flow {
        emit(UiState(isLoading = true))
        try {
            val response = apiService.getConversionList()
            if (response.isSuccessful) {
                val data = response.body()
                val conversions = data?.get("conversions")?.let { items ->
                    if (items is List<*>) items.filterIsInstance<Map<String, Any>>() else emptyList()
                } ?: emptyList()
                val conversionList = conversions.map { mapToDataConversion(it) }
                emit(UiState(data = conversionList))
            } else {
                emit(UiState(error = "Failed to get conversion list: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    // Drug Inventory Operations
    suspend fun getDrugInventory(status: String? = null, location: String? = null): Flow<UiState<List<DrugInventory>>> = flow {
        emit(UiState(isLoading = true))
        try {
            val response = apiService.getDrugInventory(status, location)
            if (response.isSuccessful) {
                val data = response.body()
                val inventory = data?.get("inventory")?.let { items ->
                    if (items is List<*>) items.filterIsInstance<Map<String, Any>>() else emptyList()
                } ?: emptyList()
                val inventoryList = inventory.map { mapToDrugInventory(it) }
                emit(UiState(data = inventoryList))
            } else {
                emit(UiState(error = "Failed to get drug inventory: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    suspend fun scanDrug(rfidTag: String, scannedBy: String = "Android App"): Flow<UiState<DrugInventory>> = flow {
        emit(UiState(isLoading = true))
        try {
            val request = ScanRequest(rfidTag = rfidTag, scannedBy = scannedBy)
            val response = apiService.scanDrug(request)
            if (response.isSuccessful) {
                val scanResponse = response.body()
                if (scanResponse?.success == true) {
                    emit(UiState(data = scanResponse.drug))
                } else {
                    emit(UiState(error = scanResponse?.message ?: "Scan failed"))
                }
            } else {
                emit(UiState(error = "Failed to scan drug: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    suspend fun updateDrugStock(
        rfidTag: String,
        quantityChange: Int,
        operation: String = "add",
        updatedBy: String = "Android App"
    ): Flow<UiState<Map<String, Any>>> = flow {
        emit(UiState(isLoading = true))
        try {
            val request = mapOf(
                "rfid_tag" to rfidTag,
                "quantity_change" to quantityChange,
                "operation" to operation,
                "updated_by" to updatedBy
            )
            val response = apiService.updateDrugStock(request)
            if (response.isSuccessful) {
                val data = response.body()
                emit(UiState(data = data))
            } else {
                emit(UiState(error = "Failed to update drug stock: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    // Patient Management Operations
    suspend fun getPatientList(): Flow<UiState<List<Patient>>> = flow {
        emit(UiState(isLoading = true))
        try {
            val response = apiService.getPatientList()
            if (response.isSuccessful) {
                val data = response.body()
                val patients = data?.get("patients")?.let { items ->
                    if (items is List<*>) items.filterIsInstance<Map<String, Any>>() else emptyList()
                } ?: emptyList()
                val patientList = patients.map { mapToPatient(it) }
                emit(UiState(data = patientList))
            } else {
                emit(UiState(error = "Failed to get patient list: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    suspend fun verifyPatient(patientId: String): Flow<UiState<Boolean>> = flow {
        emit(UiState(isLoading = true))
        try {
            val request = mapOf("patient_id" to patientId, "verification_method" to "mobile_app")
            val response = apiService.verifyPatient(request)
            if (response.isSuccessful) {
                val data = response.body()
                val verified = data?.get("verified") as? Boolean ?: false
                emit(UiState(data = verified))
            } else {
                emit(UiState(error = "Failed to verify patient: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    // Administration Operations
    suspend fun recordAdministration(request: AdministrationRequest): Flow<UiState<AdministrationRecord>> = flow {
        emit(UiState(isLoading = true))
        try {
            val response = apiService.recordAdministration(request)
            if (response.isSuccessful) {
                val adminResponse = response.body()
                if (adminResponse?.success == true) {
                    emit(UiState(data = adminResponse.administration))
                } else {
                    emit(UiState(error = adminResponse?.message ?: "Administration failed"))
                }
            } else {
                emit(UiState(error = "Failed to record administration: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    suspend fun getAdministrationHistory(
        patientId: String? = null,
        drugName: String? = null,
        dateFrom: String? = null,
        dateTo: String? = null
    ): Flow<UiState<List<AdministrationRecord>>> = flow {
        emit(UiState(isLoading = true))
        try {
            val response = apiService.getAdministrationHistory(patientId, drugName, dateFrom, dateTo)
            if (response.isSuccessful) {
                val data = response.body()
                val administrations = data?.get("administrations")?.let { items ->
                    if (items is List<*>) items.filterIsInstance<Map<String, Any>>() else emptyList()
                } ?: emptyList()
                val adminList = administrations.map { mapToAdministrationRecord(it) }
                emit(UiState(data = adminList))
            } else {
                emit(UiState(error = "Failed to get administration history: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    // Device Management Operations
    suspend fun getRfidStatus(): Flow<UiState<List<DeviceStatus>>> = flow {
        emit(UiState(isLoading = true))
        try {
            val response = apiService.getRfidStatus()
            if (response.isSuccessful) {
                val data = response.body()
                val devices = data?.get("rfid_devices")?.let { items ->
                    if (items is List<*>) items.filterIsInstance<Map<String, Any>>() else emptyList()
                } ?: emptyList()
                val deviceList = devices.map { mapToDeviceStatus(it) }
                emit(UiState(data = deviceList))
            } else {
                emit(UiState(error = "Failed to get RFID status: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    suspend fun connectBluetoothDevice(
        deviceAddress: String,
        deviceName: String
    ): Flow<UiState<DeviceStatus>> = flow {
        emit(UiState(isLoading = true))
        try {
            val request = BluetoothConnectRequest(deviceAddress = deviceAddress, deviceName = deviceName)
            val response = apiService.connectBluetoothDevice(request)
            if (response.isSuccessful) {
                val connectResponse = response.body()
                if (connectResponse?.success == true) {
                    emit(UiState(data = connectResponse.device))
                } else {
                    emit(UiState(error = connectResponse?.message ?: "Connection failed"))
                }
            } else {
                emit(UiState(error = "Failed to connect Bluetooth device: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    suspend fun getBluetoothDevices(): Flow<UiState<List<DeviceStatus>>> = flow {
        emit(UiState(isLoading = true))
        try {
            val response = apiService.getBluetoothDevices()
            if (response.isSuccessful) {
                val data = response.body()
                val devices = data?.get("bluetooth_devices")?.let { items ->
                    if (items is List<*>) items.filterIsInstance<Map<String, Any>>() else emptyList()
                } ?: emptyList()
                val deviceList = devices.map { mapToDeviceStatus(it) }
                emit(UiState(data = deviceList))
            } else {
                emit(UiState(error = "Failed to get Bluetooth devices: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(UiState(error = "Network error: ${e.message}"))
        }
    }
    
    // Mapping functions
    private fun mapToDataConversion(map: Map<String, Any>): DataConversion {
        return DataConversion(
            conversionId = map["conversion_id"] as? String ?: "",
            conversionType = map["conversion_type"] as? String ?: "",
            status = map["status"] as? String ?: "",
            createdAt = map["created_at"] as? String ?: "",
            updatedAt = map["updated_at"] as? String ?: "",
            drugRecordsCount = (map["drug_records_count"] as? Number)?.toInt() ?: 0
        )
    }
    
    private fun mapToDrugInventory(map: Map<String, Any>): DrugInventory {
        return DrugInventory(
            id = (map["id"] as? Number)?.toInt() ?: 0,
            rfidTag = map["rfid_tag"] as? String ?: "",
            drugName = map["drug_name"] as? String ?: "",
            dosage = map["dosage"] as? String ?: "",
            strength = map["strength"] as? String ?: "",
            quantity = (map["quantity"] as? Number)?.toInt() ?: 0,
            batchNumber = map["batch_number"] as? String ?: "",
            expirationDate = map["expiration_date"] as? String,
            manufacturer = map["manufacturer"] as? String ?: "",
            location = map["location"] as? String ?: "",
            status = map["status"] as? String ?: "",
            lastScanned = map["last_scanned"] as? String,
            lastScannedBy = map["last_scanned_by"] as? String ?: "",
            metadata = map["metadata"]?.let { if (it is Map<*, *>) it.filterKeys { it is String } as Map<String, Any> else null },
            createdAt = map["created_at"] as? String ?: "",
            updatedAt = map["updated_at"] as? String ?: ""
        )
    }
    
    private fun mapToPatient(map: Map<String, Any>): Patient {
        return Patient(
            id = (map["id"] as? Number)?.toInt() ?: 0,
            patientId = map["patient_id"] as? String ?: "",
            firstName = map["first_name"] as? String ?: "",
            lastName = map["last_name"] as? String ?: "",
            fullName = map["full_name"] as? String ?: "",
            age = (map["age"] as? Number)?.toInt(),
            gender = map["gender"] as? String ?: "",
            dateOfBirth = map["date_of_birth"] as? String,
            address = map["address"] as? String ?: "",
            phoneNumber = map["phone_number"] as? String ?: "",
            metadata = map["metadata"]?.let { if (it is Map<*, *>) it.filterKeys { it is String } as Map<String, Any> else null },
            createdAt = map["created_at"] as? String ?: ""
        )
    }
    
    private fun mapToAdministrationRecord(map: Map<String, Any>): AdministrationRecord {
        return AdministrationRecord(
            id = (map["id"] as? Number)?.toInt() ?: 0,
            patientName = map["patient_name"] as? String ?: "",
            drugName = map["drug_name"] as? String ?: "",
            administeredBy = map["administered_by"] as? String ?: "",
            administrationTime = map["administration_time"] as? String ?: "",
            scheduledTime = map["scheduled_time"] as? String,
            dosageAdministered = map["dosage_administered"] as? String ?: "",
            route = map["route"] as? String ?: "",
            status = map["status"] as? String ?: "",
            notes = map["notes"] as? String ?: "",
            verificationMethod = map["verification_method"] as? String ?: ""
        )
    }
    
    private fun mapToDeviceStatus(map: Map<String, Any>): DeviceStatus {
        return DeviceStatus(
            deviceId = map["device_id"] as? String ?: "",
            deviceName = map["device_name"] as? String ?: "",
            status = map["status"] as? String ?: "",
            batteryLevel = (map["battery_level"] as? Number)?.toInt(),
            lastConnected = map["last_connected"] as? String,
            connectionStatus = map["connection_status"] as? String ?: "",
            errorMessage = map["error_message"] as? String ?: ""
        )
    }
}