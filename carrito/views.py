"""
==============================================================================
MÓDULO: CARRITO - VISTAS DRF
==============================================================================
Endpoints para consultar y administrar el carrito persistente del Espectador,
con manejo seguro de conversiones numéricas.
==============================================================================
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from api.permissions import IsEspectador
from .models import Carro, ItemCarro
from .serializers import CarroSerializer
from eventos.models import Sector


class CarroUsuarioView(APIView):
    """
    Obtiene o crea automáticamente el carrito persistente del usuario autenticado.
    """
    permission_classes = [IsEspectador]

    def get(self, request):
        carro, _ = Carro.objects.get_or_create(usuario=request.user)
        serializer = CarroSerializer(carro)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgregarItemCarroView(APIView):
    """
    Agrega un sector al carrito o actualiza la cantidad si ya existe.
    """
    permission_classes = [IsEspectador]

    def post(self, request):
        sector_id = request.data.get('sector')
        cantidad_raw = request.data.get('cantidad', 1)

        try:
            cantidad = int(cantidad_raw)
            if cantidad <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {"error": "La cantidad debe ser un número entero mayor a 0."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sector = Sector.objects.get(id=sector_id)
        except Sector.DoesNotExist:
            return Response(
                {"error": "El sector especificado no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        if sector.stock_disponible < cantidad:
            return Response(
                {"error": f"Stock insuficiente. Disponible: {sector.stock_disponible}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        carro, _ = Carro.objects.get_or_create(usuario=request.user)
        item, created = ItemCarro.objects.get_or_create(carro=carro, sector=sector)

        if not created:
            nueva_cantidad = item.cantidad + cantidad
            if sector.stock_disponible < nueva_cantidad:
                return Response(
                    {"error": f"Stock insuficiente. Máximo disponible: {sector.stock_disponible}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.cantidad = nueva_cantidad
        else:
            item.cantidad = cantidad

        item.save()
        return Response(
            CarroSerializer(carro).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class EliminarItemCarroView(APIView):
    """
    Elimina un ítem específico del carrito de compras.
    """
    permission_classes = [IsEspectador]

    def delete(self, request, item_id):
        try:
            item = ItemCarro.objects.get(id=item_id, carro__usuario=request.user)
            item.delete()
            return Response({"mensaje": "Item eliminado del carrito."}, status=status.HTTP_200_OK)
        except ItemCarro.DoesNotExist:
            return Response({"error": "El ítem no existe en su carrito."}, status=status.HTTP_404_NOT_FOUND)
        