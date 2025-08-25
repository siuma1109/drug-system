package com.example.drugsystemapp.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material.icons.filled.Medication
import androidx.compose.material.icons.outlined.Medication
import androidx.compose.material.icons.filled.DevicesOther
import androidx.compose.material.icons.outlined.DevicesOther
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavController
import androidx.navigation.compose.currentBackStackEntryAsState
import com.example.drugsystemapp.data.models.Routes

sealed class BottomNavItem(
    val route: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector,
    val label: String
) {
    object Dashboard : BottomNavItem(
        route = Routes.DASHBOARD,
        selectedIcon = Icons.Default.Dashboard,
        unselectedIcon = Icons.Outlined.Dashboard,
        label = "Dashboard"
    )
    
    object Inventory : BottomNavItem(
        route = Routes.INVENTORY,
        selectedIcon = Icons.Default.Medication,
        unselectedIcon = Icons.Outlined.Medication,
        label = "Inventory"
    )
    
    object Scan : BottomNavItem(
        route = Routes.SCAN,
        selectedIcon = Icons.Default.QrCodeScanner,
        unselectedIcon = Icons.Outlined.QrCodeScanner,
        label = "Scan"
    )
    
        
    object Patients : BottomNavItem(
        route = Routes.PATIENTS,
        selectedIcon = Icons.Default.People,
        unselectedIcon = Icons.Outlined.People,
        label = "Patients"
    )
    
    object Devices : BottomNavItem(
        route = Routes.DEVICES,
        selectedIcon = Icons.Default.DevicesOther,
        unselectedIcon = Icons.Outlined.DevicesOther,
        label = "Devices"
    )
}

@Composable
fun DrugSystemBottomNavigation(
    navController: NavController,
    items: List<BottomNavItem> = listOf(
        BottomNavItem.Dashboard,
        BottomNavItem.Inventory,
        BottomNavItem.Scan,
        BottomNavItem.Patients,
        //BottomNavItem.Devices
    )
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    NavigationBar(
        containerColor = MaterialTheme.colorScheme.surface,
        contentColor = MaterialTheme.colorScheme.onSurface
    ) {
        items.forEach { item ->
            val isSelected = currentRoute == item.route
            
            NavigationBarItem(
                icon = {
                    Icon(
                        imageVector = if (isSelected) item.selectedIcon else item.unselectedIcon,
                        contentDescription = item.label
                    )
                },
                label = {
                    Text(
                        text = item.label,
                        style = MaterialTheme.typography.labelSmall
                    )
                },
                selected = isSelected,
                onClick = {
                    if (currentRoute != item.route) {
                        navController.navigate(item.route) {
                            popUpTo(navController.graph.startDestinationId) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = MaterialTheme.colorScheme.primary,
                    selectedTextColor = MaterialTheme.colorScheme.primary,
                    unselectedIconColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    unselectedTextColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    indicatorColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    }
}