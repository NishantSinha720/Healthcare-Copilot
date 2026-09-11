import pytest


@pytest.mark.django_db
def test_user_can_be_created():
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.create_user(
        username="pytest_user",
        email="pytest@example.com",
        password="TestPassword123!",
        role=User.Role.PATIENT,
    )

    assert user.id is not None
    assert user.role == User.Role.PATIENT
    assert user.check_password(
        "TestPassword123!"
    )


@pytest.mark.django_db
def test_authenticated_me_endpoint():
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient

    User = get_user_model()

    user = User.objects.create_user(
        username="pytest_me",
        email="pytest_me@example.com",
        password="TestPassword123!",
        role=User.Role.PATIENT,
    )

    client = APIClient()

    response = client.post(
        "/api/auth/login/",
        {
            "username": "pytest_me",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "tokens" in response.data
    assert "access" in response.data["tokens"]
    assert "refresh" in response.data["tokens"]

    client.credentials(
        HTTP_AUTHORIZATION=(
            f"Bearer {response.data['tokens']['access']}"
        )
    )

    response = client.get(
        "/api/auth/me/"
    )

    assert response.status_code == 200
    assert response.data["username"] == user.username


@pytest.mark.django_db
def test_unauthenticated_ai_agent_is_rejected():
    from rest_framework.test import APIClient

    client = APIClient()

    response = client.post(
        "/api/ai/agent/",
        {
            "question": "What medications am I taking?"
        },
        format="json",
    )

    assert response.status_code == 401