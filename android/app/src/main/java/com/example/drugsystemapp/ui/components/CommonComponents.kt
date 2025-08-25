package com.example.drugsystemapp.ui.components

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.drugsystemapp.ui.theme.AccentOrange
import com.example.drugsystemapp.ui.theme.ErrorRed
import com.example.drugsystemapp.ui.theme.SecondaryGreen
import com.example.drugsystemapp.ui.theme.WarningAmber

@Composable
fun DrugStatusChip(status: String) {
    val (color, text) = when (status) {
        "ACTIVE" -> SecondaryGreen to "Active"
        "LOW_STOCK" -> WarningAmber to "Low Stock"
        "OUT_OF_STOCK" -> ErrorRed to "Out of Stock"
        "EXPIRED" -> ErrorRed to "Expired"
        "RECALLED" -> ErrorRed to "Recalled"
        else -> Color.Gray to status
    }
    
    Surface(
        shape = MaterialTheme.shapes.small,
        color = color.copy(alpha = 0.2f)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.bodySmall,
            color = color
        )
    }
}

@Composable
fun AdministrationStatusChip(status: String) {
    val (color, text) = when (status) {
        "ADMINISTERED" -> SecondaryGreen to "Administered"
        "SCHEDULED" -> WarningAmber to "Scheduled"
        "MISSED" -> ErrorRed to "Missed"
        "CANCELLED" -> ErrorRed to "Cancelled"
        "REFUSED" -> ErrorRed to "Refused"
        "ACTIVE" -> SecondaryGreen to "Active"
        "LOW_STOCK" -> WarningAmber to "Low Stock"
        "OUT_OF_STOCK" -> ErrorRed to "Out of Stock"
        "EXPIRED" -> ErrorRed to "Expired"
        "RECALLED" -> ErrorRed to "Recalled"
        else -> Color.Gray to status
    }
    
    Surface(
        shape = MaterialTheme.shapes.small,
        color = color.copy(alpha = 0.2f)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.bodySmall,
            color = color
        )
    }
}