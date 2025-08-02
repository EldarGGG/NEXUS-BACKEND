from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *
from .auth_views import AuthLoginView, AuthSignupView

router = DefaultRouter()

urlpatterns = [
    path('signup/', create_user, name='signup'),
    path('', index_view, name='index_view'),
    path('', include(router.urls)),
    path('api/v1/signup/', UserCreationAPIView.as_view()),
    path('api/v1/token/', CreateTokenView.as_view()),
    path('api/v1/telegram/token/', CreateTgTokenView.as_view()),
    # New auth endpoints that match frontend expectations
    path('auth/login/', AuthLoginView.as_view(), name='auth_login'),
    path('auth/signup/', AuthSignupView.as_view(), name='auth_signup'),
]
