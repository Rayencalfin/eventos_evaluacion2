"""
==============================================================================
MÓDULO: CARRITO - ENRUTADOR DE URLS
==============================================================================
Rutas API para la gestión del carrito de compras persistente.
==============================================================================
"""

from django.urls import path
from .views import CarroUsuarioView, AgregarItemCarroView, EliminarItemCarroView

app_name = 'carrito'

urlpatterns = [
    path('api/carro/', CarroUsuarioView.as_view(), name='ver_carro'),
    path('api/carro/agregar/', AgregarItemCarroView.as_view(), name='agregar_item'),
    path('api/carro/item/<int:item_id>/eliminar/', EliminarItemCarroView.as_view(), name='eliminar_item'),
]