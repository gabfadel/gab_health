from django.db.models import Case, When, Value, CharField
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import no_body, swagger_auto_schema

from appointments.models import Appointment
from appointments.api.v1.serializers import (
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    AppointmentSerializer,
)


class AppointmentViewSet(viewsets.ModelViewSet):

    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ["date"]

    def get_serializer_class(self):
        if self.action == "list":
            return AppointmentSerializer
        elif self.action == "retrieve":
            return AppointmentDetailSerializer
        elif self.action == "create":
            return AppointmentCreateSerializer
        elif self.action in ["confirm", "cancel"]:
            return AppointmentDetailSerializer
        return AppointmentDetailSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_doctor:
            qs = Appointment.objects.filter(doctor=user)
        else:
            qs = Appointment.objects.filter(patient=user)
        
        qs = qs.select_related('patient', 'doctor') .annotate(
            status=Case(
                When(is_canceled=True, then=Value("Canceled")),
                When(is_confirmed=True, then=Value("Confirmed")),
                default=Value("Pending"),
                output_field=CharField()
            )
        )
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_doctor:
            serializer.save(doctor=user, is_confirmed=False, is_canceled=False)
        else:
            serializer.save(patient=user, is_confirmed=False, is_canceled=False)

    @swagger_auto_schema(
        operation_description="Confirm an appointment. This endpoint only requires the appointment ID in the URL path.",
        responses={
            200: AppointmentDetailSerializer,
            400: "Bad request: Appointment already confirmed or canceled",
            403: "Forbidden: User doesn't have permission to confirm appointments",
            404: "Not found: Appointment with this ID doesn't exist",
        },
        operation_id="confirm_appointment",
        request_body=no_body,
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_PATH,
                description="ID of the appointment to confirm",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
    )
    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        if not (request.user.is_staff or appointment.doctor == request.user):
            return Response(
                {"detail": "You do not have permission to confirm this appointment."},
                status=403,
            )
        if appointment.is_confirmed:
            return Response(
                {"detail": "This appointment is already confirmed."}, status=400
            )
        if appointment.is_canceled:
            return Response(
                {
                    "detail": "This appointment has been canceled and cannot be confirmed."
                },
                status=400,
            )

        appointment.is_confirmed = True
        appointment.save()
        serializer = AppointmentDetailSerializer(appointment)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Cancel an appointment. This endpoint only requires the appointment ID in the URL path.",
        responses={
            200: AppointmentDetailSerializer,
            400: "Bad request: Appointment already canceled or confirmed",
            403: "Forbidden: User doesn't have permission to cancel appointments",
            404: "Not found: Appointment with this ID doesn't exist",
        },
        operation_id="cancel_appointment",
        request_body=no_body,
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_PATH,
                description="ID of the appointment to cancel",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
    )
    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if not (request.user.is_staff or appointment.doctor == request.user):
            return Response(
                {"detail": "You do not have permission to cancel this appointment."},
                status=403,
            )
        if appointment.is_canceled:
            return Response(
                {"detail": "This appointment is already canceled."}, status=400
            )
        if appointment.is_confirmed:
            return Response(
                {
                    "detail": "This appointment has been confirmed and cannot be canceled."
                },
                status=400,
            )

        appointment.is_canceled = True
        appointment.save()
        serializer = AppointmentDetailSerializer(appointment)
        return Response(serializer.data)
