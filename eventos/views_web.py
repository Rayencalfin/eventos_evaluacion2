"""
==============================================================================
MÓDULO: EVENTOS - CONTROLADORES WEB PÚBLICOS
==============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from .models import Evento


def index_web(request):
    """Catálogo público de conciertos para la interfaz de cliente."""
    eventos = (
        Evento.objects
        .filter(estado__in=['Activo', 'Publicado', 'ACTIVO', 'PUBLICADO'])
        .select_related('artista', 'recinto')
        .prefetch_related('sectores')
        .order_by('fecha_hora')
    )
    return render(request, 'index.html', {'eventos': eventos})


def detalle_evento_web(request, evento_id):
    """Muestra el detalle del evento o redirige al login si no está autenticado."""
    if not request.user.is_authenticated:
        return redirect('usuarios_web:login')

    evento = get_object_or_404(
        Evento.objects.select_related('artista', 'recinto').prefetch_related('sectores'),
        id=evento_id
    )
    return render(request, 'eventos/detalle_evento.html', {'evento': evento})