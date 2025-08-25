package com.example.drugsystemapp.data.bluetooth

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.ActivityCompat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class BluetoothManager(private val context: Context) {
    
    private val bluetoothManager: BluetoothManager by lazy {
        context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    }
    
    private val bluetoothAdapter: BluetoothAdapter? by lazy {
        bluetoothManager.adapter
    }
    
    private val _devices = MutableStateFlow<List<BluetoothDevice>>(emptyList())
    val devices: StateFlow<List<BluetoothDevice>> = _devices
    
    private val _isScanning = MutableStateFlow(false)
    val isScanning: StateFlow<Boolean> = _isScanning
    
    private val _connectionState = MutableStateFlow<BluetoothConnectionState>(BluetoothConnectionState.Disconnected)
    val connectionState: StateFlow<BluetoothConnectionState> = _connectionState
    
    private var scanCallback: android.bluetooth.BluetoothAdapter.LeScanCallback? = null
    
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
        
        scanCallback = object : android.bluetooth.BluetoothAdapter.LeScanCallback {
            override fun onLeScan(device: BluetoothDevice?, rssi: Int, scanRecord: ByteArray?) {
                device?.let {
                    if (!_devices.value.contains(it)) {
                        _devices.value = _devices.value + it
                    }
                }
            }
        }
        
        bluetoothAdapter?.startLeScan(scanCallback)
    }
    
    fun stopScan() {
        scanCallback?.let {
            bluetoothAdapter?.stopLeScan(it)
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