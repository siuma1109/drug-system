package com.example.drugsystemapp.ui.navigation

import android.app.Activity
import androidx.navigation.NavController

// This will be set by the MainActivity
lateinit var appContext: android.content.Context

// Extension function to get context from NavController
val NavController.context: android.content.Context
    get() = appContext