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
]