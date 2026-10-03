"""
==============================================================================
PROYECTO: VENTA DE ENTRADAS PARA EVENTOS Y CONCIERTOS
Estudiante: Rayen Alejandra Calfin Melivilu | Sección: AP_N4_C1 | Año: 2026
------------------------------------------------------------------------------
DESCRIPCIÓN DEL ARCHIVO:
Enrutador principal de URLs del proyecto e integración de manejadores de error HTTP.
==============================================================================
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from api.permissions import IsOrganizador


class ProtectedSpectacularAPIView(SpectacularAPIView):
    permission_classes = [IsOrganizador]


class ProtectedSpectacularSwaggerView(SpectacularSwaggerView):
    permission_classes = [IsOrganizador]


class ProtectedSpectacularRedocView(SpectacularRedocView):
    permission_classes = [IsOrganizador]


urlpatterns = [
    # Panel nativo de Django (Uso técnico/interno)
    path('admin/', admin.site.urls),

    # Documentación interactiva de la API REST (Solo Organizador)
    path('api/schema/', ProtectedSpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', ProtectedSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', ProtectedSpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Rutas Web (Django Templates)
    path('', include('eventos.urls_web', namespace='eventos_web')),
    path('cuenta/', include('usuarios.urls_web', namespace='usuarios_web')),
    path('compras/', include('carrito.urls_web', namespace='carrito_web')),
    path('compras/', include('compras.urls_web', namespace='compras_web')),

    # Rutas API REST (DRF & JWT)
    path('', include('usuarios.urls', namespace='usuarios')),
    path('', include('eventos.urls', namespace='eventos')),
    path('', include('carrito.urls', namespace='carrito')),
    path('', include('compras.urls', namespace='compras')),
]

# ==============================================================================
# MANEJADORES GLOBALES DE ERRORES HTTP (NAVEGACIÓN WEB)
# ==============================================================================
handler400 = 'eventos.views_error.custom_bad_request_view'
handler403 = 'eventos.views_error.custom_permission_denied_view'
handler404 = 'eventos.views_error.custom_page_not_found_view'
handler500 = 'eventos.views_error.custom_server_error_view'
handler404 = 'eventos.views.error_404_view'
