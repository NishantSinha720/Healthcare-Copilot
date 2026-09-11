from django.urls import path

from .views import (
    AppointmentDetailView,
    AppointmentListCreateView,
    DoctorPatientListCreateView,
    DoctorProfileListCreateView,
    MedicalRecordDetailView,
    MedicalRecordListCreateView,
    OrganizationListCreateView,
    PatientProfileListCreateView,
    PrescriptionDetailView,
    PrescriptionListCreateView,
)


urlpatterns = [
    path(
        "organizations/",
        OrganizationListCreateView.as_view(),
        name="organization-list-create",
    ),
    path(
        "doctors/",
        DoctorProfileListCreateView.as_view(),
        name="doctor-list-create",
    ),
    path(
        "patients/",
        PatientProfileListCreateView.as_view(),
        name="patient-list-create",
    ),
    path(
        "doctor-patients/",
        DoctorPatientListCreateView.as_view(),
        name="doctor-patient-list-create",
    ),
    path(
        "appointments/",
        AppointmentListCreateView.as_view(),
        name="appointment-list-create",
    ),
    path(
        "appointments/<int:pk>/",
        AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
    path(
        "medical-records/",
        MedicalRecordListCreateView.as_view(),
        name="medical-record-list-create",
    ),
    path(
        "medical-records/<int:pk>/",
        MedicalRecordDetailView.as_view(),
        name="medical-record-detail",
    ),
    path(
        "prescriptions/",
        PrescriptionListCreateView.as_view(),
        name="prescription-list-create",
    ),
    path(
        "prescriptions/<int:pk>/",
        PrescriptionDetailView.as_view(),
        name="prescription-detail",
    ),
]