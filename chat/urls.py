from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThreadViewSet, MessageViewSet, MarkMessageAsReadView, MarkMessageAsReadView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'threads', ThreadViewSet, basename='thread')
router.register(r'threads/(?P<thread_id>\d+)/messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('messages/<int:pk>/mark-as-read/', MarkMessageAsReadView.as_view(), name='message-mark-as-read'),
    path('messages/unread-messages-count/', MessageViewSet.as_view({'get': 'count_unread_messages'}), name='unread-messages-count'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
