"""
==============================================================================
MÓDULO: CARRITO DE COMPRAS - VISTAS WEB (PERSISTENCIA TOTAL EN BD)
==============================================================================
Garantiza la persistencia del carro en PostgreSQL asociado al usuario.
Soporta logout, cierre de navegador y reconexiones sin perder ítems.
==============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from eventos.models import Sector
from .models import Carro, ItemCarro


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
    """Agrega tickets al carrito guardando la información en la Base de Datos."""
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

        # 1. Obtener o crear el Carro persistente vinculado al Usuario en la BD
        carro_usuario, _ = Carro.objects.get_or_create(usuario=request.user)

        # 2. Verificar si el sector ya existe en el carro del usuario
        item_existente = ItemCarro.objects.filter(carro=carro_usuario, sector=sector).first()
        cantidad_actual = item_existente.cantidad if item_existente else 0
        nueva_cantidad = cantidad_actual + cantidad

        if nueva_cantidad > sector.stock_disponible:
            messages.error(
                request, 
                f"Ya tienes {cantidad_actual} entradas en tu carrito. "
                f"No puedes superar el stock disponible de {sector.stock_disponible}."
            )
            return redirect('eventos_web:detalle_evento', evento_id=sector.evento.id)

        # 3. Guardar o actualizar en la Base de Datos
        if item_existente:
            item_existente.cantidad = nueva_cantidad
            item_existente.save()
        else:
            ItemCarro.objects.create(
                carro=carro_usuario,
                sector=sector,
                cantidad=cantidad
            )

        messages.success(request, f"Se agregaron {cantidad} entrada(s) de '{sector.nombre_sector}' a tu carrito.")
        return redirect('carrito_web:ver_carro')

    return redirect('eventos_web:index')


@login_required
def ver_carro_web(request):
    """Renderiza el carrito trayendo los ítems activos desde PostgreSQL."""
    # Obtener o crear el carro en BD
    carro_usuario, _ = Carro.objects.get_or_create(usuario=request.user)
    
    # Consultar los items asociados con sus relaciones pre-cargadas
    db_items = ItemCarro.objects.filter(carro=carro_usuario).select_related('sector', 'sector__evento')

    # Mapear a una lista con llaves compatibles para la plantilla
    items = []
    total_compra = 0

    for item in db_items:
        subtotal = float(item.sector.precio) * item.cantidad
        total_compra += subtotal
        items.append({
            'id': item.id,
            'sector_id': item.sector.id,
            'nombre_sector': item.sector.nombre_sector,
            'evento_titulo': item.sector.evento.titulo,
            'evento_id': item.sector.evento.id,
            'precio': float(item.sector.precio),
            'cantidad': item.cantidad,
            'subtotal': subtotal
        })

    context = {
        'items_carro': items,
        'items': items,
        'total_compra': total_compra,
        'total': total_compra,
    }
    return render(request, 'carrito/carro.html', context)


@login_required
def eliminar_carro_web(request, sector_id):
    """Elimina un producto del carrito en la Base de Datos."""
    carro_usuario = Carro.objects.filter(usuario=request.user).first()

    if carro_usuario:
        # Permite eliminar buscando tanto por ID del sector como por ID del item
        ItemCarro.objects.filter(carro=carro_usuario, sector_id=sector_id).delete()
        messages.info(request, "Entrada removida del carrito.")

    return redirect('carrito_web:ver_carro')