package com.example.drugsystemapp.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.drugsystemapp.data.repository.DrugRepository

class DrugViewModelFactory(private val repository: DrugRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(DrugViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return DrugViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}