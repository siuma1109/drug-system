package com.example.drugsystemapp.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.drugsystemapp.data.models.*
import com.example.drugsystemapp.data.repository.DrugRepository
import com.example.drugsystemapp.ui.theme.*
import com.example.drugsystemapp.ui.viewmodel.DrugViewModel
import com.example.drugsystemapp.ui.viewmodel.DrugViewModelFactory
import com.example.drugsystemapp.data.models.UiState
import com.example.drugsystemapp.ui.components.DrugStatusChip

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InventoryScreen(
    navController: NavController,
    viewModel: DrugViewModel = viewModel(factory = DrugViewModelFactory(DrugRepository(navController.context)))
) {
    var searchQuery by remember { mutableStateOf("") }
    var selectedStatus by remember { mutableStateOf<String?>(null) }
    var showFilterDialog by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        viewModel.loadDrugInventory()
    }
    
    val inventoryState by viewModel.inventoryState.collectAsState()
    val filteredInventory = remember(searchQuery, selectedStatus, inventoryState.data) {
        inventoryState.data?.filter { drug ->
            val matchesSearch = searchQuery.isEmpty() || 
                drug.drugName.contains(searchQuery, ignoreCase = true) ||
                drug.rfidTag.contains(searchQuery, ignoreCase = true)
            val matchesStatus = selectedStatus == null || drug.status == selectedStatus
            matchesSearch && matchesStatus
        } ?: emptyList()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Drug Inventory") },
                actions = {
                    IconButton(onClick = { showFilterDialog = true }) {
                        Icon(Icons.Default.FilterList, contentDescription = "Filter")
                    }
                    IconButton(onClick = { viewModel.loadDrugInventory() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { navController.navigate(Routes.SCAN) },
                containerColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add Drug")
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Search Bar
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                placeholder = { Text("Search drugs...") },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                leadingIcon = {
                    Icon(Icons.Default.Search, contentDescription = "Search")
                },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { searchQuery = "" }) {
                            Icon(Icons.Default.Clear, contentDescription = "Clear search")
                        }
                    }
                },
                singleLine = true
            )
            
            // Status Chips
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                val statuses = listOf("ALL", "ACTIVE", "LOW_STOCK", "EXPIRED", "OUT_OF_STOCK")
                statuses.forEach { status ->
                    FilterChip(
                        selected = selectedStatus == if (status == "ALL") null else status,
                        onClick = {
                            selectedStatus = if (status == "ALL") null else status
                        },
                        label = { 
                            Text(
                                text = status.replace("_", " "),
                                style = MaterialTheme.typography.bodySmall
                            ) 
                        },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                            selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    )
                }
            }
            
            // Inventory List
            when (inventoryState.isLoading) {
                true -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                false -> {
                    if (inventoryState.error != null) {
                        Box(
                            modifier = Modifier.fillMaxSize(),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Icon(
                                    Icons.Default.Error,
                                    contentDescription = "Error",
                                    modifier = Modifier.size(64.dp),
                                    tint = ErrorRed
                                )
                                Spacer(modifier = Modifier.height(16.dp))
                                Text(
                                    text = inventoryState.error ?: "Unknown error",
                                    style = MaterialTheme.typography.bodyLarge,
                                    color = ErrorRed
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Button(onClick = { viewModel.loadDrugInventory() }) {
                                    Text("Retry")
                                }
                            }
                        }
                    } else if (filteredInventory.isEmpty()) {
                        Box(
                            modifier = Modifier.fillMaxSize(),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Icon(
                                    Icons.Default.Inventory,
                                    contentDescription = "No drugs",
                                    modifier = Modifier.size(64.dp),
                                    tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
                                )
                                Spacer(modifier = Modifier.height(16.dp))
                                Text(
                                    text = "No drugs found",
                                    style = MaterialTheme.typography.bodyLarge,
                                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                                )
                            }
                        }
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(
                                start = 16.dp,
                                end = 16.dp,
                                top = 16.dp,
                                bottom = 80.dp // Add bottom padding to avoid navbar overlap
                            ),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(filteredInventory) { drug ->
                                DrugInventoryCard(
                                    drug = drug,
                                    onClick = { navController.navigate("${Routes.INVENTORY}/detail/${drug.id}") }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
    
    if (showFilterDialog) {
        AlertDialog(
            onDismissRequest = { showFilterDialog = false },
            title = { Text("Filter Options") },
            text = {
                Column {
                    Text("Status filter applied: ${selectedStatus ?: "All"}")
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Search query: $searchQuery")
                }
            },
            confirmButton = {
                TextButton(onClick = { showFilterDialog = false }) {
                    Text("OK")
                }
            }
        )
    }
}

@Composable
fun DrugInventoryCard(
    drug: DrugInventory,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
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
                        text = drug.drugName,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "${drug.dosage} - ${drug.strength}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "RFID: ${drug.rfidTag}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
                
                Column(
                    horizontalAlignment = Alignment.End
                ) {
                    DrugStatusChip(status = drug.status)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Qty: ${drug.quantity}",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = when (drug.status) {
                            "LOW_STOCK" -> WarningAmber
                            "OUT_OF_STOCK" -> ErrorRed
                            "EXPIRED" -> ErrorRed
                            else -> SecondaryGreen
                        }
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Location: ${drug.location}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
                
                if (drug.expirationDate != null) {
                    Text(
                        text = "Exp: ${drug.expirationDate}",
                        style = MaterialTheme.typography.bodySmall,
                        color = if (isExpired(drug.expirationDate)) ErrorRed else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
            }
        }
    }
}


fun isExpired(expirationDate: String): Boolean {
    return try {
        val currentDate = java.time.LocalDate.now()
        val expDate = java.time.LocalDate.parse(expirationDate)
        expDate.isBefore(currentDate)
    } catch (e: Exception) {
        false
    }
}