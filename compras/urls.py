"""
==============================================================================
MÓDULO: COMPRAS - ENRUTADOR DE URLS
==============================================================================
Rutas API para pago, historial de órdenes y consulta de entradas emitidas.
==============================================================================
"""

from django.urls import path
from .views import CheckoutView, MisOrdenesView, MisEntradasView

app_name = 'compras'

urlpatterns = [
    path('api/compras/pagar/', CheckoutView.as_view(), name='pagar'),
    path('api/mis-ordenes/', MisOrdenesView.as_view(), name='mis_ordenes'),
    path('api/mis-entradas/', MisEntradasView.as_view(), name='mis_entradas'),
]