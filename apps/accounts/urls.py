from django.urls import path

from .views import (
    AdminOnlyView,
    AdminOrDoctorView,
    DoctorOnlyView,
    LoginView,
    MeView,
    PatientOnlyView,
    RegisterView,
)


urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),
    path(
        "patient-only/",
        PatientOnlyView.as_view(),
        name="patient_only",
    ),
    path(
        "doctor-only/",
        DoctorOnlyView.as_view(),
        name="doctor_only",
    ),
    path(
        "admin-only/",
        AdminOnlyView.as_view(),
        name="admin_only",
    ),
    path(
        "admin-doctor/",
        AdminOrDoctorView.as_view(),
        name="admin_doctor",
    ),
]