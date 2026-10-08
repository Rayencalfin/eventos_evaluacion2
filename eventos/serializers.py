"""
==============================================================================
MÓDULO: EVENTOS - SERIALIZADORES DRF
==============================================================================
Serializadores para la consulta pública del catálogo: Artistas, Recintos,
Sectores y Eventos con información anidada.
==============================================================================
"""

from rest_framework import serializers
from .models import Artista, Recinto, Evento, Sector


class ArtistaSerializer(serializers.ModelSerializer):
    """
    Serializador para información de Artistas.
    """
    class Meta:
        model = Artista
        fields = '__all__'


class RecintoSerializer(serializers.ModelSerializer):
    """
    Serializador para información de Recintos.
    """
    class Meta:
        model = Recinto
        fields = '__all__'



class SectorSerializer(serializers.ModelSerializer):
    """
    Serializador para consulta de Sectores / Localidades.
    """
    class Meta:
        model = Sector
        fields = '__all__'
        read_only_fields = ['id']


class EventoDetalleSerializer(serializers.ModelSerializer):
    """
    Serializador de lectura completa para Eventos, incluyendo datos anidados
    de Artista, Recinto y la lista de Sectores disponibles mapeada desde sector_set.
    """
    artista = ArtistaSerializer(read_only=True)
    recinto = RecintoSerializer(read_only=True)
    sectores = SectorSerializer(
        source='sector_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Evento
        fields = [
            'id',
            'titulo',
            'artista',
            'recinto',
            'fecha_hora',
            'descripcion',
            'banner',
            'estado',
            'sectores'
        ]