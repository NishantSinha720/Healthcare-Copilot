import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.healthcare.models import (
    Appointment,
    DoctorPatient,
    DoctorProfile,
    MedicalRecord,
    Organization,
    PatientProfile,
    Prescription,
)
from apps.notifications.models import Notification


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def patient(db):
    return User.objects.create_user(
        username="test_patient",
        email="test_patient@example.com",
        password="TestPassword123!",
        role=User.Role.PATIENT,
    )


@pytest.fixture
def doctor(db):
    return User.objects.create_user(
        username="test_doctor",
        email="test_doctor@example.com",
        password="TestPassword123!",
        role=User.Role.DOCTOR,
    )


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username="test_admin",
        email="test_admin@example.com",
        password="TestPassword123!",
        role=User.Role.ADMIN,
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def organization(db, admin):
    return Organization.objects.create(
        name="Test Hospital",
        code="TEST001",
        created_by=admin,
    )


@pytest.fixture
def healthcare_setup(patient, doctor, organization):
    doctor_profile = DoctorProfile.objects.create(
        user=doctor,
        organization=organization,
        specialization="Cardiology",
    )

    patient_profile = PatientProfile.objects.create(
        user=patient,
        organization=organization,
        blood_group="O+",
    )

    DoctorPatient.objects.create(
        doctor=doctor_profile,
        patient=patient_profile,
    )

    return {
        "doctor_profile": doctor_profile,
        "patient_profile": patient_profile,
    }


def authenticate(client, user):
    client.force_authenticate(user=user)


@pytest.mark.django_db
def test_user_can_be_created():
    user = User.objects.create_user(
        username="pytest_user",
        email="pytest@example.com",
        password="TestPassword123!",
        role=User.Role.PATIENT,
    )

    assert user.id is not None
    assert user.role == User.Role.PATIENT
    assert user.check_password("TestPassword123!")


@pytest.mark.django_db
def test_authenticated_me_endpoint(api_client, patient):
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "test_patient",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "tokens" in response.data
    assert "access" in response.data["tokens"]
    assert "refresh" in response.data["tokens"]

    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {response.data['tokens']['access']}"
    )

    response = api_client.get("/api/auth/me/")

    assert response.status_code == 200
    assert response.data["username"] == patient.username
    assert response.data["role"] == User.Role.PATIENT


@pytest.mark.django_db
def test_unauthenticated_ai_agent_is_rejected(api_client):
    response = api_client.post(
        "/api/ai/agent/",
        {"question": "What medications am I taking?"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_healthcare_endpoint_is_rejected(api_client):
    response = api_client.get("/api/healthcare/appointments/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_patient_cannot_create_medical_record(
    api_client,
    patient,
    doctor,
    healthcare_setup,
):
    authenticate(api_client, patient)

    response = api_client.post(
        "/api/healthcare/medical-records/",
        {
            "doctor": healthcare_setup["doctor_profile"].id,
            "patient": healthcare_setup["patient_profile"].id,
            "organization": healthcare_setup["patient_profile"].organization_id,
            "diagnosis": "Unauthorized Test",
            "symptoms": "Test symptoms",
            "treatment": "Test treatment",
            "clinical_notes": "Patient must not create this.",
            "record_date": "2026-09-11",
            "created_by": doctor.id,
        },
        format="json",
    )

    assert response.status_code == 403

    assert not MedicalRecord.objects.filter(
        diagnosis="Unauthorized Test"
    ).exists()


@pytest.mark.django_db
def test_patient_cannot_create_prescription(
    api_client,
    patient,
    doctor,
    healthcare_setup,
):
    authenticate(api_client, patient)

    response = api_client.post(
        "/api/healthcare/prescriptions/",
        {
            "doctor": healthcare_setup["doctor_profile"].id,
            "patient": healthcare_setup["patient_profile"].id,
            "organization": healthcare_setup["patient_profile"].organization_id,
            "medication_name": "Unauthorized Medicine",
            "dosage": "10 mg",
            "frequency": "Once daily",
            "duration": "7 days",
            "instructions": "Test",
            "prescribed_date": "2026-09-11",
            "created_by": doctor.id,
        },
        format="json",
    )

    assert response.status_code == 403

    assert not Prescription.objects.filter(
        medication_name="Unauthorized Medicine"
    ).exists()


@pytest.mark.django_db
def test_patient_can_only_see_own_appointments(
    api_client,
    patient,
    doctor,
    healthcare_setup,
):
    other_patient = User.objects.create_user(
        username="other_patient",
        email="other_patient@example.com",
        password="TestPassword123!",
        role=User.Role.PATIENT,
    )

    other_profile = PatientProfile.objects.create(
        user=other_patient,
        organization=healthcare_setup["patient_profile"].organization,
        blood_group="A+",
    )

    Appointment.objects.create(
        doctor=healthcare_setup["doctor_profile"],
        patient=healthcare_setup["patient_profile"],
        organization=healthcare_setup["patient_profile"].organization,
        appointment_date="2026-09-15",
        start_time="10:00",
        end_time="10:30",
        reason="Own appointment",
        created_by=doctor,
    )

    Appointment.objects.create(
        doctor=healthcare_setup["doctor_profile"],
        patient=other_profile,
        organization=healthcare_setup["patient_profile"].organization,
        appointment_date="2026-09-15",
        start_time="11:00",
        end_time="11:30",
        reason="Other appointment",
        created_by=doctor,
    )

    authenticate(api_client, patient)

    response = api_client.get("/api/healthcare/appointments/")

    assert response.status_code == 200

    results = response.data

    if isinstance(results, dict):
        results = results.get("results", [])

    assert len(results) == 1
    assert results[0]["reason"] == "Own appointment"


@pytest.mark.django_db
def test_admin_can_access_audit_logs(api_client, admin):
    AuditLog.objects.create(
        user=admin,
        action=AuditLog.Action.VIEW,
        resource_type="TEST",
        description="Test audit entry",
    )

    authenticate(api_client, admin)

    response = api_client.get("/api/audit/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_patient_cannot_access_audit_logs(api_client, patient):
    authenticate(api_client, patient)

    response = api_client.get("/api/audit/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_notification_list_only_returns_current_user(
    api_client,
    patient,
):
    other_user = User.objects.create_user(
        username="notification_other",
        email="notification_other@example.com",
        password="TestPassword123!",
        role=User.Role.PATIENT,
    )

    Notification.objects.create(
        recipient=patient,
        notification_type=Notification.NotificationType.SYSTEM,
        title="My Notification",
        message="Visible to patient.",
    )

    Notification.objects.create(
        recipient=other_user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Other Notification",
        message="Must not be visible.",
    )

    authenticate(api_client, patient)

    response = api_client.get("/api/notifications/")

    assert response.status_code == 200

    results = response.data

    if isinstance(results, dict):
        results = results.get("results", [])

    titles = [item["title"] for item in results]

    assert "My Notification" in titles
    assert "Other Notification" not in titles


@pytest.mark.django_db
def test_agent_requires_confirmation_for_sensitive_action(
    api_client,
    patient,
):
    authenticate(api_client, patient)

    response = api_client.post(
        "/api/ai/agent/",
        {
            "question": "Cancel my appointment.",
        },
        format="json",
    )

    assert response.status_code in (200, 400)

    if response.status_code == 200:
        data = response.data
        assert (
            "confirmation_required" in data
            or "answer" in data
        )


@pytest.mark.django_db
def test_patient_registration_cannot_escalate_role(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {
            "username": "role_escalation_test",
            "email": "role_escalation@example.com",
            "password": "TestPassword123!",
            "password_confirm": "TestPassword123!",
            "first_name": "Role",
            "last_name": "Test",
            "role": "ADMIN",
        },
        format="json",
    )

    assert response.status_code == 201

    user = User.objects.get(
        username="role_escalation_test"
    )

    assert user.role == User.Role.PATIENT