package com.example.drugsystemapp.data.network

import com.example.drugsystemapp.data.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // Data Conversion Endpoints
    @POST("conversions")
    suspend fun createConversion(
        @Body request: Map<String, String>
    ): Response<Map<String, Any>>
    
    @GET("conversions/list")
    suspend fun getConversionList(): Response<Map<String, Any>>
    
    @GET("conversions/{conversion_id}/status")
    suspend fun getConversionStatus(
        @Path("conversion_id") conversionId: String
    ): Response<Map<String, Any>>
    
    @POST("conversions/{conversion_id}/process")
    suspend fun processConversion(
        @Path("conversion_id") conversionId: String
    ): Response<Map<String, Any>>
    
    @GET("conversions/{conversion_id}/drug-records")
    suspend fun getDrugRecords(
        @Path("conversion_id") conversionId: String
    ): Response<Map<String, Any>>
    
    // Drug Inventory Endpoints
    @GET("drugs/inventory")
    suspend fun getDrugInventory(
        @Query("status") status: String? = null,
        @Query("location") location: String? = null
    ): Response<Map<String, Any>>
    
    @POST("drugs/scan")
    suspend fun scanDrug(@Body request: ScanRequest): Response<ScanResponse>
    
    @PUT("drugs/update-stock")
    suspend fun updateDrugStock(@Body request: Map<String, Any>): Response<Map<String, Any>>
    
    // Patient Management Endpoints
    @GET("patients/list")
    suspend fun getPatientList(): Response<Map<String, Any>>
    
    @GET("patients/{patient_id}")
    suspend fun getPatientDetails(
        @Path("patient_id") patientId: Int
    ): Response<Map<String, Any>>
    
    @POST("patients/verify")
    suspend fun verifyPatient(@Body request: Map<String, String>): Response<Map<String, Any>>
    
    // Administration Records Endpoints
    @POST("administration/record")
    suspend fun recordAdministration(@Body request: AdministrationRequest): Response<AdministrationResponse>
    
    @GET("administration/history")
    suspend fun getAdministrationHistory(
        @Query("patient_id") patientId: String? = null,
        @Query("drug_name") drugName: String? = null,
        @Query("date_from") dateFrom: String? = null,
        @Query("date_to") dateTo: String? = null
    ): Response<Map<String, Any>>
    
    // Device Management Endpoints
    @GET("devices/rfid/status")
    suspend fun getRfidStatus(): Response<Map<String, Any>>
    
    @POST("devices/bluetooth/connect")
    suspend fun connectBluetoothDevice(@Body request: BluetoothConnectRequest): Response<BluetoothConnectResponse>
    
    @GET("devices/bluetooth/list")
    suspend fun getBluetoothDevices(): Response<Map<String, Any>>
}