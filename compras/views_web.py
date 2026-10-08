"""
==============================================================================
MÓDULO: COMPRAS Y CHECKOUT - VISTAS WEB
==============================================================================
Procesa el pago, descuenta stock de la base de datos y genera entradas UUID.
==============================================================================
"""

import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from compras.models import Orden, DetalleOrden, Entrada
from eventos.models import Sector
from carrito.models import Carro, ItemCarro


@login_required
def pagar_web(request):
    """Procesa el pago, descuenta stock en BD y emite los tickets con UUID válido."""
    if request.method == 'POST':
        # Obtener el carro persistente en BD del usuario
        carro_usuario = Carro.objects.filter(usuario=request.user).first()
        items_carro = list(ItemCarro.objects.filter(carro=carro_usuario).select_related('sector')) if carro_usuario else []

        if not items_carro:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('carrito_web:ver_carro')

        try:
            # Transacción atómica en PostgreSQL para evitar inconsistencias
            with transaction.atomic():
                total_orden = sum(item.cantidad * item.sector.precio for item in items_carro)

                # 1. Crear la Orden de Compra
                orden = Orden.objects.create(
                    usuario=request.user,
                    total=total_orden,
                    estado='PAGADA'
                )

                # Inspección dinámica de los campos del modelo Entrada
                campos_entrada = [field.name for field in Entrada._meta.get_fields()]

                # 2. Descontar stock y generar entradas
                for item in items_carro:
                    sector = Sector.objects.select_for_update().get(id=item.sector.id)
                    cantidad = item.cantidad

                    # Verificar stock disponible en la BD
                    if sector.stock_disponible < cantidad:
                        raise ValueError(f"Stock insuficiente para {sector.nombre_sector}. Solo quedan {sector.stock_disponible} entradas.")

                    # Descontar del stock real en PostgreSQL
                    sector.stock_disponible -= cantidad
                    sector.save()

                    # Registrar detalle de la orden con su precio histórico
                    DetalleOrden.objects.create(
                        orden=orden,
                        sector=sector,
                        cantidad=cantidad,
                        precio_unitario_historico=sector.precio
                    )

                    # Generar entradas con objeto UUID4 completo
                    for _ in range(cantidad):
                        codigo_uuid_obj = uuid.uuid4()
                        
                        kwargs_entrada = {
                            'orden': orden,
                            'sector': sector,
                        }

                        # Asignar el UUID completo según el nombre del campo que exista
                        if 'codigo_unico' in campos_entrada:
                            kwargs_entrada['codigo_unico'] = codigo_uuid_obj
                        elif 'codigo' in campos_entrada:
                            kwargs_entrada['codigo'] = codigo_uuid_obj
                        elif 'codigo_entrada' in campos_entrada:
                            kwargs_entrada['codigo_entrada'] = codigo_uuid_obj
                        elif 'uuid' in campos_entrada:
                            kwargs_entrada['uuid'] = codigo_uuid_obj
                        elif 'hash_entrada' in campos_entrada:
                            kwargs_entrada['hash_entrada'] = codigo_uuid_obj

                        Entrada.objects.create(**kwargs_entrada)

                # 3. Limpiar carrito de la Base de Datos tras la compra
                ItemCarro.objects.filter(carro=carro_usuario).delete()

                messages.success(request, f"¡Compra realizada con éxito! Orden #{orden.id} confirmada.")
                return redirect('compras_web:mis_entradas')

        except Exception as e:
            messages.error(request, f"Error al procesar la compra: {str(e)}")
            return redirect('carrito_web:ver_carro')

    return redirect('carrito_web:ver_carro')


@login_required
def mis_ordenes_web(request):
    """Historial de órdenes del cliente."""
    ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha_orden')
    return render(request, 'compras/mis_ordenes.html', {'ordenes': ordenes})


@login_required
def mis_entradas_web(request):
    """Entradas adquiridas por el cliente con sus códigos únicos UUID."""
    entradas = Entrada.objects.filter(orden__usuario=request.user).select_related('sector', 'sector__evento').order_by('-fecha_emision')
    return render(request, 'compras/mis_entradas.html', {'entradas': entradas})


@login_required
@transaction.atomic
def cancelar_orden_web(request, orden_id):
    """
    Cancela una orden y restablece el stock si estaba en estado PAGADA.
    """
    # Si es staff/admin puede cancelar cualquier orden, de lo contrario solo las suyas
    if request.user.is_staff or getattr(request.user, 'rol', '') == 'Organizador':
        orden = get_object_or_404(Orden, id=orden_id)
    else:
        orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)

    if orden.estado == 'CANCELADA':
        messages.warning(request, f"La orden #{orden.id} ya se encuentra cancelada.")
        return redirect('compras_web:mis_compras')

    # Restablecer el stock solo si la orden estaba PAGADA previamente
    if orden.estado == 'PAGADA':
        for detalle in orden.detalles.select_related('sector').all():
            sector = detalle.sector
            sector.stock_disponible += detalle.cantidad
            sector.save()

    # Actualizar estado a CANCELADA
    orden.estado = 'CANCELADA'
    orden.save()

    messages.success(request, f"La Orden #{orden.id} ha sido CANCELADA y se ha restablecido el stock de las entradas.")
    
    # Redireccionar según el rol
    if request.user.is_staff or getattr(request.user, 'rol', '') == 'Organizador':
        return redirect('eventos_web:admin_ventas')
    return redirect('compras_web:mis_compras')