"""
==============================================================================
MÓDULO: EVENTOS - CONTROLADORES DEL PANEL DE ADMINISTRACIÓN
==============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .models import Evento, Sector, Artista, Recinto
from compras.models import Orden, DetalleOrden, Entrada

User = get_user_model()


@login_required
def admin_inicio(request):
    """Dashboard principal con métricas reales y últimas ventas desde la BD."""
    entradas_disponibles = Sector.objects.aggregate(total=Sum('stock_disponible'))['total'] or 0
    entradas_vendidas = Entrada.objects.count()
    ventas_totales = Orden.objects.filter(estado='PAGADA').aggregate(total=Sum('total'))['total'] or 0
    ordenes_pendientes = Orden.objects.filter(estado='PENDIENTE').count()

    ultimas_ventas = Orden.objects.select_related('usuario').prefetch_related(
        'detalles__sector', 'detalles__sector__evento'
    ).order_by('-fecha_orden')[:10]

    context = {
        'entradas_disponibles': entradas_disponibles,
        'entradas_vendidas': entradas_vendidas,
        'ventas_totales': ventas_totales,
        'ordenes_pendientes': ordenes_pendientes,
        'ultimas_ventas': ultimas_ventas,
    }
    return render(request, 'admin_panel/inicio.html', context)


@login_required
def admin_inventario(request):
    """Gestión de inventario de sectores y stock por concierto."""
    eventos = Evento.objects.prefetch_related('sectores').all()
    sectores = Sector.objects.select_related('evento').all()
    return render(request, 'admin_panel/inventario.html', {'eventos': eventos, 'sectores': sectores})


@login_required
def admin_crear_sector(request, evento_id):
    """Crea un nuevo sector asignado a un evento manejando los nombres exactos de los campos del modelo Sector."""
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        nombre_sector = request.POST.get('nombre_sector')
        precio = request.POST.get('precio')
        capacity = request.POST.get('capacidad', 100)
        stock = request.POST.get('stock', capacity)

        # Verificamos los campos reales del modelo Sector para evitar errores de argumentos
        campos_sector = [f.name for f in Sector._meta.get_fields()]
        
        datos_creacion = {
            'evento': evento,
            'nombre_sector': nombre_sector,
            'precio': precio,
        }

        # Asignar capacidad según el nombre del campo en tu modelo
        if 'capacidad' in campos_sector:
            datos_creacion['capacidad'] = capacity
        elif 'capacidad_total' in campos_sector:
            datos_creacion['capacidad_total'] = capacity
        elif 'stock_total' in campos_sector:
            datos_creacion['stock_total'] = capacity

        # Asignar stock disponible según el nombre del campo en tu modelo
        if 'stock_disponible' in campos_sector:
            datos_creacion['stock_disponible'] = stock
        elif 'stock' in campos_sector:
            datos_creacion['stock'] = stock

        Sector.objects.create(**datos_creacion)
        messages.success(request, f"¡Sector '{nombre_sector}' agregado exitosamente!")
        return redirect('eventos_web:admin_inventario')

    return render(request, 'admin_panel/sector_form.html', {'evento': evento})

@login_required
def admin_actualizar_stock(request, sector_id):
    """Actualiza el stock disponible de un sector."""
    sector = get_object_or_404(Sector, id=sector_id)
    if request.method == 'POST':
        nuevo_stock = request.POST.get('stock_disponible')
        try:
            sector.stock_disponible = int(nuevo_stock)
            sector.save()
            messages.success(request, f"Stock actualizado para {sector.nombre_sector}.")
        except (ValueError, TypeError):
            messages.error(request, "Valor de stock inválido.")
        return redirect('eventos_web:admin_inventario')

    return render(request, 'admin_panel/sector_stock_form.html', {'sector': sector})


@login_required
def admin_evento(request):
    """Pantalla principal de gestión de eventos."""
    eventos = Evento.objects.select_related('artista', 'recinto').all().order_by('-fecha_hora')
    artistas = Artista.objects.all()
    recintos = Recinto.objects.all()

    context = {
        'eventos': eventos,
        'artistas': artistas,
        'recintos': recintos,
    }
    return render(request, 'admin_panel/evento.html', context)


@login_required
def admin_crear_evento(request):
    """Procesa la creación de un nuevo evento aceptando URLs de imágenes completas."""
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        artista_id = request.POST.get('artista_id')
        recinto_id = request.POST.get('recinto_id')
        fecha_hora = request.POST.get('fecha_hora')
        descripcion = request.POST.get('descripcion', '').strip()
        banner = request.POST.get('banner', '').strip()  # Permite URL completa sin recorte
        estado = request.POST.get('estado', 'Activo')

        artista = get_object_or_404(Artista, id=artista_id)
        recinto = get_object_or_404(Recinto, id=recinto_id)

        Evento.objects.create(
            titulo=titulo,
            artista=artista,
            recinto=recinto,
            fecha_hora=fecha_hora,
            descripcion=descripcion,
            banner=banner,
            estado=estado
        )
        messages.success(request, f"¡Evento '{titulo}' creado exitosamente!")

    return redirect('eventos_web:admin_evento')


@login_required
def admin_editar_evento(request, evento_id):
    """Procesa la actualización de un evento manteniendo la URL completa de la imagen."""
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        evento.titulo = request.POST.get('titulo', evento.titulo)
        
        artista_id = request.POST.get('artista_id')
        if artista_id:
            evento.artista = get_object_or_404(Artista, id=artista_id)
            
        recinto_id = request.POST.get('recinto_id')
        if recinto_id:
            evento.recinto = get_object_or_404(Recinto, id=recinto_id)

        fecha_hora = request.POST.get('fecha_hora')
        if fecha_hora:
            evento.fecha_hora = fecha_hora

        evento.banner = request.POST.get('banner', '').strip() or evento.banner
        evento.descripcion = request.POST.get('descripcion', evento.descripcion)
        evento.estado = request.POST.get('estado', evento.estado)
        evento.save()
        messages.success(request, f"Evento '{evento.titulo}' actualizado correctamente.")

    return redirect('eventos_web:admin_evento')


@login_required
def admin_crear_artista(request):
    """Procesa la creación de un nuevo artista."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        genero = request.POST.get('genero', 'K-Pop')
        imagen_url = request.POST.get('imagen_url', '').strip()

        if nombre:
            artista, created = Artista.objects.get_or_create(
                nombre__iexact=nombre,
                defaults={
                    'nombre': nombre,
                    'genero': genero
                }
            )

            if created:
                campos_artista = [f.name for f in Artista._meta.get_fields()]
                if imagen_url:
                    if 'imagen' in campos_artista:
                        artista.imagen = imagen_url
                    elif 'banner' in campos_artista:
                        artista.banner = imagen_url
                    elif 'foto' in campos_artista:
                        artista.foto = imagen_url
                    artista.save()

                messages.success(request, f"¡Artista '{nombre}' registrado exitosamente!")
            else:
                messages.warning(request, f"El artista '{artista.nombre}' ya está registrado.")

    return redirect('eventos_web:admin_evento')


@login_required
def admin_ventas(request):
    """Lista las ventas y órdenes en el panel de administración."""
    ordenes = Orden.objects.select_related('usuario').prefetch_related(
        'detalles__sector', 'detalles__sector__evento'
    ).order_by('-fecha_orden')
    return render(request, 'admin_panel/ventas.html', {'ordenes': ordenes, 'ultimas_ventas': ordenes})


@login_required
def admin_clientes(request):
    """Lista los usuarios espectadores registrados desde la base de datos."""
    if hasattr(User, 'rol'):
        clientes = User.objects.filter(rol='Espectador')
    else:
        clientes = User.objects.filter(is_staff=False)
    
    return render(request, 'admin_panel/clientes.html', {'clientes': clientes, 'usuarios': clientes})


@login_required
def admin_entradas(request):
    """Lista de entradas emitidas registradas en BD."""
    entradas = Entrada.objects.select_related(
        'orden', 'orden__usuario', 'sector', 'sector__evento'
    ).order_by('-fecha_emision')
    return render(request, 'admin_panel/entradas.html', {'entradas': entradas})


@login_required
def admin_reportes(request):
    """Vista de reportes."""
    eventos = Evento.objects.all()
    ordenes = Orden.objects.filter(estado='PAGADA')
    return render(request, 'admin_panel/reportes.html', {'eventos': eventos, 'ordenes': ordenes})


@login_required
def admin_configuracion(request):
    """Configuración general del panel."""
    return render(request, 'admin_panel/configuracion.html')