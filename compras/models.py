"""
==============================================================================
MÓDULO: COMPRAS - MODELOS DE DATOS
==============================================================================
Gestiona las Órdenes, Detalle de Compras y la generación de Entradas con UUID.
Controla estados, precio histórico congelado y seguridad de stock.
==============================================================================
"""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from eventos.models import Sector


class Orden(models.Model):
    """
    Representa la orden de compra realizada por un cliente Espectador.
    """
    class EstadoChoices(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PAGADO = 'PAGADO', 'Pagado'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ordenes',
        verbose_name="Usuario Comprador"
    )
    fecha_orden = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Orden")
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto Total"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.PENDIENTE,
        verbose_name="Estado de la Orden"
    )
    stock_descontado = models.BooleanField(
        default=False,
        verbose_name="Stock Descontado",
        help_text="Indica si el stock ya fue procesado en el catálogo."
    )
    stock_repuesto = models.BooleanField(
        default=False,
        verbose_name="Stock Repuesto",
        help_text="Garantiza que una orden cancelada solo reponga stock una vez."
    )

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-fecha_orden']

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.email} ({self.estado})"


class DetalleOrden(models.Model):
    """
    Detalle de ítems comprados dentro de una orden.
    Guarda el precio unitario histórico para no depender del precio actual del catálogo.
    """
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Orden de Compra"
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        related_name='detalles_orden',
        verbose_name="Sector Comprado"
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )
    precio_unitario_historico = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio Unitario Histórico"
    )

    class Meta:
        verbose_name = "Detalle de Orden"
        verbose_name_plural = "Detalles de Orden"

    def __str__(self):
        return f"{self.cantidad}x {self.sector.nombre_sector} (Orden #{self.orden.id})"


class Entrada(models.Model):
    """
    Representa un ticket físico/digital individual emitido.
    Posee un código UUID único e irrepetible garantizado a nivel global.
    """
    class EstadoChoices(models.TextChoices):
        VALIDA = 'VÁLIDA', 'Válida'
        USADA = 'USADA', 'Usada'
        ANULADA = 'ANULADA', 'Anulada'

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Código UUID Único"
    )
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name='entradas',
        verbose_name="Orden de Compra"
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        related_name='entradas_emitidas',
        verbose_name="Sector Asignado"
    )
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.VALIDA,
        verbose_name="Estado de la Entrada"
    )

    class Meta:
        verbose_name = "Entrada / Ticket"
        verbose_name_plural = "Entradas / Tickets"
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"Ticket {self.uuid} - {self.sector.nombre_sector}"
    