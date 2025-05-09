from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from appointments.models import Appointment
from appointments.tasks import cancel_appointment


@pytest.mark.django_db
def test_cancel_past_unconfirmed_appointments():
    doctor = User.objects.create_user(
        username="doctor", email="doc@example.com", password="password", is_doctor=True
    )
    patient = User.objects.create_user(
        username="patient",
        email="pat@example.com",
        password="password",
        is_doctor=False,
    )
    appointment = Appointment.objects.create(
        doctor=doctor,
        patient=patient,
        date=timezone.now() - timezone.timedelta(days=1),
        is_confirmed=False,
        is_canceled=False,
    )
    cancel_appointment()
    appointment.refresh_from_db()
    assert appointment.is_canceled == True
