from apps.documents.models import DocumentChunk
from apps.documents.services.embedding_service import (
    generate_embedding,
)
from apps.documents.services.vector_metadata import (
    get_chunk_ids,
)
from apps.documents.services.vector_store import (
    load_index,
    search_index,
)


def search_documents(
    query: str,
    user,
    top_k: int = 5,
):
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not user or not user.is_authenticated:
        raise PermissionError(
            "Authentication is required."
        )

    index = load_index()

    if index is None:
        return []

    query_embedding = generate_embedding(
        query.strip()
    )

    scores, indices = search_index(
        index,
        query_embedding,
        top_k=top_k,
    )

    chunk_ids = get_chunk_ids(indices)

    if not chunk_ids:
        return []

    queryset = DocumentChunk.objects.filter(
        id__in=chunk_ids,
        document__organization__is_active=True,
        document__patient__is_active=True,
    ).select_related(
        "document",
        "document__patient",
        "document__organization",
        "document__patient__user",
    )

    if user.role == user.Role.PATIENT:
        queryset = queryset.filter(
            document__patient__user=user
        )

    elif user.role == user.Role.DOCTOR:
        queryset = queryset.filter(
            document__organization__doctors__user=user
        )

    elif user.role == user.Role.ADMIN:
        queryset = queryset.filter(
            document__organization__is_active=True
        )

    else:
        return []

    chunk_map = {
        chunk.id: chunk
        for chunk in queryset
    }

    results = []

    for score, chunk_id in zip(
        scores,
        chunk_ids,
    ):
        chunk = chunk_map.get(chunk_id)

        if chunk is None:
            continue

        results.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "patient_id": chunk.document.patient_id,
                "organization_id": (
                    chunk.document.organization_id
                ),
                "content": chunk.content,
                "score": float(score),
            }
        )

    return results