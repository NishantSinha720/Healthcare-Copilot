from django.db import transaction

from apps.documents.models import Document, DocumentChunk

from .chunker import chunk_text
from .text_extractor import extract_text
from .vector_indexer import rebuild_vector_index


def process_document(document_id):
    document = Document.objects.get(
        id=document_id
    )

    try:
        document.status = Document.Status.PROCESSING
        document.error_message = ""

        document.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        text = extract_text(
            document.file.path
        )

        if not text:
            raise ValueError(
                "No readable text was found in the document."
            )

        chunks = chunk_text(text)

        if not chunks:
            raise ValueError(
                "No chunks could be created from the document."
            )

        with transaction.atomic():
            DocumentChunk.objects.filter(
                document=document
            ).delete()

            DocumentChunk.objects.bulk_create(
                [
                    DocumentChunk(
                        document=document,
                        chunk_index=index,
                        content=chunk,
                        character_count=len(chunk),
                    )
                    for index, chunk in enumerate(chunks)
                ]
            )

            document.extracted_text = text
            document.chunk_count = len(chunks)
            document.status = Document.Status.READY
            document.error_message = ""

            document.save(
                update_fields=[
                    "extracted_text",
                    "chunk_count",
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )

        rebuild_vector_index()

        return document

    except Exception as exc:
        document.status = Document.Status.FAILED
        document.error_message = str(exc)

        document.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        raise