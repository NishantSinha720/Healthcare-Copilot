from apps.documents.services.rag_search import search_documents
from apps.healthcare.models import (
    Appointment,
    MedicalRecord,
    Prescription,
)


def search_medical_documents(
    user,
    query: str,
    top_k: int = 5,
):
    return search_documents(
        query=query,
        user=user,
        top_k=top_k,
    )


def get_my_appointments(user):
    queryset = Appointment.objects.select_related(
        "doctor__user",
        "patient__user",
    ).order_by(
        "-appointment_date",
        "-start_time",
    )

    if user.role == user.Role.PATIENT:
        queryset = queryset.filter(
            patient__user=user
        )

    elif user.role == user.Role.DOCTOR:
        queryset = queryset.filter(
            doctor__user=user
        )

    elif user.role != user.Role.ADMIN:
        return []

    return [
        {
            "id": appointment.id,
            "doctor": appointment.doctor.user.get_full_name(),
            "patient": appointment.patient.user.get_full_name(),
            "date": str(appointment.appointment_date),
            "start_time": str(appointment.start_time),
            "end_time": str(appointment.end_time),
            "status": appointment.status,
        }
        for appointment in queryset
    ]


def get_my_medical_records(user):
    queryset = MedicalRecord.objects.select_related(
        "doctor__user",
        "patient__user",
        "organization",
    ).order_by(
        "-record_date",
        "-created_at",
    )

    if user.role == user.Role.PATIENT:
        queryset = queryset.filter(
            patient__user=user
        )

    elif user.role == user.Role.DOCTOR:
        queryset = queryset.filter(
            doctor__user=user
        )

    elif user.role != user.Role.ADMIN:
        return []

    return [
        {
            "id": record.id,
            "patient": record.patient.user.get_full_name(),
            "doctor": record.doctor.user.get_full_name(),
            "organization": record.organization.name,
            "record_date": str(record.record_date),
            "diagnosis": record.diagnosis,
            "symptoms": record.symptoms,
            "treatment": record.treatment,
            "clinical_notes": record.clinical_notes,
        }
        for record in queryset
    ]


def get_my_prescriptions(user):
    queryset = Prescription.objects.select_related(
        "doctor__user",
        "patient__user",
        "organization",
        "medical_record",
    ).order_by(
        "-prescribed_date",
        "-created_at",
    )

    if user.role == user.Role.PATIENT:
        queryset = queryset.filter(
            patient__user=user
        )

    elif user.role == user.Role.DOCTOR:
        queryset = queryset.filter(
            doctor__user=user
        )

    elif user.role != user.Role.ADMIN:
        return []

    return [
        {
            "id": prescription.id,
            "patient": prescription.patient.user.get_full_name(),
            "doctor": prescription.doctor.user.get_full_name(),
            "organization": prescription.organization.name,
            "medical_record_id": prescription.medical_record_id,
            "medication_name": prescription.medication_name,
            "dosage": prescription.dosage,
            "frequency": prescription.frequency,
            "duration": prescription.duration,
            "instructions": prescription.instructions,
            "prescribed_date": str(
                prescription.prescribed_date
            ),
        }
        for prescription in queryset
    ]


def request_cancel_appointment(
    user,
    appointment_id,
):
    try:
        appointment = Appointment.objects.select_related(
            "doctor__user",
            "patient__user",
            "organization",
        ).get(
            id=appointment_id
        )
    except Appointment.DoesNotExist:
        raise ValueError(
            "Appointment was not found."
        )

    if user.role == user.Role.PATIENT:
        if appointment.patient.user_id != user.id:
            raise PermissionError(
                "You can only cancel your own appointments."
            )

    elif user.role == user.Role.DOCTOR:
        if appointment.doctor.user_id != user.id:
            raise PermissionError(
                "You can only cancel your own appointments."
            )

    elif user.role != user.Role.ADMIN:
        raise PermissionError(
            "You do not have permission to cancel appointments."
        )

    if appointment.status == Appointment.Status.CANCELLED:
        return {
            "appointment_id": appointment.id,
            "status": appointment.status,
            "confirmation_required": False,
            "message": "Appointment is already cancelled.",
        }

    return {
        "appointment_id": appointment.id,
        "doctor": appointment.doctor.user.get_full_name(),
        "patient": appointment.patient.user.get_full_name(),
        "date": str(appointment.appointment_date),
        "start_time": str(appointment.start_time),
        "end_time": str(appointment.end_time),
        "status": appointment.status,
        "confirmation_required": True,
        "message": (
            "This action will cancel the appointment. "
            "Explicit confirmation is required."
        ),
    }


def confirm_cancel_appointment(
    user,
    appointment_id,
):
    try:
        appointment = Appointment.objects.select_related(
            "doctor__user",
            "patient__user",
        ).get(
            id=appointment_id
        )
    except Appointment.DoesNotExist:
        raise ValueError(
            "Appointment was not found."
        )

    if user.role == user.Role.PATIENT:
        if appointment.patient.user_id != user.id:
            raise PermissionError(
                "You can only cancel your own appointments."
            )

    elif user.role == user.Role.DOCTOR:
        if appointment.doctor.user_id != user.id:
            raise PermissionError(
                "You can only cancel your own appointments."
            )

    elif user.role != user.Role.ADMIN:
        raise PermissionError(
            "You do not have permission to cancel appointments."
        )

    if appointment.status == Appointment.Status.CANCELLED:
        return {
            "appointment_id": appointment.id,
            "status": appointment.status,
            "message": "Appointment is already cancelled.",
        }

    appointment.status = Appointment.Status.CANCELLED

    appointment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return {
        "appointment_id": appointment.id,
        "status": appointment.status,
        "message": "Appointment cancelled successfully.",
    }