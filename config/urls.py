"""
URL configuration for the BRPI Research Demonstrator.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("assessment/", include("assessment.urls")),
    path("", include("reports.urls")),
]
