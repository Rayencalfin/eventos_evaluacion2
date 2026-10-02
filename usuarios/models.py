"""
==============================================================================
MÓDULO: USUARIOS - MODELOS DE DATOS
==============================================================================
Define el modelo de usuario personalizado extendiendo AbstractUser de Django.
Establece el correo electrónico (email) como identificador principal de autenticación
y asigna los roles oficiales (Espectador / Organizador).
==============================================================================
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Permite autenticación por email y diferencia entre Espectador u Organizador.
    """
    class RolChoices(models.TextChoices):
        ESPECTADOR = 'Espectador', 'Espectador'
        ORGANIZADOR = 'Organizador', 'Organizador'

    email = models.EmailField(
        unique=True,
        verbose_name="Correo Electrónico",
        help_text="Correo electrónico único para autenticación."
    )
    rol = models.CharField(
        max_length=20,
        choices=RolChoices.choices,
        default=RolChoices.ESPECTADOR,
        verbose_name="Rol de Usuario",
        help_text="Rol asignado para permisos del sistema."
    )

    # Configuración de autenticación por Email + Password
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.email} ({self.rol})"