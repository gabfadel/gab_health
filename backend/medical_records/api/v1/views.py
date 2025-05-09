from django.contrib.auth import get_user_model
from django.core.cache import cache
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from medical_records.api.v1.serializers import (
    MedicalRecordCreateSerializer,
    MedicalRecordSerializer,
    MedicationSerializer,
)
from medical_records.models import MedicalRecord, Medication
from medical_records.utils import fetch_medication_data

User = get_user_model()


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MedicalRecordCreateSerializer
        return MedicalRecordSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user",
                openapi.IN_QUERY,
                description="ID do usuário para filtrar os registros (opcional)",
                type=openapi.TYPE_INTEGER,
            )
        ],
        operation_description="Lista os registros médicos filtrados pelo parâmetro 'user'.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user_param = self.request.query_params.get("user", None)

        if hasattr(self.request.user, "is_doctor") and self.request.user.is_doctor:
            return MedicalRecord.objects.all()

        if user_param is not None:
            try:
                user_id = int(user_param)
                return MedicalRecord.objects.filter(patient_id=user_id)
            except (ValueError, TypeError):
                return MedicalRecord.objects.none()

        if self.request.user.is_authenticated:
            return MedicalRecord.objects.filter(patient=self.request.user)
        else:
            return MedicalRecord.objects.none()

    @swagger_auto_schema(
        operation_description="Cria um registro médico. Apenas médicos podem criar registros.",
        responses={201: MedicalRecordSerializer()},
    )
    def create(self, request, *args, **kwargs):
        user = self.request.user
        if not hasattr(user, "is_doctor") or not user.is_doctor:
            return Response(
                {"detail": "You do not have permission to create a medical record."},
                status=403,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            patient = serializer.validated_data.pop("patient_id")
        except KeyError:
            return Response({"detail": "patient_id field is required."}, status=400)

        medical_record = MedicalRecord.objects.create(
            patient=patient,
            doctor=user,
            description=serializer.validated_data.get("description", ""),
        )

        medications = serializer.validated_data.get("medications", [])
        for med_name in medications:
            medication, created = Medication.objects.get_or_create(name=med_name)

            if created:
                data, status_code, _ = fetch_medication_data(med_name)
                if status_code == 200 and data:
                    medication.external_data = data.get("raw_data")

                    extracted = data.get("extracted_info", {})

                    medication.brand_name = (
                        next(iter(extracted.get("brand_names", [])), "") or None
                    )
                    medication.generic_name = (
                        next(iter(extracted.get("generic_names", [])), "") or None
                    )
                    medication.manufacturer = (
                        next(iter(extracted.get("manufacturers", [])), "") or None
                    )
                    medication.dosage_form = (
                        next(iter(extracted.get("dosage_forms", [])), " ") or None
                    )
                    medication.route = (
                        next(iter(extracted.get("routes", [])), "") or None
                    )
                    medication.substance_name = (
                        next(iter(extracted.get("substance_names", [])), "") or None
                    )
                    medication.pharm_class = (
                        next(iter(extracted.get("pharm_classes", [])), "") or None
                    )

                    medication.known_reactions = (
                        ", ".join(extracted.get("reactions", [])) or None
                    )

                    medication.save()

            medical_record.medications.add(medication)

        return Response(
            MedicalRecordSerializer(medical_record).data, status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_description="Atualiza um registro médico. Apenas o médico responsável pode atualizar.",
        responses={200: MedicalRecordSerializer()},
    )
    def update(self, request, *args, **kwargs):
        user = self.request.user
        if not hasattr(user, "is_doctor") or not user.is_doctor:
            return Response(
                {"detail": "You do not have permission to update a medical record."},
                status=403,
            )

        record = self.get_object()
        if record.doctor != user:
            return Response(
                {"detail": "You do not have permission to update this medical record."},
                status=403,
            )

        serializer = self.get_serializer(
            data=request.data, partial=kwargs.pop("partial", False)
        )
        serializer.is_valid(raise_exception=True)

        if "patient_id" in serializer.validated_data:
            record.patient = serializer.validated_data["patient_id"]

        if "description" in serializer.validated_data:
            record.description = serializer.validated_data["description"]

        record.save()

        if "medications" in serializer.validated_data:
            record.medications.clear()

            medications = serializer.validated_data["medications"]
            for med_name in medications:
                medication, created = Medication.objects.get_or_create(name=med_name)

                if created:
                    data, status_code, _ = fetch_medication_data(med_name)
                    if status_code == 200 and data:
                        medication.external_data = data.get("raw_data")

                        extracted = data.get("extracted_info", {})

                        medication.brand_name = (
                            next(iter(extracted.get("brand_names", [])), "") or None
                        )
                        medication.generic_name = (
                            next(iter(extracted.get("generic_names", [])), "") or None
                        )
                        medication.manufacturer = (
                            next(iter(extracted.get("manufacturers", [])), "") or None
                        )
                        medication.dosage_form = (
                            next(iter(extracted.get("dosage_forms", [])), " ") or None
                        )
                        medication.route = (
                            next(iter(extracted.get("routes", [])), "") or None
                        )
                        medication.substance_name = (
                            next(iter(extracted.get("substance_names", [])), "") or None
                        )
                        medication.pharm_class = (
                            next(iter(extracted.get("pharm_classes", [])), "") or None
                        )

                        medication.known_reactions = (
                            ", ".join(extracted.get("reactions", [])) or None
                        )

                        medication.save()

                record.medications.add(medication)

        return Response(MedicalRecordSerializer(record).data)

    @swagger_auto_schema(
        operation_description="Exclui um registro médico. Apenas o médico responsável pode excluir.",
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        if not hasattr(user, "is_doctor") or not user.is_doctor:
            return Response(
                {"detail": "You do not have permission to delete a medical record."},
                status=403,
            )
        record = self.get_object()
        if record.doctor != user:
            return Response(
                {"detail": "You do not have permission to delete this medical record."},
                status=403,
            )
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method="post",
        operation_description="Realiza uma busca externa utilizando a API do FDA, filtrando pelo campo 'query'.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "query": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Termo de busca para medicamento",
                )
            },
            required=["query"],
        ),
        responses={200: openapi.Response("Resultado da busca externa")},
    )
    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def external_search(self, request):
        """General search endpoint that doesn't require a specific record ID"""
        query = request.data.get("query")
        if not query:
            return Response({"detail": "Query parameter is required."}, status=400)

        data, status_code, message = fetch_medication_data(query)
        if status_code == 200:
            return Response(data)
        else:
            return Response({"detail": message}, status=status_code)
