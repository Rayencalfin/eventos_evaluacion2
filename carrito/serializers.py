"""
==============================================================================
MÓDULO: CARRITO - SERIALIZADORES DRF
==============================================================================
Serializadores para consultar y gestionar el carrito de compras persistente
utilizando las relaciones inversas reales (itemcarro_set).
==============================================================================
"""

from rest_framework import serializers
from .models import Carro, ItemCarro
from eventos.serializers import SectorSerializer


class ItemCarroSerializer(serializers.ModelSerializer):
    """
    Serializador para los ítems dentro del carrito de compras.
    """
    sector_detalle = SectorSerializer(source='sector', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarro
        fields = ['id', 'sector', 'sector_detalle', 'cantidad', 'subtotal', 'fecha_agregado']
        read_only_fields = ['id', 'fecha_agregado']

    def get_subtotal(self, obj):
        return obj.cantidad * obj.sector.precio


class CarroSerializer(serializers.ModelSerializer):
    """
    Serializador del carrito de compras completo del usuario.
    Mapea la relación inversa por defecto itemcarro_set.
    """
    items = ItemCarroSerializer(
        source='itemcarro_set',
        many=True,
        read_only=True
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carro
        fields = ['id', 'usuario', 'fecha_creacion', 'fecha_actualizacion', 'items', 'total']
        read_only_fields = ['id', 'usuario', 'fecha_creacion', 'fecha_actualizacion']

    def get_total(self, obj):
        return sum(
            item.cantidad * item.sector.precio
            for item in obj.itemcarro_set.all()
        )