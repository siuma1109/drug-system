package com.example.drugsystemapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.example.drugsystemapp.ui.navigation.DrugSystemBottomNavigation
import com.example.drugsystemapp.ui.navigation.DrugSystemNavHost
import com.example.drugsystemapp.ui.navigation.appContext
import com.example.drugsystemapp.ui.theme.DrugSystemAppTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Set the app context for navigation
        appContext = this
        enableEdgeToEdge()
        setContent {
            DrugSystemAppTheme {
                val navController = rememberNavController()
                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    bottomBar = {
                        DrugSystemBottomNavigation(navController = navController)
                    }
                ) { innerPadding ->
                    DrugSystemNavHost(navController = navController)
                }
            }
        }
    }
}