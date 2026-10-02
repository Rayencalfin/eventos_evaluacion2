"""
==============================================================================
MÓDULO: USUARIOS - ENRUTADOR WEB
==============================================================================
Rutas de plantillas HTML para autenticación de sesión de usuarios.
==============================================================================
"""

from django.urls import path
from .views_web import login_web, registro_web, logout_web

app_name = 'usuarios_web'

urlpatterns = [
    path('login/', login_web, name='login'),
    path('registro/', registro_web, name='registro'),
    path('logout/', logout_web, name='logout'),
]