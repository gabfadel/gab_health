from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import DoctorList, ProfileView, RegisterView

router = DefaultRouter()
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("doctors/", DoctorList.as_view(), name="doctor-list"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
