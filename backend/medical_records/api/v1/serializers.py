from rest_framework import serializers
from medical_records.models import MedicalRecord, Medication
from users.api.v1.serializers import UserSerializer
from django.contrib.auth import get_user_model

User=get_user_model()

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ('id', 'name', 'external_data', 'brand_name', 'generic_name', 'manufacturer', 
                 'dosage_form', 'route', 'substance_name', 'pharm_class', 'known_reactions')
        read_only_fields = ('external_data',)


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    medications = MedicationSerializer(many=True, read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = ('id', 'patient', 'patient_name', 'doctor', 'doctor_name', 
                 'description', 'created_at', 'medications')
    
    def get_patient_name(self, obj):
        if (obj.patient):
            return obj.patient.username
        return None
    
    def get_doctor_name(self, obj):
        if (obj.doctor):
            return obj.doctor.username
        return None

class MedicalRecordCreateSerializer(serializers.Serializer):
    patient_id = serializers.CharField(write_only=True)
    description = serializers.CharField()
    medications = serializers.ListField(child=serializers.CharField(), required=False)
    
    def validate_patient_id(self, value):
        User = get_user_model()
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this ID")
        except ValueError:
            raise serializers.ValidationError("Invalid user ID format")