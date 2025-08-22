from django.contrib import admin
from .models import DataConversion, DrugRecord


@admin.register(DataConversion)
class DataConversionAdmin(admin.ModelAdmin):
    """Admin interface for DataConversion model"""
    list_display = ['conversion_id', 'conversion_type', 'status', 'created_at', 'updated_at']
    list_filter = ['conversion_type', 'status', 'created_at']
    search_fields = ['conversion_id', 'source_data']
    readonly_fields = ['conversion_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('conversion_id', 'conversion_type', 'status')
        }),
        ('Data Content', {
            'fields': ('source_data', 'converted_data', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DrugRecord)
class DrugRecordAdmin(admin.ModelAdmin):
    """Admin interface for DrugRecord model"""
    list_display = ['drug_name', 'patient_id', 'prescription_id', 'dosage', 'quantity', 'created_at']
    list_filter = ['created_at', 'conversion__conversion_type', 'conversion__status']
    search_fields = ['drug_name', 'patient_id', 'prescription_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Drug Information', {
            'fields': ('drug_name', 'dosage', 'strength', 'quantity')
        }),
        ('Patient & Prescription', {
            'fields': ('patient_id', 'prescription_id', 'conversion')
        }),
        ('Additional Data', {
            'fields': ('metadata', 'created_at')
        })
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
