from django.utils import timezone
from celery import shared_task
from .models import Appointment

@shared_task
def cancel_appointment():
    now = timezone.now()
    expired_appointments = Appointment.objects.filter(date__lt=now, is_confirmed=False, is_canceled=False)
    count = expired_appointments.update(is_canceled=True)
    return f"Canceled {count} expired appointments."