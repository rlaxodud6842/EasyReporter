# app/admin.py
from django.contrib import admin
from .models import ViolationReport

@admin.register(ViolationReport)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "violation_type", "location", "plate_number","image")
    list_filter = ("violation_type", "date")
    search_fields = ("plate_number", "location")
    ordering = ("-date",)
