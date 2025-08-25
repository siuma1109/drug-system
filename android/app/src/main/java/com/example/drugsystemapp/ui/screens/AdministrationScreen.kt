package com.example.drugsystemapp.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.drugsystemapp.data.models.*
import com.example.drugsystemapp.data.repository.DrugRepository
import com.example.drugsystemapp.ui.theme.*
import com.example.drugsystemapp.ui.viewmodel.DrugViewModel
import com.example.drugsystemapp.ui.viewmodel.DrugViewModelFactory
import com.example.drugsystemapp.data.models.UiState
import com.example.drugsystemapp.ui.components.AdministrationStatusChip
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class, androidx.compose.material3.ExperimentalMaterial3Api::class)
@Composable
fun AdministrationScreen(
    navController: NavController,
    viewModel: DrugViewModel = viewModel(factory = DrugViewModelFactory(DrugRepository(navController.context)))
) {
    var showAdministerDialog by remember { mutableStateOf(false) }
    var selectedPatient by remember { mutableStateOf<Patient?>(null) }
    var selectedDrug by remember { mutableStateOf<DrugInventory?>(null) }
    
    LaunchedEffect(Unit) {
        viewModel.loadPatients()
        viewModel.loadDrugInventory()
        viewModel.loadAdministrationHistory()
    }
    
    val patientState by viewModel.patientState.collectAsState()
    val inventoryState by viewModel.inventoryState.collectAsState()
    val adminHistoryState by viewModel.administrationHistoryState.collectAsState()
    val adminState by viewModel.administrationState.collectAsState()
    
    LaunchedEffect(adminState) {
        adminState.data?.let {
            showAdministerDialog = false
            selectedPatient = null
            selectedDrug = null
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Drug Administration") },
                actions = {
                    IconButton(onClick = { 
                        viewModel.loadPatients()
                        viewModel.loadDrugInventory()
                        viewModel.loadAdministrationHistory()
                    }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showAdministerDialog = true },
                containerColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(Icons.Default.Add, contentDescription = "Record Administration")
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Quick Stats
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    AdminStatCard(
                        title = "Today",
                        value = adminHistoryState.data?.count { 
                            it.administrationTime.startsWith(java.time.LocalDate.now().toString()) 
                        } ?: 0,
                        icon = Icons.Default.Today,
                        color = PrimaryBlue
                    )
                    AdminStatCard(
                        title = "This Week",
                        value = adminHistoryState.data?.size ?: 0,
                        icon = Icons.Default.DateRange,
                        color = SecondaryGreen
                    )
                    AdminStatCard(
                        title = "Pending",
                        value = adminHistoryState.data?.count { it.status == "SCHEDULED" } ?: 0,
                        icon = Icons.Default.Schedule,
                        color = WarningAmber
                    )
                }
            }
            
            // Recent Administrations
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
                    .weight(1f),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Recent Administrations",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        TextButton(onClick = { /* View all history */ }) {
                            Text("View All")
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    when {
                        adminHistoryState.isLoading -> {
                            Box(
                                modifier = Modifier.fillMaxWidth(),
                                contentAlignment = Alignment.Center
                            ) {
                                CircularProgressIndicator()
                            }
                        }
                        adminHistoryState.error != null -> {
                            Box(
                                modifier = Modifier.fillMaxWidth(),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = adminHistoryState.error ?: "Error loading history",
                                    color = ErrorRed
                                )
                            }
                        }
                        adminHistoryState.data?.isEmpty() != false -> {
                            Box(
                                modifier = Modifier.fillMaxWidth(),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = "No administration records found",
                                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                                )
                            }
                        }
                        else -> {
                            LazyColumn(
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                items(adminHistoryState.data?.take(10) ?: emptyList()) { admin ->
                                    AdministrationRecordCard(administration = admin)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Administration Dialog
    if (showAdministerDialog) {
        AdministrationDialog(
            patients = patientState.data ?: emptyList(),
            drugs = inventoryState.data ?: emptyList(),
            onDismiss = { 
                showAdministerDialog = false
                selectedPatient = null
                selectedDrug = null
            },
            onConfirm = { patientId, drugId, dosage, route, notes ->
                val drug = inventoryState.data?.find { it.id == drugId }
                val rfidTag = drug?.rfidTag ?: ""
                
                val request = AdministrationRequest(
                    patientId = patientId,
                    rfidTag = rfidTag,
                    administeredBy = "Mobile App",
                    dosageAdministered = dosage,
                    route = route,
                    notes = notes,
                    verificationMethod = "Mobile App"
                )
                
                viewModel.recordAdministration(request)
            }
        )
    }
}

@Composable
fun AdminStatCard(title: String, value: Int, icon: androidx.compose.ui.graphics.vector.ImageVector, color: Color) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = title,
            tint = color,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value.toString(),
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onPrimaryContainer
        )
        Text(
            text = title,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f)
        )
    }
}

@Composable
fun AdministrationRecordCard(administration: AdministrationRecord) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = administration.drugName,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Patient: ${administration.patientName}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f)
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "By: ${administration.administeredBy}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
                
                Column(
                    horizontalAlignment = Alignment.End
                ) {
                    AdministrationStatusChip(status = administration.status)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = formatDateTime(administration.administrationTime),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
            }
            
            if (administration.dosageAdministered.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Dosage: ${administration.dosageAdministered}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
            }
            
            if (administration.route.isNotEmpty()) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Route: ${administration.route}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
            }
            
            if (administration.notes.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Notes: ${administration.notes}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
        }
    }
}

@Composable
fun AdministrationDialog(
    patients: List<Patient>,
    drugs: List<DrugInventory>,
    onDismiss: () -> Unit,
    onConfirm: (String, Int, String, String, String) -> Unit
) {
    var selectedPatient by remember { mutableStateOf<Patient?>(null) }
    var selectedDrug by remember { mutableStateOf<DrugInventory?>(null) }
    var dosage by remember { mutableStateOf("") }
    var route by remember { mutableStateOf("ORAL") }
    var notes by remember { mutableStateOf("") }
    var expandedPatient by remember { mutableStateOf(false) }
    var expandedDrug by remember { mutableStateOf(false) }
    var expandedRoute by remember { mutableStateOf(false) }
    
    val routes = listOf("ORAL", "IV", "IM", "SC", "TOPICAL", "INHALATION", "OTHER")
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Record Drug Administration") },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Patient Selection
                ExposedDropdownMenuBox(
                    expanded = expandedPatient,
                    onExpandedChange = { expandedPatient = !expandedPatient }
                ) {
                    OutlinedTextField(
                        value = selectedPatient?.fullName ?: "",
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Patient") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedPatient) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )
                    DropdownMenu(
                        expanded = expandedPatient,
                        onDismissRequest = { expandedPatient = false }
                    ) {
                        patients.forEach { patient ->
                            DropdownMenuItem(
                                text = { Text("${patient.fullName} (${patient.patientId})") },
                                onClick = {
                                    selectedPatient = patient
                                    expandedPatient = false
                                }
                            )
                        }
                    }
                }
                
                // Drug Selection
                ExposedDropdownMenuBox(
                    expanded = expandedDrug,
                    onExpandedChange = { expandedDrug = !expandedDrug }
                ) {
                    OutlinedTextField(
                        value = selectedDrug?.drugName ?: "",
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Drug") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedDrug) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )
                    DropdownMenu(
                        expanded = expandedDrug,
                        onDismissRequest = { expandedDrug = false }
                    ) {
                        drugs.forEach { drug ->
                            DropdownMenuItem(
                                text = { 
                                    Text(
                                        "${drug.drugName} (${drug.dosage}) - Qty: ${drug.quantity}",
                                        color = if (drug.quantity <= 0) ErrorRed else MaterialTheme.colorScheme.onSurface
                                    )
                                },
                                onClick = {
                                    selectedDrug = drug
                                    expandedDrug = false
                                }
                            )
                        }
                    }
                }
                
                // Dosage Input
                OutlinedTextField(
                    value = dosage,
                    onValueChange = { dosage = it },
                    label = { Text("Dosage Administered") },
                    placeholder = { Text("e.g., 1 tablet, 5ml") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                
                // Route Selection
                ExposedDropdownMenuBox(
                    expanded = expandedRoute,
                    onExpandedChange = { expandedRoute = !expandedRoute }
                ) {
                    OutlinedTextField(
                        value = route,
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Route") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedRoute) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )
                    DropdownMenu(
                        expanded = expandedRoute,
                        onDismissRequest = { expandedRoute = false }
                    ) {
                        routes.forEach { routeOption ->
                            DropdownMenuItem(
                                text = { Text(routeOption) },
                                onClick = {
                                    route = routeOption
                                    expandedRoute = false
                                }
                            )
                        }
                    }
                }
                
                // Notes Input
                OutlinedTextField(
                    value = notes,
                    onValueChange = { notes = it },
                    label = { Text("Notes (Optional)") },
                    placeholder = { Text("Any additional notes...") },
                    modifier = Modifier.fillMaxWidth(),
                    maxLines = 3
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    selectedPatient?.let { patient ->
                        selectedDrug?.let { drug ->
                            onConfirm(patient.patientId, drug.id, dosage, route, notes)
                        }
                    }
                },
                enabled = selectedPatient != null && selectedDrug != null && dosage.isNotBlank()
            ) {
                Text("Record")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}


fun formatDateTime(dateTimeString: String): String {
    return try {
        val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS")
        val outputFormat = SimpleDateFormat("MMM dd, yyyy - HH:mm")
        val date = inputFormat.parse(dateTimeString)
        outputFormat.format(date)
    } catch (e: Exception) {
        dateTimeString
    }
}