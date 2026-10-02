"""
==============================================================================
MÓDULO: MANEJO GLOBAL DE ERRORES HTTP (FRONTEND WEB)
==============================================================================
Vistas personalizadas para renderizar plantillas estilizadas en caso de
errores HTTP 400, 403, 404 y 500 dentro del ciclo web de Django.
==============================================================================
"""

from django.shortcuts import render


def custom_bad_request_view(request, exception=None):
    """Manejador personalizado para errores 400 Bad Request."""
    return render(request, '400.html', status=400)


def custom_permission_denied_view(request, exception=None):
    """Manejador personalizado para errores 403 Forbidden manejados por Django."""
    return render(request, '403.html', status=403)


def custom_page_not_found_view(request, exception=None):
    """Manejador personalizado para errores 404 Not Found."""
    return render(request, '404.html', status=404)


def custom_server_error_view(request):
    """Manejador personalizado para errores 500 Internal Server Error."""
    return render(request, '500.html', status=500)