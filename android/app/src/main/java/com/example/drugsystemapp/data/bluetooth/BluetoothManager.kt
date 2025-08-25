package com.example.drugsystemapp.data.bluetooth

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.bluetooth.le.BluetoothLeScanner
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import androidx.core.app.ActivityCompat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

data class BluetoothDeviceInfo(
    val device: BluetoothDevice,
    val name: String,
    val address: String,
    val bondState: Int,
    val deviceType: Int,
    val rssi: Int = 0
) {
    val isBonded: Boolean get() = bondState == BluetoothDevice.BOND_BONDED
    val displayName: String get() = name.ifEmpty { "Unknown Device" }
}

class BluetoothManager(private val context: Context) {
    
    private val bluetoothManager: BluetoothManager by lazy {
        context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    }
    
    private val bluetoothAdapter: BluetoothAdapter? by lazy {
        bluetoothManager.adapter
    }
    
    private val bluetoothLeScanner: BluetoothLeScanner? by lazy {
        bluetoothAdapter?.bluetoothLeScanner
    }
    
    private val _devices = MutableStateFlow<List<BluetoothDeviceInfo>>(emptyList())
    val devices: StateFlow<List<BluetoothDeviceInfo>> = _devices
    
    private val _isScanning = MutableStateFlow(false)
    val isScanning: StateFlow<Boolean> = _isScanning
    
    private val _connectionState = MutableStateFlow<BluetoothConnectionState>(BluetoothConnectionState.Disconnected)
    val connectionState: StateFlow<BluetoothConnectionState> = _connectionState
    
    private var scanCallback: ScanCallback? = null
    private val handler = Handler(Looper.getMainLooper())
    
    init {
        initializeBluetooth()
    }
    
    private fun initializeBluetooth() {
        if (!hasBluetoothPermission()) {
            return
        }
        
        bluetoothAdapter?.let { adapter ->
            if (!adapter.isEnabled) {
                // Bluetooth is disabled
                _connectionState.value = BluetoothConnectionState.Disabled
            }
        }
    }
    
    fun isBluetoothEnabled(): Boolean {
        return bluetoothAdapter?.isEnabled == true
    }
    
    fun enableBluetooth() {
        // For all versions, we need to show settings panel
        val intent = Intent(Settings.ACTION_BLUETOOTH_SETTINGS)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
    }
    
    fun disableBluetooth() {
        // For all versions, we need to show settings panel
        val intent = Intent(Settings.ACTION_BLUETOOTH_SETTINGS)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
    }
    
    fun hasBluetoothPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED &&
            ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED
        } else {
            ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH) == PackageManager.PERMISSION_GRANTED &&
            ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_ADMIN) == PackageManager.PERMISSION_GRANTED &&
            ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    fun startScan() {
        if (!hasBluetoothPermission() || !isBluetoothEnabled()) {
            return
        }
        
        _isScanning.value = true
        _devices.value = emptyList()
        
        // Get paired devices first
        val pairedDevices = getPairedDevicesInfo()
        _devices.value = pairedDevices
        
        // Start scanning for new devices using modern API
        scanCallback = object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult) {
                val device = result.device
                val deviceInfo = BluetoothDeviceInfo(
                    device = device,
                    name = device.name ?: "",
                    address = device.address,
                    bondState = device.bondState,
                    deviceType = device.type,
                    rssi = result.rssi
                )
                
                if (!_devices.value.any { d -> d.address == deviceInfo.address }) {
                    _devices.value = _devices.value + deviceInfo
                }
            }
            
            override fun onScanFailed(errorCode: Int) {
                _isScanning.value = false
            }
        }
        
        try {
            bluetoothLeScanner?.startScan(scanCallback)
        } catch (e: Exception) {
            _isScanning.value = false
        }
    }
    
    fun stopScan() {
        scanCallback?.let {
            try {
                bluetoothLeScanner?.stopScan(it)
            } catch (e: Exception) {
                // Ignore cleanup errors
            }
        }
        _isScanning.value = false
    }
    
    fun connectToDevice(device: BluetoothDevice): Boolean {
        if (!hasBluetoothPermission()) {
            return false
        }
        
        try {
            _connectionState.value = BluetoothConnectionState.Connecting(device.name)
            
            // For demonstration, simulate connection
            _connectionState.value = BluetoothConnectionState.Connected(
                deviceName = device.name,
                deviceAddress = device.address,
                batteryLevel = (60..100).random()
            )
            
            return true
        } catch (e: Exception) {
            _connectionState.value = BluetoothConnectionState.Error(e.message ?: "Connection failed")
            return false
        }
    }
    
    fun disconnect() {
        _connectionState.value = BluetoothConnectionState.Disconnected
    }
    
    fun getPairedDevices(): List<BluetoothDevice> {
        if (!hasBluetoothPermission()) {
            return emptyList()
        }
        
        return bluetoothAdapter?.bondedDevices?.toList() ?: emptyList()
    }
    
    fun getPairedDevicesInfo(): List<BluetoothDeviceInfo> {
        if (!hasBluetoothPermission()) {
            return emptyList()
        }
        
        return bluetoothAdapter?.bondedDevices?.map { device ->
            BluetoothDeviceInfo(
                device = device,
                name = device.name ?: "",
                address = device.address,
                bondState = device.bondState,
                deviceType = device.type
            )
        } ?: emptyList()
    }
    
    fun getDeviceByAddress(address: String): BluetoothDevice? {
        return bluetoothAdapter?.getRemoteDevice(address)
    }
}

sealed class BluetoothConnectionState {
    object Disabled : BluetoothConnectionState()
    object Disconnected : BluetoothConnectionState()
    data class Connecting(val deviceName: String?) : BluetoothConnectionState()
    data class Connected(
        val deviceName: String,
        val deviceAddress: String,
        val batteryLevel: Int
    ) : BluetoothConnectionState()
    data class Error(val message: String) : BluetoothConnectionState()
}