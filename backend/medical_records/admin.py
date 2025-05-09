from django.contrib import admin

from medical_records.models import MedicalRecord, Medication


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor")
    search_fields = ("patient__name", "doctor__name")


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
