import json
import re

import requests
from django.conf import settings

from apps.ai.tools.medical_tools import (
    confirm_cancel_appointment,
    get_my_appointments,
    get_my_medical_records,
    get_my_prescriptions,
    request_cancel_appointment,
    search_medical_documents,
)


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


TOOLS = {
    "get_my_appointments": (
        "Get the user's appointments."
    ),
    "get_my_medical_records": (
        "Get the user's medical records."
    ),
    "get_my_prescriptions": (
        "Get the user's prescriptions and medications."
    ),
    "search_medical_documents": (
        "Search the user's authorized medical documents."
    ),
    "cancel_appointment": (
        "Request cancellation of an appointment. "
        "This is a sensitive action and always requires "
        "explicit human confirmation."
    ),
}


def _call_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    raw_response = data.get(
        "response",
        "",
    ).strip()

    if not raw_response:
        raise ValueError(
            "Ollama returned an empty response."
        )

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ollama returned invalid JSON: {raw_response}"
        ) from exc


def _is_cancel_request(question):
    text = question.lower()

    cancel_words = [
        "cancel",
        "cancellation",
        "canceling",
        "cancelling",
    ]

    appointment_words = [
        "appointment",
        "appointments",
    ]

    return (
        any(word in text for word in cancel_words)
        and any(
            word in text
            for word in appointment_words
        )
    )


def _extract_appointment_id(question):
    patterns = [
        r"appointment\s*(?:id|number|#)?\s*[:#]?\s*(\d+)",
        r"(?:id|number|#)\s*[:#]?\s*(\d+)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            question.lower(),
        )

        if match:
            return int(match.group(1))

    return None


def _choose_tool(question):
    if _is_cancel_request(question):
        return "cancel_appointment"

    tool_list = "\n".join(
        f"- {name}: {description}"
        for name, description in TOOLS.items()
        if name != "cancel_appointment"
    )

    prompt = f"""
You are a healthcare assistant.

Choose exactly ONE tool for the user's question.

Available tools:

{tool_list}

Rules:

- Medication or medicine questions -> get_my_prescriptions
- Prescription questions -> get_my_prescriptions
- Appointment questions -> get_my_appointments
- Diagnosis, symptoms, treatment, or clinical-history questions
  -> get_my_medical_records
- Questions about uploaded reports/documents -> search_medical_documents

Return ONLY valid JSON:

{{
    "tool": "exact_tool_name"
}}

User question:
{question}
""".strip()

    result = _call_ollama(prompt)

    tool_name = result.get("tool")

    if tool_name not in TOOLS:
        raise ValueError(
            f"Ollama selected an invalid tool: {result}"
        )

    return tool_name


def _execute_tool(
    tool_name,
    user,
    question,
):
    if tool_name == "get_my_appointments":
        return get_my_appointments(user)

    if tool_name == "get_my_medical_records":
        return get_my_medical_records(user)

    if tool_name == "get_my_prescriptions":
        return get_my_prescriptions(user)

    if tool_name == "search_medical_documents":
        return search_medical_documents(
            user=user,
            query=question,
            top_k=5,
        )

    if tool_name == "cancel_appointment":
        appointment_id = _extract_appointment_id(
            question
        )

        if appointment_id is None:
            appointments = get_my_appointments(
                user
            )

            return {
                "confirmation_required": True,
                "action": "cancel_appointment",
                "message": (
                    "Appointment cancellation requires "
                    "an appointment ID and explicit confirmation."
                ),
                "appointments": appointments,
            }

        return request_cancel_appointment(
            user=user,
            appointment_id=appointment_id,
        )

    raise ValueError(
        f"Unknown tool: {tool_name}"
    )


def _generate_confirmation_answer(
    tool_result,
):
    if not tool_result.get(
        "confirmation_required",
        False,
    ):
        return None

    message = tool_result.get(
        "message",
        "Explicit confirmation is required before this action can be completed.",
    )

    return message


def _generate_final_answer(
    question,
    tool_name,
    tool_result,
):
    tool_data = json.dumps(
        tool_result,
        indent=2,
        default=str,
    )

    prompt = f"""
You are a healthcare assistant.

Answer the user's question using ONLY the
tool result provided below.

Do not invent information.

If confirmation_required is true, clearly tell
the user that explicit confirmation is required
before the sensitive action can happen.

Do not claim that an action was completed when
confirmation_required is true.

Do not give a diagnosis or medical advice beyond
what is explicitly supported by the tool result.

Tool used:
{tool_name}

Tool result:
{tool_data}

User question:
{question}

Return ONLY valid JSON:

{{
    "answer": "clear natural-language answer"
}}
""".strip()

    result = _call_ollama(prompt)

    answer = result.get(
        "answer",
        "",
    ).strip()

    if not answer:
        raise ValueError(
            "Ollama returned an empty final answer."
        )

    return answer


def run_agent(
    question: str,
    user,
):
    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    question = question.strip()

    tool_name = _choose_tool(
        question
    )

    tool_result = _execute_tool(
        tool_name=tool_name,
        user=user,
        question=question,
    )

    # Sensitive actions must never require an LLM to
    # produce the confirmation response. This keeps
    # the safety boundary deterministic and ensures
    # cancellation requests work even when Ollama is
    # unavailable.
    if (
        tool_name == "cancel_appointment"
        and tool_result.get(
            "confirmation_required",
            False,
        )
    ):
        answer = _generate_confirmation_answer(
            tool_result
        )

        return {
            "question": question,
            "answer": answer,
            "tool": tool_name,
            "data": tool_result,
            "confirmation_required": True,
        }

    # If an appointment is already cancelled, return
    # the deterministic tool message instead of asking
    # the LLM to rewrite it.
    if (
        tool_name == "cancel_appointment"
        and not tool_result.get(
            "confirmation_required",
            False,
        )
    ):
        return {
            "question": question,
            "answer": tool_result.get(
                "message",
                "The appointment cancellation request was processed.",
            ),
            "tool": tool_name,
            "data": tool_result,
            "confirmation_required": False,
        }

    answer = _generate_final_answer(
        question=question,
        tool_name=tool_name,
        tool_result=tool_result,
    )

    return {
        "question": question,
        "answer": answer,
        "tool": tool_name,
        "data": tool_result,
        "confirmation_required": False,
    }


def confirm_agent_action(
    user,
    action,
    appointment_id,
):
    if action != "cancel_appointment":
        raise ValueError(
            "Unsupported agent action."
        )

    result = confirm_cancel_appointment(
        user=user,
        appointment_id=appointment_id,
    )

    return result
