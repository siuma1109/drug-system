package com.example.drugsystemapp.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavController
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.example.drugsystemapp.data.models.Routes
import com.example.drugsystemapp.ui.screens.*

@Composable
fun DrugSystemNavHost(navController: NavHostController) {
    
    NavHost(
        navController = navController,
        startDestination = Routes.DASHBOARD
    ) {
        composable(Routes.DASHBOARD) {
            DashboardScreen(navController = navController)
        }
        
        composable(Routes.INVENTORY) {
            InventoryScreen(navController = navController)
        }
        
        composable(Routes.SCAN) {
            ScanScreen(navController = navController)
        }
        
          
        composable(Routes.PATIENTS) {
            PatientsScreen(navController = navController)
        }
        
        composable(Routes.DEVICES) {
            DevicesScreen(navController = navController)
        }
        
        composable(
            route = "${Routes.INVENTORY}/detail/{drugId}",
            arguments = listOf(navArgument("drugId") { type = NavType.IntType })
        ) { backStackEntry ->
            val drugId = backStackEntry.arguments?.getInt("drugId")
            DrugDetailScreen(navController = navController, drugId = drugId)
        }
        
        composable(
            route = "${Routes.PATIENTS}/detail/{patientId}",
            arguments = listOf(navArgument("patientId") { type = NavType.IntType })
        ) { backStackEntry ->
            val patientId = backStackEntry.arguments?.getInt("patientId")
            PatientDetailScreen(navController = navController, patientId = patientId)
        }
        
        composable(Routes.SETTINGS) {
            SettingsScreen(navController = navController)
        }
    }
}