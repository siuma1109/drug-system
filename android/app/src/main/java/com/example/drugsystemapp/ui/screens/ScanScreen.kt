package com.example.drugsystemapp.ui.screens

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.drugsystemapp.data.models.*
import com.example.drugsystemapp.data.repository.DrugRepository
import com.example.drugsystemapp.ui.theme.*
import com.example.drugsystemapp.ui.viewmodel.DrugViewModel
import com.example.drugsystemapp.ui.viewmodel.DrugViewModelFactory
import com.example.drugsystemapp.data.models.UiState
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScanScreen(
    navController: NavController,
    viewModel: DrugViewModel = viewModel(factory = DrugViewModelFactory(DrugRepository(navController.context)))
) {
    var scanMode by remember { mutableStateOf(ScanMode.QR_CODE) }
    var showPermissionDialog by remember { mutableStateOf(false) }
    var showResultDialog by remember { mutableStateOf(false) }
    var lastScannedDrug by remember { mutableStateOf<DrugInventory?>(null) }
    var manualRfidInput by remember { mutableStateOf("") }
    var showManualInput by remember { mutableStateOf(false) }
    var lastScanResult by remember { mutableStateOf<String?>(null) }
    
    val context = LocalContext.current
    val scanState by viewModel.scanState.collectAsState()
    
    // Permission launcher
    val cameraPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            startQRScanner(context)
        } else {
            Toast.makeText(context, "Camera permission required for QR scanning", Toast.LENGTH_SHORT).show()
        }
    }
    
    // QR Code scanner
    val qrScannerLauncher = rememberLauncherForActivityResult(
        contract = ScanContract()
    ) { result ->
        result.contents?.let { scannedData ->
            lastScanResult = scannedData
            scanDrug(viewModel, scannedData, "QR Scanner")
        }
    }
    
    // NFC permission check
    val nfcPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            Toast.makeText(context, "NFC enabled. Tap RFID tag to scan.", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(context, "NFC permission required for RFID scanning", Toast.LENGTH_SHORT).show()
        }
    }
    
    LaunchedEffect(scanState) {
        scanState.data?.let { drug ->
            lastScannedDrug = drug
            showResultDialog = true
        }
        scanState.error?.let { error ->
            Toast.makeText(context, error, Toast.LENGTH_SHORT).show()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Scan Drug") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(MaterialTheme.colorScheme.background)
                .verticalScroll(rememberScrollState()) // Make screen scrollable
                .padding(bottom = 80.dp), // Add bottom padding to avoid navbar overlap
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Scan Mode Selection
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Select Scan Mode",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        ScanModeCard(
                            title = "QR Code",
                            icon = Icons.Default.QrCodeScanner,
                            isSelected = scanMode == ScanMode.QR_CODE,
                            onClick = { 
                                scanMode = ScanMode.QR_CODE
                                lastScanResult = null
                            },
                            color = PrimaryBlue
                        )
                    }
                }
            }
            
            // Scan Area
            Card(
                modifier = Modifier
                    .size(250.dp)
                    .border(
                        width = 2.dp,
                        color = MaterialTheme.colorScheme.primary.copy(alpha = 0.3f),
                        shape = MaterialTheme.shapes.medium
                    ),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.1f)
                )
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .clickable {
                            when (scanMode) {
                                ScanMode.QR_CODE -> {
                                    if (hasCameraPermission(context)) {
                                        startQRScanner(context, qrScannerLauncher)
                                    } else {
                                        cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                                    }
                                }
                            }
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            imageVector = when (scanMode) {
                                ScanMode.QR_CODE -> Icons.Default.QrCodeScanner
                            },
                            contentDescription = "Scan",
                            modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = when (scanMode) {
                                ScanMode.QR_CODE -> "Tap to scan QR code"
                            },
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }
                }
            }
            
            // Instructions
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Instructions",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = when (scanMode) {
                            ScanMode.QR_CODE -> "Point camera at QR code on drug packaging"
                        },
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
            
            // Scan Result Display
            if (lastScanResult != null) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.secondaryContainer
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Scan Result",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Scanned Data: ${lastScanResult}",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Scan Mode: ${when (scanMode) {
                                ScanMode.QR_CODE -> "QR Code"
                            }}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.8f)
                        )
                    }
                }
            }
        }
    }
    
    // Result Dialog
    if (showResultDialog && lastScannedDrug != null) {
        AlertDialog(
            onDismissRequest = { 
                showResultDialog = false
                lastScannedDrug = null
            },
            title = { Text("Drug Scanned Successfully") },
            text = {
                Column {
                    Text("Drug: ${lastScannedDrug!!.drugName}")
                    Text("Dosage: ${lastScannedDrug!!.dosage}")
                    Text("Strength: ${lastScannedDrug!!.strength}")
                    Text("Quantity: ${lastScannedDrug!!.quantity}")
                    Text("Status: ${lastScannedDrug!!.status}")
                    Text("Location: ${lastScannedDrug!!.location}")
                }
            },
            confirmButton = {
                TextButton(
                    onClick = { 
                        showResultDialog = false
                        lastScannedDrug = null
                        navController.navigate(Routes.INVENTORY)
                    }
                ) {
                    Text("View Details")
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { 
                        showResultDialog = false
                        lastScannedDrug = null
                    }
                ) {
                    Text("OK")
                }
            }
        )
    }
}

@Composable
fun ScanModeCard(
    title: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    isSelected: Boolean,
    onClick: () -> Unit,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.clickable(onClick = onClick)
    ) {
        Surface(
            shape = CircleShape,
            color = if (isSelected) color.copy(alpha = 0.2f) else Color.Transparent,
            modifier = Modifier.size(60.dp)
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    modifier = Modifier.size(32.dp),
                    tint = if (isSelected) color else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.bodySmall,
            color = if (isSelected) color else MaterialTheme.colorScheme.onSurface
        )
    }
}

enum class ScanMode {
    QR_CODE,
}

fun hasCameraPermission(context: android.content.Context): Boolean {
    return ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
}

fun hasNfcPermission(context: android.content.Context): Boolean {
    return ContextCompat.checkSelfPermission(context, Manifest.permission.NFC) == PackageManager.PERMISSION_GRANTED
}

fun startQRScanner(context: android.content.Context, launcher: androidx.activity.compose.ManagedActivityResultLauncher<ScanOptions, com.journeyapps.barcodescanner.ScanIntentResult>? = null) {
    val options = ScanOptions().apply {
        setDesiredBarcodeFormats(com.google.zxing.BarcodeFormat.QR_CODE.name)
        setPrompt("Scan QR code")
        setCameraId(1)
        setBeepEnabled(true)
        setBarcodeImageEnabled(true)
    }
    
    launcher?.launch(options)
}

fun scanDrug(viewModel: DrugViewModel, rfidTag: String, scannedBy: String) {
    viewModel.scanDrug(rfidTag, scannedBy)
}