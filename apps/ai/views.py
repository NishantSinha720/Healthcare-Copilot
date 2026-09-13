from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.services.rag_service import ask_question

from .services.agent_service import (
    confirm_agent_action,
    run_agent,
)


class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "example": "What medications am I taking?",
                    }
                },
                "required": ["question"],
            }
        },
        responses={
            200: OpenApiResponse(
                description="Grounded AI answer with document sources."
            ),
            400: OpenApiResponse(
                description="Question is missing or invalid."
            ),
            401: OpenApiResponse(
                description="Authentication required."
            ),
            403: OpenApiResponse(
                description="User does not have permission."
            ),
            500: OpenApiResponse(
                description="AI question answering failed."
            ),
        },
        examples=[
            OpenApiExample(
                "Question",
                value={
                    "question": (
                        "What medications am I currently taking?"
                    )
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        question = request.data.get(
            "question",
            "",
        ).strip()

        if not question:
            return Response(
                {"detail": "Question is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sensitive appointment cancellation must require
        # explicit confirmation and must not depend on Ollama.
        question_lower = question.lower()

        if (
            "appointment" in question_lower
            and (
                "cancel" in question_lower
                or "cancellation" in question_lower
                or "cancelling" in question_lower
                or "canceling" in question_lower
            )
        ):
            return Response(
                {
                    "question": question,
                    "answer": (
                        "Appointment cancellation requires "
                        "an appointment ID and explicit confirmation."
                    ),
                    "tool": "cancel_appointment",
                    "data": {
                        "confirmation_required": True,
                        "action": "cancel_appointment",
                        "message": (
                            "Appointment cancellation requires "
                            "an appointment ID and explicit confirmation."
                        ),
                    },
                    "confirmation_required": True,
                },
                status=status.HTTP_200_OK,
            )

        try:
            result = ask_question(
                question=question,
                user=request.user,
            )

            return Response(
                result,
                status=status.HTTP_200_OK,
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except PermissionError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        except Exception as exc:
            return Response(
                {
                    "detail": (
                        "AI question answering failed."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AgentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "example": (
                            "What medications am I taking?"
                        ),
                    }
                },
                "required": ["question"],
            }
        },
        responses={
            200: OpenApiResponse(
                description=(
                    "AI agent response, including tool execution "
                    "and confirmation information when applicable."
                )
            ),
            400: OpenApiResponse(
                description="Question is missing or invalid."
            ),
            401: OpenApiResponse(
                description="Authentication required."
            ),
            403: OpenApiResponse(
                description="User does not have permission."
            ),
            500: OpenApiResponse(
                description="AI agent failed."
            ),
        },
    )
    def post(self, request):
        question = request.data.get(
            "question",
            "",
        ).strip()

        if not question:
            return Response(
                {"detail": "Question is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = run_agent(
                question=question,
                user=request.user,
            )

            return Response(
                result,
                status=status.HTTP_200_OK,
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except PermissionError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        except Exception as exc:
            return Response(
                {
                    "detail": "AI agent failed.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AgentConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "example": "cancel_appointment",
                    },
                    "appointment_id": {
                        "type": "integer",
                        "example": 1,
                    },
                },
                "required": [
                    "action",
                    "appointment_id",
                ],
            }
        },
        responses={
            200: OpenApiResponse(
                description="Confirmed agent action executed."
            ),
            400: OpenApiResponse(
                description="Invalid confirmation request."
            ),
            401: OpenApiResponse(
                description="Authentication required."
            ),
            403: OpenApiResponse(
                description="User is not permitted to perform the action."
            ),
            500: OpenApiResponse(
                description="Agent action failed."
            ),
        },
    )
    def post(self, request):
        action = request.data.get(
            "action",
            "",
        ).strip()

        appointment_id = request.data.get(
            "appointment_id"
        )

        if not action:
            return Response(
                {"detail": "Action is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if appointment_id is None:
            return Response(
                {
                    "detail": (
                        "appointment_id is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment_id = int(
                appointment_id
            )
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": (
                        "appointment_id must be an integer."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = confirm_agent_action(
                user=request.user,
                action=action,
                appointment_id=appointment_id,
            )

            return Response(
                result,
                status=status.HTTP_200_OK,
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except PermissionError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        except Exception as exc:
            return Response(
                {
                    "detail": "Agent action failed.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )