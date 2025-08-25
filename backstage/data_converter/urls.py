from django.urls import path
from . import views

urlpatterns = [
    # Conversion management
    path("conversions", views.create_conversion_view, name="create_conversion"),
    path(
        "conversions/list",
        views.get_conversion_list_view,
        name="get_conversion_list",
    ),
    path(
        "conversions/<str:conversion_id>/status",
        views.get_conversion_status_view,
        name="get_conversion_status",
    ),
    path(
        "conversions/<str:conversion_id>/process",
        views.process_conversion_view,
        name="process_conversion",
    ),
    path(
        "conversions/<str:conversion_id>/drug-records",
        views.get_drug_records_view,
        name="get_drug_records",
    ),
    
    # Drug inventory management
    path("drugs/inventory", views.get_drug_inventory_view, name="get_drug_inventory"),
    path("drugs/scan", views.scan_drug_view, name="scan_drug"),
    path("drugs/update-stock", views.update_drug_stock_view, name="update_drug_stock"),
    
    # Patient management
    path("patients/list", views.get_patient_list_view, name="get_patient_list"),
    path("patients/<int:patient_id>", views.get_patient_details_view, name="get_patient_details"),
    path("patients/verify", views.verify_patient_view, name="verify_patient"),
    
    # Administration records
    path("administration/record", views.record_administration_view, name="record_administration"),
    path("administration/history", views.get_administration_history_view, name="get_administration_history"),
    
    # Device management
    path("devices/rfid/status", views.get_rfid_status_view, name="get_rfid_status"),
    path("devices/bluetooth/connect", views.connect_bluetooth_device_view, name="connect_bluetooth_device"),
    path("devices/bluetooth/list", views.get_bluetooth_devices_view, name="get_bluetooth_devices"),
]