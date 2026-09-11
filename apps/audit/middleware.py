import json

from django.utils.deprecation import MiddlewareMixin

from .services import create_audit_log


class AuditMiddleware(MiddlewareMixin):
    """
    Automatically records important authenticated API activity.

    This is intentionally lightweight:
    - GET  -> VIEW
    - POST -> CREATE
    - PUT/PATCH -> UPDATE
    - DELETE -> DELETE

    AI and confirmation endpoints receive semantic action names.
    """

    EXCLUDED_PATHS = {
        "/admin/",
        "/api/audit/",
    }

    def process_response(self, request, response):
        if not request.path.startswith("/api/"):
            return response

        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return response

        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            return response

        # Don't create audit noise for failed requests.
        if response.status_code >= 400:
            return response

        method = request.method.upper()

        action_map = {
            "GET": "VIEW",
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
        }

        action = action_map.get(method)

        if not action:
            return response

        path = request.path.lower()

        # More meaningful actions for important endpoints.
        if "/auth/login" in path:
            action = "LOGIN"
        elif "/auth/logout" in path:
            action = "LOGOUT"
        elif "/ai/ask" in path:
            action = "AI_QUERY"
        elif "/ai/agent/confirm" in path:
            action = "AI_CONFIRM"
        elif "/ai/agent" in path:
            action = "AI_ACTION"
        elif "/documents" in path and method == "POST":
            action = "UPLOAD"
        elif "/appointments" in path and method == "DELETE":
            action = "CANCEL"

        resource_type = "API"
        resource_id = None

        path_parts = [part for part in request.path.split("/") if part]

        if len(path_parts) >= 2:
            resource_type = path_parts[1]

        if path_parts and path_parts[-1].isdigit():
            resource_id = int(path_parts[-1])

        description = f"{method} {request.path} -> {response.status_code}"

        metadata = {
            "method": method,
            "path": request.path,
            "status_code": response.status_code,
        }

        try:
            create_audit_log(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                request=request,
                metadata=metadata,
            )
        except Exception:
            # Audit logging must never break the actual API request.
            pass

        return response