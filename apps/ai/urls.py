from django.urls import path

from .views import (
    AgentConfirmView,
    AgentView,
    AskQuestionView,
)


urlpatterns = [
    path(
        "ask/",
        AskQuestionView.as_view(),
        name="ai-ask",
    ),
    path(
        "agent/",
        AgentView.as_view(),
        name="ai-agent",
    ),
    path(
        "agent/confirm/",
        AgentConfirmView.as_view(),
        name="ai-agent-confirm",
    ),
]