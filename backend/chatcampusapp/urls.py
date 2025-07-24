from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView, TokenRefreshView
from .views import HomePageAPIView, RoomDetailMessageCreateAPIView, RoomTopicCreateUpdateRetrieveDeleteListAPIView, TopicListAPIView, UserProfileAPIView, UserRetrieveUpdateAPIView, UserCreateAPIView

urlpatterns = [
    path('sso-auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("auth/register/", UserCreateAPIView.as_view(), name="register"),
    path("user/me/", UserRetrieveUpdateAPIView.as_view(), name="user-profile"),
    path("rooms/", RoomTopicCreateUpdateRetrieveDeleteListAPIView.as_view(),
         name="room-topic-create-list"),
    path("rooms/<int:pk>/", RoomTopicCreateUpdateRetrieveDeleteListAPIView.as_view(),
         name="room-get-update-delete"),
    path("topics/", TopicListAPIView.as_view(), name="topic-list"),
    path("roomDetails/<int:pk>/", RoomDetailMessageCreateAPIView.as_view(),
         name="room-details-message-create"),
    path("", HomePageAPIView.as_view(), name="homepage"),
    path("user/profile/<int:pk>/",
         UserProfileAPIView.as_view(), name="user-profile"),
]
