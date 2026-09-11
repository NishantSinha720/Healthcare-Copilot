from apps.documents.models import Document, DocumentChunk

from .embedding_service import generate_embedding
from .vector_metadata import save_chunk_metadata
from .vector_store import (
    create_index,
    save_index,
)


def rebuild_vector_index():
    chunks = list(
        DocumentChunk.objects.filter(
            document__status=Document.Status.READY,
            document__organization__is_active=True,
            document__patient__is_active=True,
        ).order_by(
            "id"
        )
    )

    if not chunks:
        return {
            "indexed_chunks": 0,
        }

    embeddings = []
    chunk_ids = []

    for chunk in chunks:
        embedding = generate_embedding(
            chunk.content
        )

        embeddings.append(embedding)
        chunk_ids.append(chunk.id)

    index = create_index(
        embeddings
    )

    save_index(index)

    save_chunk_metadata(
        chunk_ids
    )

    return {
        "indexed_chunks": len(chunks),
    }