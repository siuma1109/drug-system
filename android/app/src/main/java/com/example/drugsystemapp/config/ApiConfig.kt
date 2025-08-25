package com.example.drugsystemapp.config

/**
 * API Configuration for different environments
 */
object ApiConfig {
    
    // Base URLs for different environments
    private const val EMULATOR_BASE_URL = "http://10.0.2.2:8000/api/"
    private const val DEVICE_BASE_URL = "http://192.168.1.100:8000/api/" // Change this to your local IP
    
    // Current environment - set this based on your needs
    private var isEmulator: Boolean = true
    
    /**
     * Get the base URL for the current environment
     */
    fun getBaseUrl(): String {
        return if (isEmulator) {
            EMULATOR_BASE_URL
        } else {
            DEVICE_BASE_URL
        }
    }
    
    /**
     * Set the environment mode
     * @param isEmulator true if running on emulator, false for physical device
     */
    fun setEnvironment(isEmulator: Boolean) {
        this.isEmulator = isEmulator
    }
    
    /**
     * Get current environment mode
     */
    fun isEmulatorEnvironment(): Boolean = isEmulator
    
    /**
     * API timeout values (in milliseconds)
     */
    object Timeouts {
        const val CONNECT_TIMEOUT = 30000L
        const val READ_TIMEOUT = 30000L
        const val WRITE_TIMEOUT = 30000L
    }
    
    /**
     * API endpoints information (relative to base URL)
     */
    object Endpoints {
        // Data Conversion
        const val CONVERSIONS = "conversions"
        const val CONVERSION_LIST = "conversions/list"
        const val CONVERSION_STATUS = "conversions/{conversion_id}/status"
        const val CONVERSION_PROCESS = "conversions/{conversion_id}/process"
        const val CONVERSION_DRUG_RECORDS = "conversions/{conversion_id}/drug-records"
        
        // Drug Inventory
        const val DRUG_INVENTORY = "drugs/inventory"
        const val DRUG_SCAN = "drugs/scan"
        const val DRUG_UPDATE_STOCK = "drugs/update-stock"
        
        // Patient Management
        const val PATIENT_LIST = "patients/list"
        const val PATIENT_DETAILS = "patients/{patient_id}"
        const val PATIENT_VERIFY = "patients/verify"
        
        // Administration Records
        const val ADMINISTRATION_RECORD = "administration/record"
        const val ADMINISTRATION_HISTORY = "administration/history"
        
        // Device Management
        const val RFID_STATUS = "devices/rfid/status"
        const val BLUETOOTH_CONNECT = "devices/bluetooth/connect"
        const val BLUETOOTH_LIST = "devices/bluetooth/list"
    }
}