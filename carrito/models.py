"""
==============================================================================
MÓDULO: CARRITO - MODELOS DE DATOS
==============================================================================
Garantiza la persistencia del carro de compras en PostgreSQL.
Relación 1 a 1 entre el Usuario y su Carro activo (sobrevive al logout).
==============================================================================
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from eventos.models import Sector


class Carro(models.Model):
    """
    Carro de compras persistente asociado de forma 1 a 1 con el Usuario.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carro',
        verbose_name="Usuario"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Carro de Compras"
        verbose_name_plural = "Carros de Compras"

    def __str__(self):
        return f"Carro de {self.usuario.email}"


class ItemCarro(models.Model):
    """
    Representa un producto/sector agregado dentro del carro de compras.
    """
    carro = models.ForeignKey(
        Carro,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Carro de Compras"
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name='items_carro',
        verbose_name="Sector Seleccionado"
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad Solicitada"
    )
    fecha_agregado = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Agregado")

    class Meta:
        verbose_name = "Item de Carro"
        verbose_name_plural = "Items de Carro"
        constraints = [
            models.UniqueConstraint(
                fields=['carro', 'sector'],
                name='unique_sector_en_carro'
            )
        ]

    def __str__(self):
        return f"{self.cantidad}x {self.sector.nombre_sector} (Carro: {self.carro.usuario.email})"