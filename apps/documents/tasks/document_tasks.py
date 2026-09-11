from celery import shared_task

from apps.documents.services.document_processor import (
    process_document,
)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def process_document_task(self, document_id):
    document = process_document(document_id)

    return {
        "document_id": document.id,
        "status": document.status,
    }