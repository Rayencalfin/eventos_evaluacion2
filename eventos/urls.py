"""
==============================================================================
MÓDULO: EVENTOS - ENRUTADOR DE URLS
==============================================================================
Registra los ViewSets de lectura de eventos, artistas, recintos y sectores
en el router oficial de DRF.
==============================================================================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArtistaViewSet, RecintoViewSet, EventoViewSet, SectorViewSet

app_name = 'eventos'

router = DefaultRouter()
router.register(r'artistas', ArtistaViewSet, basename='artista')
router.register(r'recintos', RecintoViewSet, basename='recinto')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'sectores', SectorViewSet, basename='sector')

urlpatterns = [
    path('api/', include(router.urls)),
]