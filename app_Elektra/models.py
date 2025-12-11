from django.db import models
from django.utils import timezone

# =====================================================
# TABLA: PROVEEDORES
# =====================================================
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    fecha_registro = models.DateField(default=timezone.now)
    activo = models.BooleanField(default=True)
    
    # Imagen/Logo del proveedor
    logo = models.ImageField(
        upload_to='proveedores/',
        null=True,
        blank=True,
        default='proveedores/default_proveedor.png',
        verbose_name='Logo del proveedor'
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'


# =====================================================
# TABLA EXTRA: CATEGORÍAS (relación con Productos)
# =====================================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    # Icono/Imagen de la categoría
    icono = models.ImageField(
        upload_to='categorias/',
        null=True,
        blank=True,
        default='categorias/default_categoria.png',
        verbose_name='Icono de la categoría'
    )
    
    # Color para la categoría
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text='Color en formato HEX (#RRGGBB)'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


# =====================================================
# TABLA: PRODUCTOS
# =====================================================
class Producto(models.Model):
    nombre_producto = models.CharField(max_length=120)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    descripcion = models.TextField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="productos")
    sku = models.CharField(max_length=50, unique=True)
    
    # Imagen del producto
    imagen = models.ImageField(
        upload_to='productos/',
        null=True,
        blank=True,
        default='productos/default_producto.png',
        verbose_name='Imagen del producto'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_producto
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


# =====================================================
# TABLA EXTRA: VENDEDORES
# =====================================================
class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    
    # Foto del vendedor
    foto = models.ImageField(
        upload_to='vendedores/',
        null=True,
        blank=True,
        default='vendedores/default_vendedor.png',
        verbose_name='Foto del vendedor'
    )
    
    # Información adicional
    fecha_contratacion = models.DateField(default=timezone.now)
    activo = models.BooleanField(default=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'


# =====================================================
# TABLA EXTRA: CLIENTES
# =====================================================
class Cliente(models.Model):
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    direccion = models.TextField()
    
    # Foto del cliente
    foto = models.ImageField(
        upload_to='clientes/',
        null=True,
        blank=True,
        default='clientes/default_cliente.png',
        verbose_name='Foto del cliente'
    )
    
    # Información adicional
    tipo_cliente = models.CharField(
        max_length=20,
        choices=[
            ('regular', 'Cliente Regular'),
            ('premium', 'Cliente Premium'),
            ('corporativo', 'Cliente Corporativo'),
        ],
        default='regular'
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'


# =====================================================
# TABLA: VENTAS
# =====================================================
class Venta(models.Model):
    folio = models.CharField(max_length=50, unique=True)
    fecha_venta = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)

    vendedor = models.ForeignKey(Vendedor, on_delete=models.SET_NULL, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    
    # Notas adicionales
    notas = models.TextField(blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Venta {self.folio}"
    
    class Meta:
        ordering = ['-fecha_venta']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'