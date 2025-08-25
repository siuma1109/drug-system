package com.example.drugsystemapp.data.hl7

import com.example.drugsystemapp.data.models.Patient
import com.example.drugsystemapp.data.models.DrugRecord
import java.text.SimpleDateFormat
import java.util.*

class HL7Parser {
    
    companion object {
        private const val FIELD_SEPARATOR = "|"
        private const val COMPONENT_SEPARATOR = "^"
        private const val SUBCOMPONENT_SEPARATOR = "&"
        private const val REPETITION_SEPARATOR = "~"
        private const val ESCAPE_CHARACTER = "\\"
        private const val SEGMENT_TERMINATOR = "\r"
        
        // HL7 Message Types
        const val MESSAGE_TYPE_ADT = "ADT" // Admission, Discharge, Transfer
        const val MESSAGE_TYPE_ORU = "ORU" // Observation Result
        const val MESSAGE_TYPE_ORC = "ORC" // Order Common
        const val MESSAGE_TYPE_RXA = "RXA" // Pharmacy Administration
    }
    
    data class HL7Message(
        val messageType: String,
        val messageControlId: String,
        val processingId: String,
        val versionId: String,
        val segments: Map<String, List<HL7Segment>>
    )
    
    data class HL7Segment(
        val segmentType: String,
        val fields: List<String>
    )
    
    data class HL7Patient(
        val patientId: String,
        val firstName: String?,
        val lastName: String?,
        val dateOfBirth: Date?,
        val gender: String?,
        val address: String?,
        val phoneNumber: String?
    )
    
    data class HL7Order(
        val orderId: String,
        val orderControl: String,
        val placerOrderNumber: String,
        val fillerOrderNumber: String,
        val orderStatus: String,
        val orderDateTime: Date?
    )
    
    data class HL7Observation(
        val observationId: String,
        val observationValue: String,
        val observationDateTime: Date?,
        val observationType: String,
        val units: String?
    )
    
    /**
     * Parse HL7 message string into structured data
     */
    fun parseHL7Message(hl7String: String): HL7Message {
        val lines = hl7String.split(SEGMENT_TERMINATOR).filter { it.isNotEmpty() }
        val segments = mutableMapOf<String, List<HL7Segment>>()
        
        lines.forEach { line ->
            if (line.length >= 3) {
                val segmentType = line.substring(0, 3)
                val fields = line.substring(3).split(FIELD_SEPARATOR)
                val segment = HL7Segment(segmentType, fields)
                
                segments[segmentType] = segments.getOrDefault(segmentType, emptyList()) + segment
            }
        }
        
        // Extract message header information
        val mshSegment = segments["MSH"]?.firstOrNull()
        val messageType = mshSegment?.fields?.get(8)?.split(COMPONENT_SEPARATOR)?.get(0) ?: ""
        val messageControlId = mshSegment?.fields?.get(9) ?: ""
        val processingId = mshSegment?.fields?.get(10) ?: ""
        val versionId = mshSegment?.fields?.get(11) ?: ""
        
        return HL7Message(
            messageType = messageType,
            messageControlId = messageControlId,
            processingId = processingId,
            versionId = versionId,
            segments = segments
        )
    }
    
    /**
     * Extract patient information from HL7 message
     */
    fun extractPatient(hl7Message: HL7Message): HL7Patient? {
        val pidSegments = hl7Message.segments["PID"] ?: return null
        val pidSegment = pidSegments.firstOrNull() ?: return null
        
        val patientId = getComponent(pidSegment.fields.getOrNull(2), 0)
        val patientNameComponents = getComponents(pidSegment.fields.getOrNull(5), 3)
        val firstName = patientNameComponents.getOrNull(1)
        val lastName = patientNameComponents.getOrNull(0)
        val dateOfBirth = parseDate(pidSegment.fields.getOrNull(7))
        val gender = pidSegment.fields.getOrNull(8)
        val addressComponents = getComponents(pidSegment.fields.getOrNull(11), 3)
        val address = addressComponents.joinToString(" ").takeIf { it.isNotBlank() }
        val phoneNumberComponents = getComponents(pidSegment.fields.getOrNull(13), 0)
        val phoneNumber = phoneNumberComponents.firstOrNull()
        
        return HL7Patient(
            patientId = patientId,
            firstName = firstName,
            lastName = lastName,
            dateOfBirth = dateOfBirth,
            gender = gender,
            address = address,
            phoneNumber = phoneNumber
        )
    }
    
    /**
     * Extract drug orders from HL7 message
     */
    fun extractDrugOrders(hl7Message: HL7Message): List<DrugRecord> {
        val drugRecords = mutableListOf<DrugRecord>()
        val orcSegments = hl7Message.segments["ORC"] ?: emptyList()
        val rxoSegments = hl7Message.segments["RXO"] ?: emptyList()
        val rxaSegments = hl7Message.segments["RXA"] ?: emptyList()
        
        orcSegments.forEachIndexed { index, orcSegment ->
            val orderId = getComponent(orcSegment.fields.getOrNull(1), 0)
            val orderControl = orcSegment.fields.getOrNull(4)
            val placerOrderNumber = orcSegment.fields.getOrNull(1)
            val fillerOrderNumber = orcSegment.fields.getOrNull(2)
            
            // Get corresponding RXO segment if available
            val rxoSegment = rxoSegments.getOrNull(index)
            val drugName = rxoSegment?.fields?.getOrNull(1)
            val dosage = rxoSegment?.fields?.getOrNull(2)
            val strength = rxoSegment?.fields?.getOrNull(3)
            
            // Get corresponding RXA segment if available
            val rxaSegment = rxaSegments.getOrNull(index)
            val quantity = rxaSegment?.fields?.getOrNull(4)?.toIntOrNull()
            val administrationDateTime = parseDate(rxaSegment?.fields?.getOrNull(3))
            
            if (drugName != null) {
                drugRecords.add(
                    DrugRecord(
                        id = 0, // Will be set by database
                        drugName = drugName,
                        dosage = dosage ?: "",
                        strength = strength ?: "",
                        quantity = quantity,
                        originalPatientId = "",
                        prescriptionId = orderId,
                        patient = null,
                        createdAt = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(Date()),
                        metadata = mapOf(
                            "order_control" to (orderControl ?: ""),
                            "placer_order_number" to (placerOrderNumber ?: ""),
                            "filler_order_number" to (fillerOrderNumber ?: ""),
                            "administration_datetime" to (administrationDateTime?.toString() ?: "")
                        )
                    )
                )
            }
        }
        
        return drugRecords
    }
    
    /**
     * Generate HL7 message for patient admission
     */
    fun generateADTMessage(
        patient: Patient,
        messageType: String = "ADT^A01", // Admission
        messageControlId: String = UUID.randomUUID().toString()
    ): String {
        val timestamp = SimpleDateFormat("yyyyMMddHHmmss").format(Date())
        val patientName = "${patient.lastName}^${patient.firstName}"
        val dob = SimpleDateFormat("yyyyMMdd").format(patient.dateOfBirth ?: Date())
        
        return buildString {
            append("MSH|^~\\&|DRUG_SYSTEM|HOSPITAL|HOSPITAL|HOSPITAL|$timestamp||$messageType|$messageControlId|P|2.5.1||||||UNICODE")
            append(SEGMENT_TERMINATOR)
            append("PID|||${patient.patientId}||$patientName||${patient.gender ?: ""}||$dob|||||${patient.address ?: ""}||||||||||${patient.phoneNumber ?: ""}")
            append(SEGMENT_TERMINATOR)
            append("PV1||I|GEN|||010101^DOCTOR^JOHN|||||||||1|A0")
            append(SEGMENT_TERMINATOR)
        }
    }
    
    /**
     * Generate HL7 message for drug administration
     */
    fun generateRXAMessage(
        patientId: String,
        drugName: String,
        dosage: String,
        administeredBy: String,
        administrationTime: Date = Date()
    ): String {
        val timestamp = SimpleDateFormat("yyyyMMddHHmmss").format(Date())
        val adminTime = SimpleDateFormat("yyyyMMddHHmmss").format(administrationTime)
        val messageId = UUID.randomUUID().toString()
        
        return buildString {
            append("MSH|^~\\&|DRUG_SYSTEM|HOSPITAL|HOSPITAL|HOSPITAL|$timestamp||RXA^R01|$messageId|P|2.5.1||||||UNICODE")
            append(SEGMENT_TERMINATOR)
            append("PID|||$patientId")
            append(SEGMENT_TERMINATOR)
            append("ORC|RE|||||||||$administeredBy")
            append(SEGMENT_TERMINATOR)
            append("RXA|$adminTime||$drugName|$dosage|mg|||||$administeredBy")
            append(SEGMENT_TERMINATOR)
        }
    }
    
    /**
     * Convert HL7Patient to Patient model
     */
    fun toPatientModel(hl7Patient: HL7Patient): Patient {
        return Patient(
            id = 0, // Will be set by database
            patientId = hl7Patient.patientId,
            firstName = hl7Patient.firstName ?: "",
            lastName = hl7Patient.lastName ?: "",
            fullName = "${hl7Patient.firstName ?: ""} ${hl7Patient.lastName ?: ""}".trim(),
            age = calculateAge(hl7Patient.dateOfBirth),
            gender = hl7Patient.gender ?: "",
            dateOfBirth = hl7Patient.dateOfBirth?.toString(),
            address = hl7Patient.address ?: "",
            phoneNumber = hl7Patient.phoneNumber ?: "",
            createdAt = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(Date()),
            metadata = mapOf(
                "source" to "HL7",
                "imported_at" to SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(Date())
            )
        )
    }
    
    // Helper functions
    private fun getComponent(field: String?, index: Int): String {
        if (field == null) return ""
        val components = field.split(COMPONENT_SEPARATOR)
        return components.getOrNull(index) ?: ""
    }
    
    private fun getComponents(field: String?, maxComponents: Int): List<String> {
        if (field == null) return emptyList()
        val components = field.split(COMPONENT_SEPARATOR)
        return components.take(maxComponents)
    }
    
    private fun parseDate(dateString: String?): Date? {
        if (dateString == null) return null
        
        val formats = listOf(
            "yyyyMMdd",
            "yyyyMMddHHmmss",
            "yyyy-MM-dd",
            "yyyy-MM-dd'T'HH:mm:ss",
            "MM/dd/yyyy",
            "dd/MM/yyyy"
        )
        
        formats.forEach { format ->
            try {
                val sdf = SimpleDateFormat(format)
                return sdf.parse(dateString)
            } catch (e: Exception) {
                // Try next format
            }
        }
        
        return null
    }
    
    private fun calculateAge(birthDate: Date?): Int? {
        if (birthDate == null) return null
        
        val today = Calendar.getInstance()
        val birth = Calendar.getInstance().apply {
            time = birthDate
        }
        
        var age = today.get(Calendar.YEAR) - birth.get(Calendar.YEAR)
        if (today.get(Calendar.DAY_OF_YEAR) < birth.get(Calendar.DAY_OF_YEAR)) {
            age--
        }
        
        return age
    }
}