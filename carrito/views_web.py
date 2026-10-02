"""
==============================================================================
MÓDULO: CARRITO DE COMPRAS - VISTAS WEB
==============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from eventos.models import Sector


def espectador_required(view_func):
    """Decorador RBAC para espectadores autenticados."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios_web:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
def agregar_carro_web(request, sector_id):
    """Agrega tickets al carrito guardando la información en la sesión."""
    if request.method == 'POST':
        sector = get_object_or_404(Sector.objects.select_related('evento'), id=sector_id)
        
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (ValueError, TypeError):
            cantidad = 1

        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser mayor a cero.")
            return redirect('eventos_web:detalle_evento', evento_id=sector.evento.id)

        # Validar stock disponible en BD
        if cantidad > sector.stock_disponible:
            messages.error(request, f"No hay suficiente stock. Quedan {sector.stock_disponible} entradas.")
            return redirect('eventos_web:detalle_evento', evento_id=sector.evento.id)

        # Obtener o inicializar el carrito en la sesión
        carrito = request.session.get('carrito', {})
        sector_key = str(sector.id)

        cantidad_actual = carrito.get(sector_key, {}).get('cantidad', 0)
        nueva_cantidad = cantidad_actual + cantidad

        if nueva_cantidad > sector.stock_disponible:
            messages.error(
                request, 
                f"Ya tienes {cantidad_actual} entradas en tu carrito. "
                f"No puedes superar el stock disponible de {sector.stock_disponible}."
            )
            return redirect('eventos_web:detalle_evento', evento_id=sector.evento.id)

        # Guardar ítem detallado
        carrito[sector_key] = {
            'sector_id': sector.id,
            'nombre_sector': sector.nombre_sector,
            'evento_titulo': sector.evento.titulo,
            'evento_id': sector.evento.id,
            'precio': float(sector.precio),
            'cantidad': nueva_cantidad,
            'subtotal': float(sector.precio) * nueva_cantidad
        }

        request.session['carrito'] = carrito
        request.session.modified = True

        messages.success(request, f"Se agregaron {cantidad} entrada(s) de '{sector.nombre_sector}' a tu carrito.")
        return redirect('carrito_web:ver_carro')

    return redirect('eventos_web:index')


@login_required
def ver_carro_web(request):
    """Renderiza el carrito con los ítems activos en la sesión."""
    carrito = request.session.get('carrito', {})
    items = list(carrito.values())
    total_compra = sum(item['subtotal'] for item in items)

    context = {
        'items_carro': items,
        'items': items,
        'total_compra': total_compra,
        'total': total_compra,
    }
    return render(request, 'carrito/carro.html', context)


@login_required
def eliminar_carro_web(request, sector_id):
    """Elimina un producto del carrito."""
    carrito = request.session.get('carrito', {})
    sector_key = str(sector_id)

    if sector_key in carrito:
        del carrito[sector_key]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.info(request, "Entrada removida del carrito.")

    return redirect('carrito_web:ver_carro')