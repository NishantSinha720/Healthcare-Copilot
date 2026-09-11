from rest_framework.permissions import BasePermission

from .models import User


class IsAdmin(BasePermission):
    """
    Allows access only to ADMIN users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsDoctor(BasePermission):
    """
    Allows access only to DOCTOR users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.DOCTOR
        )


class IsPatient(BasePermission):
    """
    Allows access only to PATIENT users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.PATIENT
        )


class IsAdminOrDoctor(BasePermission):
    """
    Allows access to ADMIN or DOCTOR users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            in [User.Role.ADMIN, User.Role.DOCTOR]
        )