from django.urls import path
from .views_auth import LoginView, MeView, LogoutView, ForgotPasswordView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/me/', MeView.as_view(), name='auth_me'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/forgot/', ForgotPasswordView.as_view(), name='auth_forgot'),
]

