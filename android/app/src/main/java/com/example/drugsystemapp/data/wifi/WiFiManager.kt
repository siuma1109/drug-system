package com.example.drugsystemapp.data.wifi

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.Manifest
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.net.wifi.WifiInfo
import android.net.wifi.WifiManager
import android.os.Build
import android.provider.Settings
import androidx.core.content.ContextCompat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

data class WiFiNetwork(
    val ssid: String,
    val bssid: String,
    val signalStrength: Int,
    val frequency: Int,
    val capabilities: String,
    val isSecured: Boolean
)

class WiFiManager(private val context: Context) {
    
    private val connectivityManager: ConnectivityManager by lazy {
        ContextCompat.getSystemService(context, ConnectivityManager::class.java) as ConnectivityManager
    }
    
    private val wifiManager: WifiManager by lazy {
        ContextCompat.getSystemService(context, WifiManager::class.java) as WifiManager
    }
    
    private val _connectionState = MutableStateFlow<WiFiConnectionState>(WiFiConnectionState.Disconnected)
    val connectionState: StateFlow<WiFiConnectionState> = _connectionState
    
    private val _availableNetworks = MutableStateFlow<List<WiFiNetwork>>(emptyList())
    val availableNetworks: StateFlow<List<WiFiNetwork>> = _availableNetworks
    
    private val _isScanning = MutableStateFlow(false)
    val isScanning: StateFlow<Boolean> = _isScanning
    
    private val _networkQuality = MutableStateFlow<NetworkQuality>(NetworkQuality.Unknown)
    val networkQuality: StateFlow<NetworkQuality> = _networkQuality
    
    private var networkCallback: ConnectivityManager.NetworkCallback? = null
    
    init {
        initializeNetworkMonitoring()
    }
    
    private fun initializeNetworkMonitoring() {
        val networkRequest = NetworkRequest.Builder()
            .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
            .build()
        
        networkCallback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                updateConnectionState()
            }
            
            override fun onLost(network: Network) {
                _connectionState.value = WiFiConnectionState.Disconnected
                _networkQuality.value = NetworkQuality.Unknown
            }
            
            override fun onCapabilitiesChanged(
                network: Network,
                networkCapabilities: NetworkCapabilities
            ) {
                updateConnectionState()
                updateNetworkQuality(networkCapabilities)
            }
        }
        
        try {
            connectivityManager.registerNetworkCallback(networkRequest, networkCallback!!)
        } catch (e: Exception) {
            // Handle security exception
        }
        
        // Initial state update
        updateConnectionState()
    }
    
    private fun updateConnectionState() {
        val activeNetwork = connectivityManager.activeNetwork
        val capabilities = connectivityManager.getNetworkCapabilities(activeNetwork)
        
        if (capabilities != null && capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) {
            val wifiInfo = wifiManager.connectionInfo
            if (wifiInfo != null) {
                _connectionState.value = WiFiConnectionState.Connected(
                    ssid = wifiInfo.ssid.removeSurrounding("\""),
                    ipAddress = formatIpAddress(wifiInfo.ipAddress),
                    signalStrength = wifiInfo.rssi,
                    linkSpeed = wifiInfo.linkSpeed
                )
            } else {
                _connectionState.value = WiFiConnectionState.Connected(
                    ssid = "Unknown",
                    ipAddress = "Unknown",
                    signalStrength = 0,
                    linkSpeed = 0
                )
            }
        } else {
            _connectionState.value = WiFiConnectionState.Disconnected
        }
    }
    
    private fun updateNetworkQuality(capabilities: NetworkCapabilities) {
        val downSpeed = capabilities.linkDownstreamBandwidthKbps
        val upSpeed = capabilities.linkUpstreamBandwidthKbps
        
        _networkQuality.value = when {
            downSpeed >= 10000 -> NetworkQuality.Excellent
            downSpeed >= 5000 -> NetworkQuality.Good
            downSpeed >= 1000 -> NetworkQuality.Fair
            downSpeed > 0 -> NetworkQuality.Poor
            else -> NetworkQuality.Unknown
        }
    }
    
    fun getCurrentNetworkInfo(): WiFiConnectionState {
        return _connectionState.value
    }
    
    fun getNetworkQuality(): NetworkQuality {
        return _networkQuality.value
    }
    
    fun isWiFiEnabled(): Boolean {
        return wifiManager.isWifiEnabled
    }
    
    fun enableWiFi() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            // For Android 10+, we need to show settings panel
            val intent = Intent(Settings.Panel.ACTION_WIFI)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
        } else {
            // For older versions, we can enable directly
            if (hasWiFiPermission()) {
                wifiManager.isWifiEnabled = true
            }
        }
    }
    
    fun disableWiFi() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            // For Android 10+, we need to show settings panel
            val intent = Intent(Settings.Panel.ACTION_WIFI)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
        } else {
            // For older versions, we can disable directly
            if (hasWiFiPermission()) {
                wifiManager.isWifiEnabled = false
            }
        }
    }
    
    private fun hasWiFiPermission(): Boolean {
        return ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_WIFI_STATE) == 
               PackageManager.PERMISSION_GRANTED &&
               ContextCompat.checkSelfPermission(context, Manifest.permission.CHANGE_WIFI_STATE) == 
               PackageManager.PERMISSION_GRANTED
    }
    
    fun getSignalStrength(): Int {
        val wifiInfo = wifiManager.connectionInfo
        return wifiInfo?.rssi ?: -100
    }
    
    fun getConnectedSSID(): String? {
        val wifiInfo = wifiManager.connectionInfo
        return wifiInfo?.ssid?.removeSurrounding("\"")
    }
    
    fun startNetworkScan() {
        if (!hasWiFiPermission() || !isWiFiEnabled()) {
            return
        }
        
        _isScanning.value = true
        
        try {
            // Start scan
            wifiManager.startScan()
            
            // Get current results
            updateAvailableNetworks()
            
        } catch (e: Exception) {
            _isScanning.value = false
        }
    }
    
    private fun updateAvailableNetworks() {
        try {
            val scanResults = wifiManager.scanResults
            val networks = scanResults.map { result ->
                WiFiNetwork(
                    ssid = result.SSID.removeSurrounding("\""),
                    bssid = result.BSSID,
                    signalStrength = result.level,
                    frequency = result.frequency,
                    capabilities = result.capabilities,
                    isSecured = result.capabilities.contains("WEP") || 
                               result.capabilities.contains("WPA") || 
                               result.capabilities.contains("WPA2") || 
                               result.capabilities.contains("WPA3")
                )
            }.distinctBy { it.ssid }
            
            _availableNetworks.value = networks
        } catch (e: Exception) {
            _availableNetworks.value = emptyList()
        } finally {
            _isScanning.value = false
        }
    }
    
    fun stopNetworkScan() {
        _isScanning.value = false
    }
    
    private fun formatIpAddress(ipAddress: Int): String {
        return String.format(
            "%d.%d.%d.%d",
            (ipAddress and 0xff),
            (ipAddress shr 8 and 0xff),
            (ipAddress shr 16 and 0xff),
            (ipAddress shr 24 and 0xff)
        )
    }
    
    fun cleanup() {
        networkCallback?.let {
            try {
                connectivityManager.unregisterNetworkCallback(it)
            } catch (e: Exception) {
                // Ignore
            }
        }
    }
}

sealed class WiFiConnectionState {
    object Disconnected : WiFiConnectionState()
    data class Connected(
        val ssid: String,
        val ipAddress: String,
        val signalStrength: Int,
        val linkSpeed: Int
    ) : WiFiConnectionState()
}

enum class NetworkQuality {
    Unknown,
    Poor,
    Fair,
    Good,
    Excellent
}