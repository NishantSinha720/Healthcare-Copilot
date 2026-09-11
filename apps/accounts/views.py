from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import (
    IsAdmin,
    IsAdminOrDoctor,
    IsDoctor,
    IsPatient,
)
from .serializers import (
    LoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    permission_classes = []

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(
                description="Invalid registration data."
            ),
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "message": "Registration successful.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Login successful. Returns user data and JWT tokens."
            ),
            400: OpenApiResponse(
                description="Invalid username or password."
            ),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: UserSerializer,
            401: OpenApiResponse(
                description="Authentication credentials were not provided or are invalid."
            ),
        },
    )
    def get(self, request):
        serializer = UserSerializer(
            request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class PatientOnlyView(APIView):
    permission_classes = [IsPatient]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Patient endpoint accessed successfully."
            ),
            403: OpenApiResponse(
                description="User is not a patient."
            ),
        },
    )
    def get(self, request):
        return Response(
            {
                "message": (
                    "Patient endpoint accessed successfully."
                ),
                "role": request.user.role,
            },
            status=status.HTTP_200_OK,
        )


class DoctorOnlyView(APIView):
    permission_classes = [IsDoctor]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Doctor endpoint accessed successfully."
            ),
            403: OpenApiResponse(
                description="User is not a doctor."
            ),
        },
    )
    def get(self, request):
        return Response(
            {
                "message": (
                    "Doctor endpoint accessed successfully."
                ),
                "role": request.user.role,
            },
            status=status.HTTP_200_OK,
        )


class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Admin endpoint accessed successfully."
            ),
            403: OpenApiResponse(
                description="User is not an administrator."
            ),
        },
    )
    def get(self, request):
        return Response(
            {
                "message": (
                    "Admin endpoint accessed successfully."
                ),
                "role": request.user.role,
            },
            status=status.HTTP_200_OK,
        )


class AdminOrDoctorView(APIView):
    permission_classes = [IsAdminOrDoctor]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description=(
                    "Admin/Doctor endpoint accessed successfully."
                )
            ),
            403: OpenApiResponse(
                description=(
                    "User is neither an administrator nor a doctor."
                )
            ),
        },
    )
    def get(self, request):
        return Response(
            {
                "message": (
                    "Admin/Doctor endpoint accessed successfully."
                ),
                "role": request.user.role,
            },
            status=status.HTTP_200_OK,
        )