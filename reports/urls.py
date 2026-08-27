from django.urls import path

from reports import views

app_name = "reports"

urlpatterns = [
    path("report/", views.ReportView.as_view(), name="report"),
    path("report/print/", views.PrintReportView.as_view(), name="print"),
]
