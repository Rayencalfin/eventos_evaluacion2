"""
==============================================================================
MÓDULO: USUARIOS - CUSTOM CLAIMS JWT
==============================================================================
Sobreescribe TokenObtainPairSerializer de SimpleJWT para inyectar
los campos 'rol' y 'email' en el Payload del token desencriptado.
==============================================================================
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador de JWT personalizado que agrega claims de rol y email al token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Inyección de claims personalizados en el Payload del JWT
        token['email'] = user.email
        token['rol'] = user.rol
        token['username'] = user.username

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Información de retorno adicional en la respuesta JSON del endpoint /api/token/
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['username'] = self.user.username
        data['rol'] = self.user.rol
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista DRF para obtener el par de tokens JWT con los claims personalizados.
    """
    serializer_class = CustomTokenObtainPairSerializer
    