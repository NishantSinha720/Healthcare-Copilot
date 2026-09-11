from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    model_name = getattr(
        settings,
        "EMBEDDING_MODEL",
        "all-MiniLM-L6-v2",
    )

    return SentenceTransformer(
        model_name,
        device="cpu",
    )


def generate_embedding(text):
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    text = text.strip()

    if not text:
        raise ValueError("text cannot be empty.")

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return embedding