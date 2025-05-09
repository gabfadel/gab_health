from django.urls import path, include
from rest_framework.routers import DefaultRouter
from medical_records.api.v1.views import MedicalRecordViewSet
router=DefaultRouter()
urlpatterns = [
    path('medical-records/', MedicalRecordViewSet.as_view({'get': 'list', 'post': 'create'}), name='medical-record-list'),
    path('medical-records/<int:pk>/', MedicalRecordViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='medical-record-detail'),
    path('medical-records/external-search/', MedicalRecordViewSet.as_view({'post': 'external_search'}), name='external-search' ),
]
