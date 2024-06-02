from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import LimitOffsetPagination
from .models import Thread, Message
from .serializers import MessageUpdateSerializer, ThreadSerializer, MessageSerializer
from django.db.models import Q

class ThreadViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        return Thread.objects.filter(
            Q(participant1=user) | Q(participant2=user)
        )


class MessageViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        user = self.request.user
        return Message.objects.filter(
            Q(thread__participant1=user) | Q(thread__participant2=user),
            thread_id=thread_id,
        ).select_related('sender', 'thread')

    @action(detail=False, methods=['get'], url_path='unread-messages-count')
    def count_unread_messages(self, request):
        unread_count = Message.objects.filter(
            Q(thread__participant1=request.user) | Q(thread__participant2=request.user),
            is_read=False
        ).count()
        return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)


class MarkMessageAsReadView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        serializer = self.get_serializer(message, data={'is_read': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Message marked as read'}, status=status.HTTP_200_OK)
