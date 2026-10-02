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


@login_required
def pagar_web(request):
    """Procesa el pago, descuenta stock en BD y emite los tickets con UUID válido."""
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})

        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('carrito_web:ver_carro')

        try:
            # Transacción atómica en PostgreSQL para evitar inconsistencias
            with transaction.atomic():
                total_orden = sum(item['subtotal'] for item in carrito.values())

                # 1. Crear la Orden de Compra
                orden = Orden.objects.create(
                    usuario=request.user,
                    total=total_orden,
                    estado='PAGADA'
                )

                # Inspección dinámica de los campos del modelo Entrada
                campos_entrada = [field.name for field in Entrada._meta.get_fields()]

                # 2. Descontar stock y generar entradas
                for sector_id_str, item in carrito.items():
                    sector = Sector.objects.select_for_update().get(id=item['sector_id'])
                    cantidad = item['cantidad']

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
                        precio_unitario_historico=item['precio']
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

                # 3. Limpiar carrito de la sesión tras la compra
                request.session['carrito'] = {}
                request.session.modified = True

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