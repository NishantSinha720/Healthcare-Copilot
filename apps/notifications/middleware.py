from urllib.parse import parse_qs

from asgiref.sync import sync_to_async


def _authenticate_token(token):
    from django.contrib.auth.models import AnonymousUser
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

    try:
        authentication = JWTAuthentication()
        validated_token = authentication.get_validated_token(token)
        return authentication.get_user(validated_token)

    except (InvalidToken, AuthenticationFailed):
        return AnonymousUser()

    except Exception:
        return AnonymousUser()


@sync_to_async(thread_sensitive=True)
def get_user_from_token(token):
    return _authenticate_token(token)


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser

        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)

        token_values = query_params.get("token", [])
        token = token_values[0] if token_values else None

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)