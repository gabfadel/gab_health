from django.db import models
from django.conf import settings

class Medication(models.Model):
    name = models.CharField(max_length=255)
    external_data = models.JSONField(blank=True, null=True)
    
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    dosage_form = models.CharField(max_length=100, blank=True, null=True)
    route = models.CharField(max_length=100, blank=True, null=True)
    substance_name = models.CharField(max_length=255, blank=True, null=True)
    pharm_class = models.CharField(max_length=255, blank=True, null=True)
    known_reactions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class MedicalRecord(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_records_as_doctor')
    description = models.TextField()
    medications= models.ManyToManyField('Medication',blank=True, related_name='medical_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MedicalRecord({self.patient.username} - {self.doctor.username} on {self.created_at})"