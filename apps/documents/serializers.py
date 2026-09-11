from pathlib import Path

from rest_framework import serializers

from apps.healthcare.models import Organization, PatientProfile

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(
        source="uploaded_by.username"
    )

    patient_name = serializers.CharField(
        source="patient.user.get_full_name",
        read_only=True,
    )

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    class Meta:
        model = Document
        fields = (
            "id",
            "patient",
            "patient_name",
            "organization",
            "organization_name",
            "uploaded_by",
            "title",
            "document_type",
            "file",
            "file_size",
            "extracted_text",
            "status",
            "error_message",
            "chunk_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "uploaded_by",
            "document_type",
            "file_size",
            "extracted_text",
            "status",
            "error_message",
            "chunk_count",
            "created_at",
            "updated_at",
        )

    def validate_file(self, value):
        extension = Path(value.name).suffix.lower()

        allowed_extensions = {
            ".pdf": Document.DocumentType.PDF,
            ".docx": Document.DocumentType.DOCX,
        }

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only PDF and DOCX files are supported."
            )

        max_size = 10 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "File size cannot exceed 10 MB."
            )

        return value

    def validate(self, attrs):
        patient = attrs.get("patient")
        organization = attrs.get("organization")
        file = attrs.get("file")

        if patient and organization:
            if patient.organization_id != organization.id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "Patient does not belong "
                            "to this organization."
                        )
                    }
                )

        if file:
            extension = Path(file.name).suffix.lower()

            document_type = {
                ".pdf": Document.DocumentType.PDF,
                ".docx": Document.DocumentType.DOCX,
            }.get(extension)

            if document_type:
                attrs["document_type"] = document_type

        return attrs