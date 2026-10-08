"""
==============================================================================
MÓDULO: CARRITO - ENRUTADOR WEB
==============================================================================
Rutas de plantillas HTML para la gestión del carrito de compras.
==============================================================================
"""

from django.urls import path
from .views_web import ver_carro_web, agregar_carro_web, eliminar_carro_web

app_name = 'carrito_web'

urlpatterns = [
    path('carro/', ver_carro_web, name='ver_carro'),
    path('carro/agregar/<int:sector_id>/', agregar_carro_web, name='agregar_item'),
    path('carro/eliminar/<int:sector_id>/', eliminar_carro_web, name='eliminar_carro'),
]