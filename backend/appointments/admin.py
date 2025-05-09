from django.contrib import admin

from appointments.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "date", "appointment_status")
    search_fields = ("patient__name", "doctor__name")
    ordering = ("-date",)
    date_hierarchy = "date"

    def appointment_status(self, obj):
        if obj.is_confirmed:
            return "Confirmed"
        elif obj.is_canceled:
            return "Canceled"
        else:
            return "Pending"
