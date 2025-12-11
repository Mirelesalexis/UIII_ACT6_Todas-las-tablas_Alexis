from django.urls import path
from . import views

urlpatterns = [
    # Página principal
    path('', views.inicio_elektra, name='inicio_elektra'),
    
    # Proveedores
    path('proveedores/', views.proveedores_ver, name='proveedores_ver'),
    path('proveedores/agregar/', views.proveedores_agregar, name='proveedores_agregar'),
    path('proveedores/actualizar/<int:pk>/', views.proveedores_actualizar, name='proveedores_actualizar'),
    path('proveedores/borrar/<int:pk>/', views.proveedores_borrar, name='proveedores_borrar'),
    
    # Categorías
    path('categorias/', views.categorias_ver, name='categorias_ver'),
    path('categorias/agregar/', views.categorias_agregar, name='categorias_agregar'),
    path('categorias/actualizar/<int:pk>/', views.categorias_actualizar, name='categorias_actualizar'),
    path('categorias/borrar/<int:pk>/', views.categorias_borrar, name='categorias_borrar'),
    
    # Productos
    path('productos/', views.productos_ver, name='productos_ver'),
    path('productos/agregar/', views.productos_agregar, name='productos_agregar'),
    path('productos/actualizar/<int:pk>/', views.productos_actualizar, name='productos_actualizar'),
    path('productos/borrar/<int:pk>/', views.productos_borrar, name='productos_borrar'),
    
    # Vendedores
    path('vendedores/', views.vendedores_ver, name='vendedores_ver'),
    path('vendedores/agregar/', views.vendedores_agregar, name='vendedores_agregar'),
    path('vendedores/actualizar/<int:pk>/', views.vendedores_actualizar, name='vendedores_actualizar'),
    path('vendedores/borrar/<int:pk>/', views.vendedores_borrar, name='vendedores_borrar'),
    
    # Clientes
    path('clientes/', views.clientes_ver, name='clientes_ver'),
    path('clientes/agregar/', views.clientes_agregar, name='clientes_agregar'),
    path('clientes/actualizar/<int:pk>/', views.clientes_actualizar, name='clientes_actualizar'),
    path('clientes/borrar/<int:pk>/', views.clientes_borrar, name='clientes_borrar'),
    
    # Ventas
    path('ventas/', views.ventas_ver, name='ventas_ver'),
    path('ventas/agregar/', views.ventas_agregar, name='ventas_agregar'),
    path('ventas/actualizar/<int:pk>/', views.ventas_actualizar, name='ventas_actualizar'),
    path('ventas/borrar/<int:pk>/', views.ventas_borrar, name='ventas_borrar'),
    
    # Reportes
    path('reportes/ventas/', views.reportes_ventas, name='reportes_ventas'),
]