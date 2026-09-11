from apps.documents.services.llm_service import generate_answer
from apps.documents.services.rag_search import search_documents


def ask_question(
    question: str,
    user,
    top_k: int = 5,
):
    results = search_documents(
        question,
        user=user,
        top_k=top_k,
    )

    if not results:
        return {
            "question": question,
            "answer": (
                "I could not find relevant information "
                "in the available medical records."
            ),
            "sources": [],
        }

    context_parts = []

    for result in results:
        context_parts.append(
            (
                f"Document ID: {result['document_id']}\n"
                f"Content:\n{result['content']}"
            )
        )

    context = "\n\n---\n\n".join(context_parts)

    answer = generate_answer(
        question=question,
        context=context,
    )

    sources = [
        {
            "document_id": result["document_id"],
            "chunk_id": result["chunk_id"],
            "score": result["score"],
        }
        for result in results
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }
