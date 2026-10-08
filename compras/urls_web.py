"""
==============================================================================
MÓDULO: COMPRAS - ENRUTADOR WEB
==============================================================================
Rutas de plantillas HTML para pago, historial de órdenes y tickets emitidos.
Ruta limpia /compras/pagar/ (evita duplicación de namespace).
==============================================================================
"""

from django.urls import path
from .views_web import pagar_web, mis_ordenes_web, mis_entradas_web, cancelar_orden_web

app_name = 'compras_web'

urlpatterns = [
    path('pagar/', pagar_web, name='pagar'),
    path('mis-ordenes/', mis_ordenes_web, name='mis_ordenes'),
    path('mis-entradas/', mis_entradas_web, name='mis_entradas'),
    path('orden/<int:orden_id>/cancelar/', cancelar_orden_web, name='cancelar_orden'),
]