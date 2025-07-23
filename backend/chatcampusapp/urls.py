from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView, TokenRefreshView

from .views import UserRetrieveUpdateAPIView, UserCreateAPIView

urlpatterns = [
    path('sso-auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("auth/register/", UserCreateAPIView.as_view(), name="register"),
    path("user/me/", UserRetrieveUpdateAPIView.as_view(), name="user-profile"),
]
