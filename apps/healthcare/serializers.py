from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User

from .models import (
    Appointment,
    DoctorPatient,
    DoctorProfile,
    MedicalRecord,
    Organization,
    PatientProfile,
    Prescription,
)


class OrganizationSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(
        source="created_by.username"
    )

    class Meta:
        model = Organization
        fields = (
            "id", "name", "code", "email", "phone_number",
            "address", "is_active", "created_by",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "created_by", "created_at", "updated_at",
        )


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.DOCTOR)
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True)
    )

    class Meta:
        model = DoctorProfile
        fields = (
            "id", "user", "organization", "specialization",
            "license_number", "years_of_experience",
            "consultation_fee", "bio", "is_available",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        user = attrs.get("user")

        if user and DoctorProfile.objects.filter(user=user).exists():
            if not self.instance or self.instance.user_id != user.id:
                raise serializers.ValidationError(
                    {"user": "This user already has a doctor profile."}
                )

        return attrs


class PatientProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.PATIENT)
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True)
    )

    class Meta:
        model = PatientProfile
        fields = (
            "id", "user", "organization", "blood_group",
            "emergency_contact_name", "emergency_contact_phone",
            "insurance_provider", "insurance_policy_number",
            "address", "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        user = attrs.get("user")

        if user and PatientProfile.objects.filter(user=user).exists():
            if not self.instance or self.instance.user_id != user.id:
                raise serializers.ValidationError(
                    {"user": "This user already has a patient profile."}
                )

        return attrs


class DoctorPatientSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name",
        read_only=True,
    )
    patient_name = serializers.CharField(
        source="patient.user.get_full_name",
        read_only=True,
    )
    doctor_specialization = serializers.CharField(
        source="doctor.specialization",
        read_only=True,
    )

    doctor = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.filter(
            is_available=True,
            organization__is_active=True,
        )
    )
    patient = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.filter(
            is_active=True,
            organization__is_active=True,
        )
    )

    class Meta:
        model = DoctorPatient
        fields = (
            "id", "doctor", "doctor_name",
            "doctor_specialization", "patient",
            "patient_name", "is_active",
            "assigned_at", "updated_at",
        )
        read_only_fields = (
            "id", "doctor_name", "doctor_specialization",
            "patient_name", "assigned_at", "updated_at",
        )

    def validate(self, attrs):
        doctor = attrs.get("doctor")
        patient = attrs.get("patient")

        if doctor and patient:
            if doctor.organization_id != patient.organization_id:
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "Doctor and patient must belong "
                            "to the same organization."
                        )
                    }
                )

            existing = DoctorPatient.objects.filter(
                doctor=doctor,
                patient=patient,
            )

            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": (
                            "This doctor-patient relationship "
                            "already exists."
                        )
                    }
                )

        return attrs


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name",
        read_only=True,
    )
    patient_name = serializers.CharField(
        source="patient.user.get_full_name",
        read_only=True,
    )
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    doctor = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.filter(
            is_available=True,
            organization__is_active=True,
        )
    )
    patient = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.filter(
            is_active=True,
            organization__is_active=True,
        )
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True)
    )

    class Meta:
        model = Appointment
        fields = (
            "id", "doctor", "doctor_name",
            "patient", "patient_name",
            "organization", "organization_name",
            "appointment_date", "start_time",
            "end_time", "status", "reason",
            "notes", "created_by",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "doctor_name", "patient_name",
            "organization_name", "status",
            "created_by", "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        doctor = attrs.get(
            "doctor",
            getattr(self.instance, "doctor", None),
        )
        patient = attrs.get(
            "patient",
            getattr(self.instance, "patient", None),
        )
        organization = attrs.get(
            "organization",
            getattr(self.instance, "organization", None),
        )
        appointment_date = attrs.get(
            "appointment_date",
            getattr(self.instance, "appointment_date", None),
        )
        start_time = attrs.get(
            "start_time",
            getattr(self.instance, "start_time", None),
        )
        end_time = attrs.get(
            "end_time",
            getattr(self.instance, "end_time", None),
        )

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                {
                    "end_time": (
                        "End time must be later "
                        "than start time."
                    )
                }
            )

        if (
            appointment_date
            and not self.instance
            and appointment_date < timezone.localdate()
        ):
            raise serializers.ValidationError(
                {
                    "appointment_date": (
                        "Appointment date cannot "
                        "be in the past."
                    )
                }
            )

        if doctor and patient:
            if doctor.organization_id != patient.organization_id:
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "Doctor and patient must "
                            "belong to the same organization."
                        )
                    }
                )

            if not DoctorPatient.objects.filter(
                doctor=doctor,
                patient=patient,
                is_active=True,
            ).exists():
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "This doctor and patient "
                            "do not have an active "
                            "relationship."
                        )
                    }
                )

        if organization and doctor:
            if doctor.organization_id != organization.id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "Doctor does not belong "
                            "to this organization."
                        )
                    }
                )

        if organization and patient:
            if patient.organization_id != organization.id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "Patient does not belong "
                            "to this organization."
                        )
                    }
                )

        if doctor and appointment_date and start_time and end_time:
            overlapping = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                status__in=[
                    Appointment.Status.SCHEDULED,
                    Appointment.Status.CONFIRMED,
                ],
                start_time__lt=end_time,
                end_time__gt=start_time,
            )

            if self.instance:
                overlapping = overlapping.exclude(
                    pk=self.instance.pk
                )

            if overlapping.exists():
                raise serializers.ValidationError(
                    {
                        "start_time": (
                            "Doctor already has an "
                            "overlapping appointment "
                            "during this time."
                        )
                    }
                )

        return attrs


class MedicalRecordSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name",
        read_only=True,
    )
    patient_name = serializers.CharField(
        source="patient.user.get_full_name",
        read_only=True,
    )
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    doctor = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.filter(
            organization__is_active=True
        )
    )
    patient = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.filter(
            is_active=True,
            organization__is_active=True,
        )
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True)
    )

    class Meta:
        model = MedicalRecord
        fields = (
            "id", "doctor", "doctor_name",
            "patient", "patient_name",
            "organization", "organization_name",
            "diagnosis", "symptoms", "treatment",
            "clinical_notes", "record_date",
            "created_by", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "doctor_name", "patient_name",
            "organization_name", "created_by",
            "created_at", "updated_at",
        )

    def validate(self, attrs):
        doctor = attrs.get("doctor")
        patient = attrs.get("patient")
        organization = attrs.get("organization")
        record_date = attrs.get("record_date")

        if record_date and record_date > timezone.localdate():
            raise serializers.ValidationError(
                {
                    "record_date": (
                        "Medical record date cannot "
                        "be in the future."
                    )
                }
            )

        if doctor and patient:
            if doctor.organization_id != patient.organization_id:
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "Doctor and patient must "
                            "belong to the same organization."
                        )
                    }
                )

            if not DoctorPatient.objects.filter(
                doctor=doctor,
                patient=patient,
                is_active=True,
            ).exists():
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "This doctor and patient do not "
                            "have an active relationship."
                        )
                    }
                )

        if organization and doctor:
            if doctor.organization_id != organization.id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "Doctor does not belong "
                            "to this organization."
                        )
                    }
                )

        if organization and patient:
            if patient.organization_id != organization.id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "Patient does not belong "
                            "to this organization."
                        )
                    }
                )

        return attrs


class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name",
        read_only=True,
    )
    patient_name = serializers.CharField(
        source="patient.user.get_full_name",
        read_only=True,
    )
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    doctor = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.filter(
            is_available=True,
            organization__is_active=True,
        )
    )
    patient = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.filter(
            is_active=True,
            organization__is_active=True,
        )
    )
    medical_record = serializers.PrimaryKeyRelatedField(
        queryset=MedicalRecord.objects.select_related(
            "doctor",
            "patient",
            "organization",
        )
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True)
    )

    class Meta:
        model = Prescription
        fields = (
            "id",
            "doctor",
            "doctor_name",
            "patient",
            "patient_name",
            "medical_record",
            "organization",
            "organization_name",
            "medication_name",
            "dosage",
            "frequency",
            "duration",
            "instructions",
            "prescribed_date",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "doctor_name",
            "patient_name",
            "organization_name",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        doctor = attrs.get("doctor")
        patient = attrs.get("patient")
        medical_record = attrs.get("medical_record")
        organization = attrs.get("organization")
        prescribed_date = attrs.get("prescribed_date")

        if prescribed_date and prescribed_date > timezone.localdate():
            raise serializers.ValidationError(
                {
                    "prescribed_date": (
                        "Prescription date cannot "
                        "be in the future."
                    )
                }
            )

        if doctor and patient:
            if doctor.organization_id != patient.organization_id:
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "Doctor and patient must "
                            "belong to the same organization."
                        )
                    }
                )

            if not DoctorPatient.objects.filter(
                doctor=doctor,
                patient=patient,
                is_active=True,
            ).exists():
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "This doctor and patient do "
                            "not have an active relationship."
                        )
                    }
                )

        if medical_record and doctor and patient:
            if medical_record.doctor_id != doctor.id:
                raise serializers.ValidationError(
                    {
                        "medical_record": (
                            "Medical record belongs "
                            "to a different doctor."
                        )
                    }
                )

            if medical_record.patient_id != patient.id:
                raise serializers.ValidationError(
                    {
                        "medical_record": (
                            "Medical record belongs "
                            "to a different patient."
                        )
                    }
                )

        if medical_record and organization:
            if medical_record.organization_id != organization.id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "Medical record does not "
                            "belong to this organization."
                        )
                    }
                )

        if organization and doctor:
            if doctor.organization_id != organization.id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "Doctor does not belong "
                            "to this organization."
                        )
                    }
                )

        if organization and patient:
            if patient.organization_id != organization.id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "Patient does not belong "
                            "to this organization."
                        )
                    }
                )

        return attrs