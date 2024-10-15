from django.urls import path
from .views import AuthenticationViewSet

urlpatterns = [
    path('register/', AuthenticationViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', AuthenticationViewSet.as_view({'post': 'login'}), name='login'),
    path('change/password/', AuthenticationViewSet.as_view({'post': 'change_password'})),
    path('me/', AuthenticationViewSet.as_view({'get': 'auth_me'})),
]
