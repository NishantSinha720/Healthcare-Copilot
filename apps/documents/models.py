from django.conf import settings
from django.db import models


class Document(models.Model):
    class DocumentType(models.TextChoices):
        PDF = "PDF", "PDF"
        DOCX = "DOCX", "DOCX"

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PROCESSING = "PROCESSING", "Processing"
        READY = "READY", "Ready"
        FAILED = "FAILED", "Failed"

    patient = models.ForeignKey(
        "healthcare.PatientProfile",
        on_delete=models.PROTECT,
        related_name="documents",
    )

    organization = models.ForeignKey(
        "healthcare.Organization",
        on_delete=models.PROTECT,
        related_name="documents",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_documents",
    )

    title = models.CharField(
        max_length=255,
    )

    document_type = models.CharField(
        max_length=10,
        choices=DocumentType.choices,
    )

    file = models.FileField(
        upload_to="medical_documents/%Y/%m/%d/",
    )

    file_size = models.PositiveBigIntegerField(
        default=0,
    )

    extracted_text = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
        db_index=True,
    )

    error_message = models.TextField(
        blank=True,
    )

    chunk_count = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["patient", "-created_at"]
            ),
            models.Index(
                fields=["organization", "-created_at"]
            ),
            models.Index(
                fields=["status"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.title} | "
            f"{self.patient} | "
            f"{self.status}"
        )


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )

    chunk_index = models.PositiveIntegerField()

    content = models.TextField()

    character_count = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["document", "chunk_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "chunk_index"],
                name="unique_document_chunk_index",
            )
        ]
        indexes = [
            models.Index(
                fields=["document", "chunk_index"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.document.title} | "
            f"Chunk {self.chunk_index}"
        )