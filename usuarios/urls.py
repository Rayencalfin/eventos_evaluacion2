"""
==============================================================================
MÓDULO: USUARIOS - ENRUTADOR DE URLS
==============================================================================
Rutas para autenticación JWT y perfil de usuario.
==============================================================================
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .tokens import CustomTokenObtainPairView

app_name = 'usuarios'

urlpatterns = [
    # Endpoints API REST JWT
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]