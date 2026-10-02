from django.urls import path
from eventos import views_web, views_admin

app_name = 'eventos_web'

urlpatterns = [
    # Rutas web públicas del catálogo
    path('', views_web.index_web, name='index'),
    path('evento/<int:evento_id>/', views_web.detalle_evento_web, name='detalle_evento'),

    # RUTAS DEL PANEL DE ADMINISTRACIÓN SIMPLIFICADO
    path('admin-panel/', views_admin.admin_inicio, name='admin_inicio'),
    path('admin-panel/inventario/', views_admin.admin_inventario, name='admin_inventario'),
    path('admin-panel/inventario/sector/crear/<int:evento_id>/', views_admin.admin_crear_sector, name='admin_crear_sector'),
    path('admin-panel/inventario/stock/<int:sector_id>/', views_admin.admin_actualizar_stock, name='admin_actualizar_stock'),

    path('admin-panel/evento/', views_admin.admin_evento, name='admin_evento'),
    path('admin-panel/evento/crear/', views_admin.admin_crear_evento, name='admin_crear_evento'),
    path('admin-panel/evento/editar/<int:evento_id>/', views_admin.admin_editar_evento, name='admin_editar_evento'),

    path('admin-panel/artista/crear/', views_admin.admin_crear_artista, name='admin_crear_artista'),

    path('admin-panel/ventas/', views_admin.admin_ventas, name='admin_ventas'),
    path('admin-panel/clientes/', views_admin.admin_clientes, name='admin_clientes'),
    path('admin-panel/entradas/', views_admin.admin_entradas, name='admin_entradas'),
    path('admin-panel/reportes/', views_admin.admin_reportes, name='admin_reportes'),
    path('admin-panel/configuracion/', views_admin.admin_configuracion, name='admin_configuracion'),
]