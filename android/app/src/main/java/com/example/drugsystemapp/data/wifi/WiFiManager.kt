package com.example.drugsystemapp.data.wifi

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.net.wifi.WifiInfo
import android.net.wifi.WifiManager
import androidx.core.content.ContextCompat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class WiFiManager(private val context: Context) {
    
    private val connectivityManager: ConnectivityManager by lazy {
        ContextCompat.getSystemService(context, ConnectivityManager::class.java) as ConnectivityManager
    }
    
    private val wifiManager: WifiManager by lazy {
        ContextCompat.getSystemService(context, WifiManager::class.java) as WifiManager
    }
    
    private val _connectionState = MutableStateFlow<WiFiConnectionState>(WiFiConnectionState.Disconnected)
    val connectionState: StateFlow<WiFiConnectionState> = _connectionState
    
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
    
    fun getSignalStrength(): Int {
        val wifiInfo = wifiManager.connectionInfo
        return wifiInfo?.rssi ?: -100
    }
    
    fun getConnectedSSID(): String? {
        val wifiInfo = wifiManager.connectionInfo
        return wifiInfo?.ssid?.removeSurrounding("\"")
    }
    
    fun scanNetworks(): List<String> {
        return try {
            val results = wifiManager.scanResults
            results.map { it.SSID.removeSurrounding("\"") }.distinct()
        } catch (e: Exception) {
            emptyList()
        }
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