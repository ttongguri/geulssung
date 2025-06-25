from django.urls import path
from .views import report_view

urlpatterns = [
    path("", report_view, name="report"),
]
