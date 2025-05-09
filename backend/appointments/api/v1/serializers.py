from rest_framework import serializers

from appointments.models import Appointment
from users.api.v1.serializers import UserSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.username", read_only=True)
    doctor_name = serializers.CharField(source="doctor.username", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient_name",
            "doctor_name",
            "date",
            "is_confirmed",
            "is_canceled",
        )


class AppointmentDetailSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    doctor = UserSerializer(read_only=True)
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "doctor",
            "date",
            "is_confirmed",
            "is_canceled",
            "created_at",
            "updated_at",
            "status",
        )




class AppointmentCreateSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=UserSerializer.Meta.model.objects.all(), required=False
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=UserSerializer.Meta.model.objects.filter(is_doctor=True),
        required=False,
    )

    class Meta:
        model = Appointment
        fields = ("id", "patient", "doctor", "date")
