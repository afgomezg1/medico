from django.contrib import admin
from .models import Doctor, Assignment


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('doctor_id', 'name', 'city')
    search_fields = ('name', 'city')
    list_filter = ('city',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment_id', 'doctor', 'patient_id', 'assigned_at')
    search_fields = ('patient_id', 'doctor__name')
    list_filter = ('assigned_at', 'doctor__city')
    date_hierarchy = 'assigned_at'
