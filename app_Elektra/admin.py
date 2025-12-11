from django.contrib import admin
from django.utils.html import format_html
from .models import *

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'categoria', 'precio', 'stock', 'mostrar_imagen', 'proveedor')
    list_filter = ('categoria', 'proveedor')
    search_fields = ('nombre_producto', 'sku', 'descripcion')
    
    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen.url)
        return "Sin imagen"
    mostrar_imagen.short_description = 'Imagen'

# Registrar modelos con configuraciones personalizadas
admin.site.register(Proveedor)
admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Vendedor)
admin.site.register(Cliente)
admin.site.register(Venta)