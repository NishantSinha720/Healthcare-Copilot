import requests
from django.conf import settings


OLLAMA_URL = getattr(
    settings,
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate",
)

OLLAMA_MODEL = getattr(
    settings,
    "OLLAMA_MODEL",
    "llama2:7b",
)


def generate_answer(
    question: str,
    context: str,
) -> str:
    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if not context or not context.strip():
        raise ValueError(
            "Context cannot be empty."
        )

    prompt = f"""
You are a healthcare assistant.

Answer the user's question using ONLY the
provided medical context.

If the answer is not present in the context,
say that the information is not available
in the provided medical records.

Do not invent medical facts.

Medical Context:
{context}

User Question:
{question}

Answer:
""".strip()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    answer = data.get("response", "").strip()

    if not answer:
        raise ValueError(
            "Ollama returned an empty response."
        )

    return answer