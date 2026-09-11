from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminOrDoctor

from .models import Document
from .serializers import DocumentSerializer
from .tasks.document_tasks import process_document_task


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrDoctor()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Document.objects.filter(
            organization__is_active=True,
            patient__is_active=True,
        ).select_related(
            "patient__user",
            "organization",
            "uploaded_by",
        )

        user = self.request.user

        if user.role == user.Role.DOCTOR:
            queryset = queryset.filter(
                organization__doctors__user=user
            )

        elif user.role == user.Role.PATIENT:
            queryset = queryset.filter(
                patient__user=user
            )

        return queryset

    def perform_create(self, serializer):
        document = serializer.save(
            uploaded_by=self.request.user,
        )

        document.file_size = document.file.size

        document.save(
            update_fields=[
                "file_size",
                "updated_at",
            ]
        )

        process_document_task.delay(document.id)


class DocumentDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = DocumentSerializer

    def get_permissions(self):
        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return [IsAdminOrDoctor()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Document.objects.filter(
            organization__is_active=True,
            patient__is_active=True,
        ).select_related(
            "patient__user",
            "organization",
            "uploaded_by",
        )

        user = self.request.user

        if user.role == user.Role.DOCTOR:
            queryset = queryset.filter(
                organization__doctors__user=user
            )

        elif user.role == user.Role.PATIENT:
            queryset = queryset.filter(
                patient__user=user
            )

        return queryset