from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    @extend_schema(
        responses={
            200: NotificationSerializer(many=True),
            401: OpenApiResponse(
                description="Authentication required."
            ),
        }
    )
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        )


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: NotificationSerializer,
            401: OpenApiResponse(
                description="Authentication required."
            ),
            404: OpenApiResponse(
                description="Notification not found."
            ),
        }
    )
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=request.user,
            )
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        notification.is_read = True

        notification.save(
            update_fields=["is_read"]
        )

        return Response(
            NotificationSerializer(
                notification
            ).data,
            status=status.HTTP_200_OK,
        )


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="All unread notifications were marked as read."
            ),
            401: OpenApiResponse(
                description="Authentication required."
            ),
        }
    )
    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(
            is_read=True
        )

        return Response(
            {
                "message": "Notifications marked as read.",
                "updated_count": updated,
            },
            status=status.HTTP_200_OK,
        )