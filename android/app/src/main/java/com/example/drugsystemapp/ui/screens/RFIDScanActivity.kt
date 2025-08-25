package com.example.drugsystemapp.ui.screens

import android.app.PendingIntent
import android.content.Intent
import android.content.IntentFilter
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.Ndef
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.drugsystemapp.data.models.DrugInventory
import com.example.drugsystemapp.data.repository.DrugRepository
import com.example.drugsystemapp.ui.theme.*
import com.example.drugsystemapp.ui.viewmodel.DrugViewModel
import com.example.drugsystemapp.ui.viewmodel.DrugViewModelFactory
import com.example.drugsystemapp.data.models.UiState
import java.nio.charset.StandardCharsets

class RFIDScanActivity : ComponentActivity() {
    private var nfcAdapter: NfcAdapter? = null
    private var pendingIntent: PendingIntent? = null
    private var viewModel: DrugViewModel? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        nfcAdapter = NfcAdapter.getDefaultAdapter(this)
        pendingIntent = PendingIntent.getActivity(
            this, 0, Intent(this, javaClass).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), 0
        )
        
        setContent {
            DrugSystemAppTheme {
                val repository = DrugRepository(this)
                viewModel = viewModel(factory = DrugViewModelFactory(repository))
                
                RFIDScanScreen(
                    viewModel = viewModel!!,
                    onBack = { finish() },
                    onScanComplete = { drug ->
                        val resultIntent = Intent().apply {
                            putExtra("scanned_drug_id", drug.id)
                            putExtra("scanned_drug_name", drug.drugName)
                            putExtra("scanned_drug_rfid", drug.rfidTag)
                        }
                        setResult(RESULT_OK, resultIntent)
                        finish()
                    }
                )
            }
        }
    }
    
    override fun onResume() {
        super.onResume()
        nfcAdapter?.let {
            val intentFilter = arrayOf(IntentFilter(NfcAdapter.ACTION_TECH_DISCOVERED))
            val techLists = arrayOf(arrayOf(Ndef::class.java.name))
            it.enableForegroundDispatch(this, pendingIntent, intentFilter, techLists)
        }
    }
    
    override fun onPause() {
        super.onPause()
        nfcAdapter?.disableForegroundDispatch(this)
    }
    
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        if (intent.action == NfcAdapter.ACTION_TECH_DISCOVERED) {
            val tag = intent.getParcelableExtra<Tag>(NfcAdapter.EXTRA_TAG)
            tag?.let {
                val rfidData = readRFIDTag(it)
                rfidData?.let { data ->
                    viewModel?.scanDrug(data, "RFID Scanner")
                }
            }
        }
    }
    
    private fun readRFIDTag(tag: Tag): String? {
        return try {
            val ndef = Ndef.get(tag)
            ndef?.connect()
            val message = ndef?.ndefMessage
            ndef?.close()
            
            message?.records?.firstOrNull()?.let { record ->
                val payload = record.payload
                if (payload.isNotEmpty()) {
                    // Remove language byte (first byte) if present
                    val textBytes = if (payload[0].toInt() < payload.size) {
                        payload.copyOfRange(1, payload.size)
                    } else {
                        payload
                    }
                    String(textBytes, StandardCharsets.UTF_8)
                } else {
                    null
                }
            }
        } catch (e: Exception) {
            null
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RFIDScanScreen(
    viewModel: DrugViewModel,
    onBack: () -> Unit,
    onScanComplete: (DrugInventory) -> Unit
) {
    val scanState by viewModel.scanState.collectAsState()
    val context = LocalContext.current
    
    LaunchedEffect(scanState) {
        scanState.data?.let { drug ->
            onScanComplete(drug)
        }
        scanState.error?.let { error ->
            Toast.makeText(context, error, Toast.LENGTH_SHORT).show()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("RFID Scanner") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Scanner Animation Area
            Card(
                modifier = Modifier
                    .size(250.dp)
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Nfc,
                            contentDescription = "NFC Scanner",
                            modifier = Modifier.size(80.dp),
                            tint = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "Ready to Scan",
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Tap RFID tag on device",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f)
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
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Instructions",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    InstructionItem(
                        icon = Icons.Default.Nfc,
                        text = "Ensure NFC is enabled on your device"
                    )
                    InstructionItem(
                        icon = Icons.Default.TouchApp,
                        text = "Hold RFID tag close to the NFC reader"
                    )
                    InstructionItem(
                        icon = Icons.Default.Timer,
                        text = "Keep tag steady until scan completes"
                    )
                }
            }
            
            // Status Indicator
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = when {
                        scanState.isLoading -> MaterialTheme.colorScheme.tertiaryContainer
                        scanState.error != null -> MaterialTheme.colorScheme.errorContainer
                        else -> MaterialTheme.colorScheme.secondaryContainer
                    }
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = when {
                            scanState.isLoading -> Icons.Default.Sync
                            scanState.error != null -> Icons.Default.Error
                            else -> Icons.Default.CheckCircle
                        },
                        contentDescription = "Status",
                        tint = when {
                            scanState.isLoading -> MaterialTheme.colorScheme.onTertiaryContainer
                            scanState.error != null -> MaterialTheme.colorScheme.onErrorContainer
                            else -> MaterialTheme.colorScheme.onSecondaryContainer
                        }
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Text(
                        text = when {
                            scanState.isLoading -> "Scanning..."
                            scanState.error != null -> "Scan Failed"
                            else -> "Ready to Scan"
                        },
                        style = MaterialTheme.typography.bodyLarge,
                        color = when {
                            scanState.isLoading -> MaterialTheme.colorScheme.onTertiaryContainer
                            scanState.error != null -> MaterialTheme.colorScheme.onErrorContainer
                            else -> MaterialTheme.colorScheme.onSecondaryContainer
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun InstructionItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    text: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.width(16.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}