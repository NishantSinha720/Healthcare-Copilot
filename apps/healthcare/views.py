from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import IsAdmin, IsAdminOrDoctor

from .models import (
    Appointment,
    DoctorPatient,
    DoctorProfile,
    MedicalRecord,
    Organization,
    PatientProfile,
    Prescription,
)
from .serializers import (
    AppointmentSerializer,
    DoctorPatientSerializer,
    DoctorProfileSerializer,
    MedicalRecordSerializer,
    OrganizationSerializer,
    PatientProfileSerializer,
    PrescriptionSerializer,
)


class OrganizationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorProfileSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return DoctorProfile.objects.filter(
            organization__is_active=True
        ).select_related(
            "user",
            "organization",
        )


class PatientProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientProfileSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return PatientProfile.objects.filter(
            is_active=True
        ).select_related(
            "user",
            "organization",
        )


class DoctorPatientListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = DoctorPatientSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return DoctorPatient.objects.filter(
            is_active=True,
            doctor__organization__is_active=True,
            patient__is_active=True,
        ).select_related(
            "doctor__user",
            "patient__user",
        )


class AppointmentListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = AppointmentSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrDoctor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Appointment.objects.filter(
            organization__is_active=True
        ).select_related(
            "doctor__user",
            "patient__user",
            "organization",
            "created_by",
        )

        user = self.request.user

        if user.role == user.Role.DOCTOR:
            queryset = queryset.filter(
                doctor__user=user
            )
        elif user.role == user.Role.PATIENT:
            queryset = queryset.filter(
                patient__user=user
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


class AppointmentDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = AppointmentSerializer

    def get_permissions(self):
        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return [IsAdminOrDoctor()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Appointment.objects.filter(
            organization__is_active=True
        ).select_related(
            "doctor__user",
            "patient__user",
            "organization",
            "created_by",
        )

        user = self.request.user

        if user.role == user.Role.DOCTOR:
            queryset = queryset.filter(
                doctor__user=user
            )
        elif user.role == user.Role.PATIENT:
            queryset = queryset.filter(
                patient__user=user
            )

        return queryset

    def destroy(self, request, *args, **kwargs):
        appointment = self.get_object()

        if appointment.status in [
            Appointment.Status.COMPLETED,
            Appointment.Status.CANCELLED,
        ]:
            return Response(
                {
                    "detail": (
                        "This appointment cannot "
                        "be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = Appointment.Status.CANCELLED
        appointment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": (
                    "Appointment cancelled "
                    "successfully."
                ),
                "appointment_id": appointment.id,
                "status": appointment.status,
            },
            status=status.HTTP_200_OK,
        )


class MedicalRecordListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = MedicalRecordSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrDoctor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = MedicalRecord.objects.filter(
            organization__is_active=True
        ).select_related(
            "doctor__user",
            "patient__user",
            "organization",
            "created_by",
        )

        user = self.request.user

        if user.role == user.Role.DOCTOR:
            queryset = queryset.filter(
                doctor__user=user
            )
        elif user.role == user.Role.PATIENT:
            queryset = queryset.filter(
                patient__user=user
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


class MedicalRecordDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = MedicalRecordSerializer

    def get_permissions(self):
        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return [IsAdminOrDoctor()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = MedicalRecord.objects.filter(
            organization__is_active=True
        ).select_related(
            "doctor__user",
            "patient__user",
            "organization",
            "created_by",
        )

        user = self.request.user

        if user.role == user.Role.DOCTOR:
            queryset = queryset.filter(
                doctor__user=user
            )
        elif user.role == user.Role.PATIENT:
            queryset = queryset.filter(
                patient__user=user
            )

        return queryset


class PrescriptionListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = PrescriptionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrDoctor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Prescription.objects.filter(
            organization__is_active=True
        ).select_related(
            "doctor__user",
            "patient__user",
            "medical_record",
            "organization",
            "created_by",
        )

        user = self.request.user

        if user.role == user.Role.DOCTOR:
            queryset = queryset.filter(
                doctor__user=user
            )
        elif user.role == user.Role.PATIENT:
            queryset = queryset.filter(
                patient__user=user
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


class PrescriptionDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = PrescriptionSerializer

    def get_permissions(self):
        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return [IsAdminOrDoctor()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Prescription.objects.filter(
            organization__is_active=True
        ).select_related(
            "doctor__user",
            "patient__user",
            "medical_record",
            "organization",
            "created_by",
        )

        user = self.request.user

        if user.role == user.Role.DOCTOR:
            queryset = queryset.filter(
                doctor__user=user
            )
        elif user.role == user.Role.PATIENT:
            queryset = queryset.filter(
                patient__user=user
            )

        return queryset