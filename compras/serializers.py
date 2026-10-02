"""
==============================================================================
MÓDULO: COMPRAS - SERIALIZADORES DRF
==============================================================================
Serializadores para Órdenes de Compra, Detalle y Entradas/Tickets
utilizando las relaciones inversas reales (detalleorden_set, entrada_set).
==============================================================================
"""

from rest_framework import serializers
from .models import Orden, DetalleOrden, Entrada
from eventos.serializers import SectorSerializer


class EntradaSerializer(serializers.ModelSerializer):
    """
    Serializador para las entradas/tickets con código UUID único.
    """
    sector_nombre = serializers.CharField(source='sector.nombre_sector', read_only=True)
    evento_titulo = serializers.CharField(source='sector.evento.titulo', read_only=True)

    class Meta:
        model = Entrada
        fields = ['id', 'uuid', 'sector_nombre', 'evento_titulo', 'fecha_emision', 'estado']


class DetalleOrdenSerializer(serializers.ModelSerializer):
    """
    Serializador para el detalle histórico de productos en la orden.
    """
    sector_detalle = SectorSerializer(source='sector', read_only=True)

    class Meta:
        model = DetalleOrden
        fields = ['id', 'sector', 'sector_detalle', 'cantidad', 'precio_unitario_historico']


class OrdenSerializer(serializers.ModelSerializer):
    """
    Serializador de la Orden de Compra mapeando detalleorden_set y entrada_set.
    """
    detalles = DetalleOrdenSerializer(
        source='detalleorden_set',
        many=True,
        read_only=True
    )
    entradas = EntradaSerializer(
        source='entrada_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Orden
        fields = [
            'id', 'usuario', 'fecha_orden', 'total',
            'estado', 'stock_descontado', 'detalles', 'entradas'
        ]
        read_only_fields = ['id', 'usuario', 'fecha_orden', 'total', 'estado', 'stock_descontado']