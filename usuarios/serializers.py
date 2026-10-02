"""
==============================================================================
MÓDULO: USUARIOS - SERIALIZADORES DRF
==============================================================================
Serializadores para registro de usuarios y consulta de perfil.
==============================================================================
"""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de nuevos usuarios Espectadores.
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'password', 'rol']
        read_only_fields = ['id', 'rol']  # El rol por defecto siempre es Espectador al registrarse

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['rol'] = Usuario.RolChoices.ESPECTADOR
        return super().create(validated_data)


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """
    Serializador para consultar los datos del usuario autenticado.
    """
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'rol', 'date_joined']
        read_only_fields = ['id', 'email', 'rol', 'date_joined']