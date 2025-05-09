from django.urls import path
from rest_framework.routers import DefaultRouter

from appointments.api.v1.views import AppointmentViewSet

router = DefaultRouter()
urlpatterns = [
    path(
        "appointments/",
        AppointmentViewSet.as_view({"get": "list", "post": "create"}),
        name="appointment-list",
    ),
    path(
        "appointments/<int:pk>/",
        AppointmentViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="appointment-detail",
    ),
    path(
        "appointments/<int:pk>/confirm/",
        AppointmentViewSet.as_view({"post": "confirm"}),
        name="appointment-confirm",
    ),
    path(
        "appointments/<int:pk>/cancel/",
        AppointmentViewSet.as_view({"post": "cancel"}),
        name="appointment-cancel",
    ),
]
