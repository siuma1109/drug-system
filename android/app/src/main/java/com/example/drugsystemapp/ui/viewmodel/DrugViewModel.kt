package com.example.drugsystemapp.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.drugsystemapp.data.models.*
import com.example.drugsystemapp.data.repository.DrugRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class DrugViewModel(private val repository: DrugRepository) : ViewModel() {
    
    // Drug Inventory State
    private val _inventoryState = MutableStateFlow<UiState<List<DrugInventory>>>(UiState())
    val inventoryState: StateFlow<UiState<List<DrugInventory>>> = _inventoryState
    
    // Scan State
    private val _scanState = MutableStateFlow<UiState<DrugInventory>>(UiState())
    val scanState: StateFlow<UiState<DrugInventory>> = _scanState
    
    // Patient State
    private val _patientState = MutableStateFlow<UiState<List<Patient>>>(UiState())
    val patientState: StateFlow<UiState<List<Patient>>> = _patientState
    
    // Administration State
    private val _administrationState = MutableStateFlow<UiState<AdministrationRecord>>(UiState())
    val administrationState: StateFlow<UiState<AdministrationRecord>> = _administrationState
    
    private val _administrationHistoryState = MutableStateFlow<UiState<List<AdministrationRecord>>>(UiState())
    val administrationHistoryState: StateFlow<UiState<List<AdministrationRecord>>> = _administrationHistoryState
    
    // Device State
    private val _rfidDeviceState = MutableStateFlow<UiState<List<DeviceStatus>>>(UiState())
    val rfidDeviceState: StateFlow<UiState<List<DeviceStatus>>> = _rfidDeviceState
    
    private val _bluetoothDeviceState = MutableStateFlow<UiState<List<DeviceStatus>>>(UiState())
    val bluetoothDeviceState: StateFlow<UiState<List<DeviceStatus>>> = _bluetoothDeviceState
    
    private val _connectionState = MutableStateFlow<UiState<DeviceStatus>>(UiState())
    val connectionState: StateFlow<UiState<DeviceStatus>> = _connectionState
    
    // Load drug inventory
    fun loadDrugInventory(status: String? = null, location: String? = null) {
        viewModelScope.launch {
            repository.getDrugInventory(status, location).collect { state ->
                _inventoryState.value = state
            }
        }
    }
    
    // Scan drug
    fun scanDrug(rfidTag: String, scannedBy: String = "Android App") {
        viewModelScope.launch {
            repository.scanDrug(rfidTag, scannedBy).collect { state ->
                _scanState.value = state
                // Refresh inventory after successful scan
                if (state.data != null) {
                    loadDrugInventory()
                }
            }
        }
    }
    
    // Load patients
    fun loadPatients() {
        viewModelScope.launch {
            repository.getPatientList().collect { state ->
                _patientState.value = state
            }
        }
    }
    
    // Verify patient
    fun verifyPatient(patientId: String) {
        viewModelScope.launch {
            repository.verifyPatient(patientId).collect { state ->
                // Handle verification result
            }
        }
    }
    
    // Record administration
    fun recordAdministration(request: AdministrationRequest) {
        viewModelScope.launch {
            repository.recordAdministration(request).collect { state ->
                _administrationState.value = state
                // Refresh data after successful administration
                if (state.data != null) {
                    loadDrugInventory()
                    loadAdministrationHistory()
                }
            }
        }
    }
    
    // Load administration history
    fun loadAdministrationHistory(
        patientId: String? = null,
        drugName: String? = null,
        dateFrom: String? = null,
        dateTo: String? = null
    ) {
        viewModelScope.launch {
            repository.getAdministrationHistory(patientId, drugName, dateFrom, dateTo).collect { state ->
                _administrationHistoryState.value = state
            }
        }
    }
    
    // Load RFID device status
    fun loadRfidDeviceStatus() {
        viewModelScope.launch {
            repository.getRfidStatus().collect { state ->
                _rfidDeviceState.value = state
            }
        }
    }
    
    // Connect Bluetooth device
    fun connectBluetoothDevice(deviceAddress: String, deviceName: String) {
        viewModelScope.launch {
            repository.connectBluetoothDevice(deviceAddress, deviceName).collect { state ->
                _connectionState.value = state
                // Refresh device list after connection
                if (state.data != null) {
                    loadBluetoothDevices()
                }
            }
        }
    }
    
    // Load Bluetooth devices
    fun loadBluetoothDevices() {
        viewModelScope.launch {
            repository.getBluetoothDevices().collect { state ->
                _bluetoothDeviceState.value = state
            }
        }
    }
    
    // Restock drug
    fun restockDrug(rfidTag: String, quantity: Int) {
        viewModelScope.launch {
            repository.updateDrugStock(rfidTag, quantity, "add", "Android App").collect { state ->
                // Refresh inventory after successful restock
                if (state.data != null) {
                    loadDrugInventory()
                }
            }
        }
    }
    
    // Reset states
    fun resetScanState() {
        _scanState.value = UiState()
    }
    
    fun resetAdministrationState() {
        _administrationState.value = UiState()
    }
    
    fun resetConnectionState() {
        _connectionState.value = UiState()
    }
}