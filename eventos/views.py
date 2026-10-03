"""
==============================================================================
MÓDULO: EVENTOS - VISTAS DRF
==============================================================================
ModelViewSets protegidos con permisos RBAC (IsOrganizadorOrReadOnly).
==============================================================================
"""

from rest_framework import viewsets
from api.permissions import IsOrganizadorOrReadOnly
from .models import Artista, Recinto, Evento, Sector
from django.shortcuts import render
from .serializers import (
    ArtistaSerializer,
    RecintoSerializer,
    SectorSerializer,
    EventoDetalleSerializer
)


class ArtistaViewSet(viewsets.ModelViewSet):
    queryset = Artista.objects.all()
    serializer_class = ArtistaSerializer
    permission_classes = [IsOrganizadorOrReadOnly]


class RecintoViewSet(viewsets.ModelViewSet):
    queryset = Recinto.objects.all()
    serializer_class = RecintoSerializer
    permission_classes = [IsOrganizadorOrReadOnly]


class EventoViewSet(viewsets.ModelViewSet):
    queryset = (
        Evento.objects
        .all()
        .select_related('artista', 'recinto')
        .prefetch_related('sector_set')
    )
    serializer_class = EventoDetalleSerializer
    permission_classes = [IsOrganizadorOrReadOnly]


class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.all().select_related('evento')
    serializer_class = SectorSerializer
    permission_classes = [IsOrganizadorOrReadOnly]


def error_404_view(request, exception=None):
    return render(request, '404.html', status=404)