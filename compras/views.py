"""
==============================================================================
MÓDULO: COMPRAS - VISTAS DRF (TRANSACCIONES ACID)
==============================================================================
Gestiona el proceso de pago atómico (@transaction.atomic) ordenando los IDs
para evitar deadlocks y consultando las relaciones inversas correspondientes.
==============================================================================
"""

from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from api.permissions import IsEspectador
from carrito.models import Carro
from .models import Orden, DetalleOrden, Entrada
from .serializers import OrdenSerializer, EntradaSerializer
from eventos.models import Sector


class CheckoutView(APIView):
    """
    Procesa el pago de forma atómica. Ordena los IDs de los sectores para prevenir
    deadlocks y aplica el descuento en la base de datos dentro de la transacción.
    """
    permission_classes = [IsEspectador]

    @transaction.atomic
    def post(self, request):
        try:
            carro = Carro.objects.get(usuario=request.user)
        except Carro.DoesNotExist:
            return Response({"error": "El usuario no posee un carrito activo."}, status=status.HTTP_400_BAD_REQUEST)

        items = list(carro.itemcarro_set.select_related('sector').all())
        if not items:
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Bloqueo pesimista ordenado por ID para prevenir deadlocks en PostgreSQL
        sectores_ids_ordenados = sorted(set(item.sector_id for item in items))
        sectores_map = {
            s.id: s for s in Sector.objects.select_for_update().filter(id__in=sectores_ids_ordenados)
        }

        total_orden = 0
        for item in items:
            sector = sectores_map[item.sector_id]
            if sector.stock_disponible < item.cantidad:
                return Response(
                    {"error": f"Stock insuficiente para '{sector.nombre_sector}'. Disponible: {sector.stock_disponible}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            total_orden += item.cantidad * sector.precio

        # 2. Creación de la Orden
        orden = Orden.objects.create(
            usuario=request.user,
            total=total_orden,
            estado=Orden.EstadoChoices.PAGADO,
            stock_descontado=True
        )

        # 3. Creación del Detalle, Descuento de Stock y Emisión de Entradas UUID
        for item in items:
            sector = sectores_map[item.sector_id]

            # Registrar detalle con precio histórico congelado
            DetalleOrden.objects.create(
                orden=orden,
                sector=sector,
                cantidad=item.cantidad,
                precio_unitario_historico=sector.precio
            )

            # Descontar stock
            sector.stock_disponible -= item.cantidad
            sector.save()

            # Emitir ticket individual por cada unidad comprada
            for _ in range(item.cantidad):
                Entrada.objects.create(
                    orden=orden,
                    sector=sector,
                    estado=Entrada.EstadoChoices.VALIDA
                )

        # 4. Vaciar carrito tras la compra exitosa
        carro.itemcarro_set.all().delete()

        serializer = OrdenSerializer(orden)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MisOrdenesView(APIView):
    """
    Consulta el historial de órdenes del espectador autenticado.
    """
    permission_classes = [IsEspectador]

    def get(self, request):
        ordenes = Orden.objects.filter(usuario=request.user).prefetch_related('detalleorden_set', 'entrada_set')
        serializer = OrdenSerializer(ordenes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MisEntradasView(APIView):
    """
    Consulta todas las entradas / tickets emitidos del espectador autenticado.
    """
    permission_classes = [IsEspectador]

    def get(self, request):
        entradas = Entrada.objects.filter(orden__usuario=request.user).select_related('sector', 'sector__evento')
        serializer = EntradaSerializer(entradas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)