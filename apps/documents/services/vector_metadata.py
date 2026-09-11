import json
from pathlib import Path

from django.conf import settings


VECTOR_STORE_DIR = (
    Path(settings.BASE_DIR) / "vector_store"
)

METADATA_PATH = (
    VECTOR_STORE_DIR / "chunk_metadata.json"
)


def save_chunk_metadata(chunk_ids):
    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        str(index): chunk_id
        for index, chunk_id in enumerate(chunk_ids)
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
        )


def load_chunk_metadata():
    if not METADATA_PATH.exists():
        return {}

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_chunk_ids(indices):
    metadata = load_chunk_metadata()

    return [
        int(metadata[str(index)])
        for index in indices
        if str(index) in metadata
    ]