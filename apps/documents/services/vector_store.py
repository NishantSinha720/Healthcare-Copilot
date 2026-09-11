from pathlib import Path

import faiss
import numpy as np
from django.conf import settings


VECTOR_DIMENSION = 384

VECTOR_STORE_DIR = (
    Path(settings.BASE_DIR) / "vector_store"
)

INDEX_PATH = VECTOR_STORE_DIR / "documents.index"


def create_index(embeddings):
    if not embeddings:
        raise ValueError(
            "At least one embedding is required."
        )

    vectors = np.asarray(
        embeddings,
        dtype="float32",
    )

    if vectors.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2D array."
        )

    if vectors.shape[1] != VECTOR_DIMENSION:
        raise ValueError(
            f"Expected {VECTOR_DIMENSION} dimensions, "
            f"got {vectors.shape[1]}."
        )

    index = faiss.IndexFlatIP(
        VECTOR_DIMENSION
    )

    index.add(vectors)

    return index


def save_index(index):
    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    faiss.write_index(
        index,
        str(INDEX_PATH),
    )


def load_index():
    if not INDEX_PATH.exists():
        return None

    return faiss.read_index(
        str(INDEX_PATH)
    )


def search_index(
    index,
    query_embedding,
    top_k=5,
):
    if index is None or index.ntotal == 0:
        return [], []

    query_vector = np.asarray(
        [query_embedding],
        dtype="float32",
    )

    scores, indices = index.search(
        query_vector,
        min(top_k, index.ntotal),
    )

    return (
        scores[0].tolist(),
        indices[0].tolist(),
    )