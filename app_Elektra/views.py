from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from .models import *

# ==================== FUNCIONES AUXILIARES ====================
def generar_folio_venta():
    """Genera un folio único para ventas"""
    import uuid
    return f"VENTA-{uuid.uuid4().hex[:8].upper()}"

# ==================== VISTAS GENERALES ====================
def inicio_elektra(request):
    """Página principal del sistema con estadísticas"""
    try:
        # Estadísticas para el dashboard
        total_ventas = Venta.objects.count()
        total_productos = Producto.objects.count()
        productos_bajo_stock = Producto.objects.filter(stock__lt=10).count()
        productos_sin_stock = Producto.objects.filter(stock=0).count()
        ventas_recientes = Venta.objects.select_related('producto', 'cliente').order_by('-fecha_venta')[:5]
        
        # Calcular total de ventas del mes actual
        mes_actual = timezone.now().month
        ventas_mes = Venta.objects.filter(fecha_venta__month=mes_actual)
        total_ventas_mes = ventas_mes.aggregate(Sum('total'))['total__sum'] or 0
        
        # Productos con stock bajo (para mostrar en alerta)
        productos_bajo_stock_lista = Producto.objects.filter(stock__lt=10, stock__gt=0)[:8]
        
        context = {
            'proveedores_count': Proveedor.objects.count(),
            'productos_count': total_productos,
            'productos_bajo_stock': productos_bajo_stock,
            'productos_sin_stock': productos_sin_stock,
            'ventas_count': total_ventas,
            'ventas_recientes': ventas_recientes,
            'clientes_count': Cliente.objects.count(),
            'vendedores_count': Vendedor.objects.count(),
            
            # Totales monetarios
            'total_ventas_mes': total_ventas_mes,
            
            # Listas para templates
            'productos_bajo_stock_lista': productos_bajo_stock_lista,
        }
        return render(request, 'inicio.html', context)
    except Exception as e:
        messages.error(request, f'Error al cargar estadísticas: {str(e)}')
        return render(request, 'inicio.html', {
            'proveedores_count': 0,
            'productos_count': 0,
            'productos_bajo_stock': 0,
            'productos_sin_stock': 0,
            'ventas_count': 0,
            'ventas_recientes': [],
            'clientes_count': 0,
            'vendedores_count': 0,
            'total_ventas_mes': 0,
            'productos_bajo_stock_lista': [],
        })

# ==================== PROVEEDORES ====================
def proveedores_ver(request):
    """Lista de proveedores con búsqueda y paginación"""
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    
    proveedores = Proveedor.objects.all()
    
    if query:
        proveedores = proveedores.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(pais__icontains=query)
        )
    
    if estado:
        if estado == 'activo':
            proveedores = proveedores.filter(activo=True)
        elif estado == 'inactivo':
            proveedores = proveedores.filter(activo=False)
    
    # Ordenar por nombre
    proveedores = proveedores.order_by('nombre')
    
    # Paginación
    paginator = Paginator(proveedores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'proveedores/ver.html', {
        'page_obj': page_obj,
        'query': query,
        'estado': estado,
        'total': proveedores.count()
    })

def proveedores_agregar(request):
    if request.method == 'POST':
        try:
            # Validar email único
            email = request.POST['email']
            if Proveedor.objects.filter(email=email).exists():
                messages.error(request, 'Este email ya está registrado')
                return redirect('proveedores_agregar')
            
            proveedor = Proveedor.objects.create(
                nombre=request.POST['nombre'],
                pais=request.POST['pais'],
                direccion=request.POST['direccion'],
                telefono=request.POST['telefono'],
                email=email,
                activo='activo' in request.POST
            )
            
            # Manejar logo si se subió
            if 'logo' in request.FILES:
                proveedor.logo = request.FILES['logo']
                proveedor.save()
            
            messages.success(request, 'Proveedor agregado exitosamente')
            return redirect('proveedores_ver')
        except Exception as e:
            messages.error(request, f'Error al agregar proveedor: {str(e)}')
            return redirect('proveedores_agregar')
    
    return render(request, 'proveedores/agregar.html')

def proveedores_actualizar(request, pk):
    proveedor = get_object_or_404(Proveedor, id=pk)
    
    if request.method == 'POST':
        try:
            email = request.POST['email']
            # Validar que el email no esté siendo usado por otro proveedor
            if Proveedor.objects.filter(email=email).exclude(id=pk).exists():
                messages.error(request, 'Este email ya está registrado por otro proveedor')
                return redirect('proveedores_actualizar', pk=pk)
            
            proveedor.nombre = request.POST['nombre']
            proveedor.pais = request.POST['pais']
            proveedor.direccion = request.POST['direccion']
            proveedor.telefono = request.POST['telefono']
            proveedor.email = email
            proveedor.activo = 'activo' in request.POST
            
            # Manejar logo si se subió
            if 'logo' in request.FILES:
                proveedor.logo = request.FILES['logo']
            
            proveedor.save()
            
            messages.success(request, 'Proveedor actualizado exitosamente')
            return redirect('proveedores_ver')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    
    return render(request, 'proveedores/actualizar.html', {'proveedor': proveedor})

def proveedores_borrar(request, pk):
    proveedor = get_object_or_404(Proveedor, id=pk)
    
    if request.method == 'POST':
        try:
            # Verificar si tiene productos asociados
            productos_count = proveedor.productos.count()
            if productos_count > 0:
                messages.error(request, 
                    f'No se puede eliminar el proveedor porque tiene {productos_count} producto(s) asociado(s)')
                return redirect('proveedores_ver')
            
            proveedor.delete()
            messages.success(request, 'Proveedor eliminado exitosamente')
            return redirect('proveedores_ver')
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
    
    return render(request, 'proveedores/borrar.html', {'proveedor': proveedor})

# ==================== CATEGORÍAS ====================
def categorias_ver(request):
    """Lista de categorías con búsqueda"""
    query = request.GET.get('q', '')
    
    categorias = Categoria.objects.all()
    
    if query:
        categorias = categorias.filter(nombre__icontains=query)
    
    categorias = categorias.order_by('nombre')
    
    # Paginación
    paginator = Paginator(categorias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'categorias/ver.html', {
        'page_obj': page_obj,
        'query': query,
        'total': categorias.count()
    })

def categorias_agregar(request):
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre'].strip()
            if not nombre:
                messages.error(request, 'El nombre es requerido')
                return redirect('categorias_agregar')
            
            categoria = Categoria.objects.create(
                nombre=nombre,
                color=request.POST.get('color', '#6c757d')
            )
            
            # Manejar icono si se subió
            if 'icono' in request.FILES:
                categoria.icono = request.FILES['icono']
                categoria.save()
            
            messages.success(request, 'Categoría agregada exitosamente')
            return redirect('categorias_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'categorias/agregar.html')

def categorias_actualizar(request, pk):
    categoria = get_object_or_404(Categoria, id=pk)
    
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre'].strip()
            if not nombre:
                messages.error(request, 'El nombre es requerido')
                return redirect('categorias_actualizar', pk=pk)
            
            categoria.nombre = nombre
            categoria.color = request.POST.get('color', '#6c757d')
            
            # Manejar icono si se subió
            if 'icono' in request.FILES:
                categoria.icono = request.FILES['icono']
            
            categoria.save()
            messages.success(request, 'Categoría actualizada exitosamente')
            return redirect('categorias_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'categorias/actualizar.html', {'categoria': categoria})

def categorias_borrar(request, pk):
    categoria = get_object_or_404(Categoria, id=pk)
    
    if request.method == 'POST':
        try:
            # Verificar si tiene productos asociados
            productos_count = categoria.productos.count()
            if productos_count > 0:
                messages.error(request, 
                    f'No se puede eliminar la categoría porque tiene {productos_count} producto(s) asociado(s)')
                return redirect('categorias_ver')
            
            categoria.delete()
            messages.success(request, 'Categoría eliminada exitosamente')
            return redirect('categorias_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'categorias/borrar.html', {'categoria': categoria})

# ==================== PRODUCTOS ====================
def productos_ver(request):
    """Lista de productos con búsqueda avanzada"""
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    stock_filter = request.GET.get('stock', '')
    
    productos = Producto.objects.select_related('categoria', 'proveedor').all()
    
    if query:
        productos = productos.filter(
            Q(nombre_producto__icontains=query) |
            Q(sku__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if stock_filter:
        if stock_filter == 'bajo':
            productos = productos.filter(stock__lt=10)
        elif stock_filter == 'sin':
            productos = productos.filter(stock=0)
        elif stock_filter == 'suficiente':
            productos = productos.filter(stock__gte=10)
    
    # Ordenar
    productos = productos.order_by('nombre_producto')
    
    # Estadísticas
    total_productos = productos.count()
    productos_suficiente = productos.filter(stock__gte=10).count()
    productos_bajo = productos.filter(stock__lt=10, stock__gt=0).count()
    productos_sin = productos.filter(stock=0).count()
    
    # Paginación
    paginator = Paginator(productos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categorias = Categoria.objects.all()
    
    return render(request, 'productos/ver.html', {
        'page_obj': page_obj,
        'categorias': categorias,
        'query': query,
        'categoria_id': int(categoria_id) if categoria_id and categoria_id.isdigit() else '',
        'stock_filter': stock_filter,
        'total': total_productos,
        'productos_suficiente': productos_suficiente,
        'productos_bajo': productos_bajo,
        'productos_sin': productos_sin,
    })

def productos_agregar(request):
    if request.method == 'POST':
        try:
            # Validar SKU único
            sku = request.POST['sku']
            if Producto.objects.filter(sku=sku).exists():
                messages.error(request, 'Este SKU ya está registrado')
                return redirect('productos_agregar')
            
            categoria = get_object_or_404(Categoria, id=request.POST['categoria'])
            proveedor = get_object_or_404(Proveedor, id=request.POST['proveedor'])
            
            # Validar stock y precio
            stock = int(request.POST['stock'])
            precio = float(request.POST['precio'])
            
            if stock < 0:
                messages.error(request, 'El stock no puede ser negativo')
                return redirect('productos_agregar')
            
            if precio <= 0:
                messages.error(request, 'El precio debe ser mayor a 0')
                return redirect('productos_agregar')
            
            # Crear producto
            producto = Producto.objects.create(
                nombre_producto=request.POST['nombre_producto'],
                categoria=categoria,
                precio=precio,
                stock=stock,
                descripcion=request.POST['descripcion'],
                proveedor=proveedor,
                sku=sku
            )
            
            # Manejar imagen si se subió
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']
                producto.save()
            
            messages.success(request, 'Producto agregado exitosamente')
            return redirect('productos_ver')
        except ValueError:
            messages.error(request, 'Datos numéricos inválidos')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.filter(activo=True)
    return render(request, 'productos/agregar.html', {
        'categorias': categorias,
        'proveedores': proveedores
    })

def productos_actualizar(request, pk):
    producto = get_object_or_404(Producto, id=pk)
    
    if request.method == 'POST':
        try:
            sku = request.POST['sku']
            # Validar que el SKU no esté siendo usado por otro producto
            if Producto.objects.filter(sku=sku).exclude(id=pk).exists():
                messages.error(request, 'Este SKU ya está registrado por otro producto')
                return redirect('productos_actualizar', pk=pk)
            
            categoria = get_object_or_404(Categoria, id=request.POST['categoria'])
            proveedor = get_object_or_404(Proveedor, id=request.POST['proveedor'])
            
            # Validar stock y precio
            stock = int(request.POST['stock'])
            precio = float(request.POST['precio'])
            
            if stock < 0:
                messages.error(request, 'El stock no puede ser negativo')
                return redirect('productos_actualizar', pk=pk)
            
            if precio <= 0:
                messages.error(request, 'El precio debe ser mayor a 0')
                return redirect('productos_actualizar', pk=pk)
            
            producto.nombre_producto = request.POST['nombre_producto']
            producto.categoria = categoria
            producto.precio = precio
            producto.stock = stock
            producto.descripcion = request.POST['descripcion']
            producto.proveedor = proveedor
            producto.sku = sku
            
            # Manejar imagen si se subió una nueva
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']
            
            producto.save()
            
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('productos_ver')
        except ValueError:
            messages.error(request, 'Datos numéricos inválidos')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.filter(activo=True)
    return render(request, 'productos/actualizar.html', {
        'producto': producto,
        'categorias': categorias,
        'proveedores': proveedores
    })

def productos_borrar(request, pk):
    producto = get_object_or_404(Producto, id=pk)
    
    if request.method == 'POST':
        try:
            # Verificar si tiene ventas asociadas
            ventas_count = Venta.objects.filter(producto=producto).count()
            if ventas_count > 0:
                messages.error(request, 
                    f'No se puede eliminar el producto porque tiene {ventas_count} venta(s) asociada(s)')
                return redirect('productos_ver')
            
            producto.delete()
            messages.success(request, 'Producto eliminado exitosamente')
            return redirect('productos_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'productos/borrar.html', {'producto': producto})

# ==================== VENDEDORES ====================
def vendedores_ver(request):
    """Lista de vendedores con búsqueda"""
    query = request.GET.get('q', '')
    
    vendedores = Vendedor.objects.all()
    
    if query:
        vendedores = vendedores.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(telefono__icontains=query)
        )
    
    vendedores = vendedores.order_by('nombre')
    
    # Paginación
    paginator = Paginator(vendedores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'vendedores/ver.html', {
        'page_obj': page_obj,
        'query': query,
        'total': vendedores.count()
    })

def vendedores_agregar(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            # Validar email único
            if Vendedor.objects.filter(email=email).exists():
                messages.error(request, 'Este email ya está registrado')
                return redirect('vendedores_agregar')
            
            vendedor = Vendedor.objects.create(
                nombre=request.POST['nombre'],
                telefono=request.POST['telefono'],
                email=email,
                fecha_contratacion=request.POST.get('fecha_contratacion', timezone.now().date()),
                activo='activo' in request.POST
            )
            
            # Manejar foto si se subió
            if 'foto' in request.FILES:
                vendedor.foto = request.FILES['foto']
                vendedor.save()
            
            messages.success(request, 'Vendedor agregado exitosamente')
            return redirect('vendedores_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'vendedores/agregar.html')

def vendedores_actualizar(request, pk):
    vendedor = get_object_or_404(Vendedor, id=pk)
    
    if request.method == 'POST':
        try:
            email = request.POST['email']
            # Validar que el email no esté siendo usado por otro vendedor
            if Vendedor.objects.filter(email=email).exclude(id=pk).exists():
                messages.error(request, 'Este email ya está registrado por otro vendedor')
                return redirect('vendedores_actualizar', pk=pk)
            
            vendedor.nombre = request.POST['nombre']
            vendedor.telefono = request.POST['telefono']
            vendedor.email = email
            vendedor.fecha_contratacion = request.POST.get('fecha_contratacion', vendedor.fecha_contratacion)
            vendedor.activo = 'activo' in request.POST
            
            # Manejar foto si se subió
            if 'foto' in request.FILES:
                vendedor.foto = request.FILES['foto']
            
            vendedor.save()
            
            messages.success(request, 'Vendedor actualizado exitosamente')
            return redirect('vendedores_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'vendedores/actualizar.html', {'vendedor': vendedor})

def vendedores_borrar(request, pk):
    vendedor = get_object_or_404(Vendedor, id=pk)
    
    if request.method == 'POST':
        try:
            # Verificar si tiene ventas asociadas
            ventas_count = Venta.objects.filter(vendedor=vendedor).count()
            if ventas_count > 0:
                messages.error(request, 
                    f'No se puede eliminar el vendedor porque tiene {ventas_count} venta(s) asociada(s)')
                return redirect('vendedores_ver')
            
            vendedor.delete()
            messages.success(request, 'Vendedor eliminado exitosamente')
            return redirect('vendedores_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'vendedores/borrar.html', {'vendedor': vendedor})

# ==================== CLIENTES ====================
def clientes_ver(request):
    """Lista de clientes con búsqueda"""
    query = request.GET.get('q', '')
    
    clientes = Cliente.objects.all()
    
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(telefono__icontains=query)
        )
    
    clientes = clientes.order_by('nombre')
    
    # Paginación
    paginator = Paginator(clientes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'clientes/ver.html', {
        'page_obj': page_obj,
        'query': query,
        'total': clientes.count()
    })

def clientes_agregar(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            # Validar email único
            if Cliente.objects.filter(email=email).exists():
                messages.error(request, 'Este email ya está registrado')
                return redirect('clientes_agregar')
            
            cliente = Cliente.objects.create(
                nombre=request.POST['nombre'],
                telefono=request.POST['telefono'],
                email=email,
                direccion=request.POST['direccion'],
                tipo_cliente=request.POST.get('tipo_cliente', 'regular')
            )
            
            # Manejar foto si se subió
            if 'foto' in request.FILES:
                cliente.foto = request.FILES['foto']
                cliente.save()
            
            messages.success(request, 'Cliente agregado exitosamente')
            return redirect('clientes_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'clientes/agregar.html')

def clientes_actualizar(request, pk):
    cliente = get_object_or_404(Cliente, id=pk)
    
    if request.method == 'POST':
        try:
            email = request.POST['email']
            # Validar que el email no esté siendo usado por otro cliente
            if Cliente.objects.filter(email=email).exclude(id=pk).exists():
                messages.error(request, 'Este email ya está registrado por otro cliente')
                return redirect('clientes_actualizar', pk=pk)
            
            cliente.nombre = request.POST['nombre']
            cliente.telefono = request.POST['telefono']
            cliente.email = email
            cliente.direccion = request.POST['direccion']
            cliente.tipo_cliente = request.POST.get('tipo_cliente', 'regular')
            
            # Manejar foto si se subió
            if 'foto' in request.FILES:
                cliente.foto = request.FILES['foto']
            
            cliente.save()
            
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('clientes_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'clientes/actualizar.html', {'cliente': cliente})

def clientes_borrar(request, pk):
    cliente = get_object_or_404(Cliente, id=pk)
    
    if request.method == 'POST':
        try:
            # Verificar si tiene ventas asociadas
            ventas_count = Venta.objects.filter(cliente=cliente).count()
            if ventas_count > 0:
                messages.error(request, 
                    f'No se puede eliminar el cliente porque tiene {ventas_count} venta(s) asociada(s)')
                return redirect('clientes_ver')
            
            cliente.delete()
            messages.success(request, 'Cliente eliminado exitosamente')
            return redirect('clientes_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'clientes/borrar.html', {'cliente': cliente})

# ==================== VENTAS ====================
def ventas_ver(request):
    """Lista de ventas con filtros avanzados"""
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    ventas = Venta.objects.select_related('vendedor', 'producto', 'cliente').all()
    
    if query:
        ventas = ventas.filter(
            Q(folio__icontains=query) |
            Q(producto__nombre_producto__icontains=query) |
            Q(cliente__nombre__icontains=query) |
            Q(vendedor__nombre__icontains=query)
        )
    
    if estado:
        ventas = ventas.filter(estado=estado)
    
    if fecha_inicio:
        ventas = ventas.filter(fecha_venta__date__gte=fecha_inicio)
    
    if fecha_fin:
        ventas = ventas.filter(fecha_venta__date__lte=fecha_fin)
    
    # Ordenar por fecha más reciente
    ventas = ventas.order_by('-fecha_venta')
    
    # Calcular totales
    total_ventas = sum(v.total for v in ventas)
    
    # Paginación
    paginator = Paginator(ventas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'ventas/ver.html', {
        'page_obj': page_obj,
        'query': query,
        'estado': estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_ventas': total_ventas,
        'total_count': ventas.count()
    })

def ventas_agregar(request):
    if request.method == 'POST':
        try:
            folio = generar_folio_venta()
            vendedor = get_object_or_404(Vendedor, id=request.POST['vendedor'])
            producto = get_object_or_404(Producto, id=request.POST['producto'])
            cliente = get_object_or_404(Cliente, id=request.POST['cliente'])
            
            # Validar cantidad
            cantidad = int(request.POST.get('cantidad', 1))
            if cantidad <= 0:
                messages.error(request, 'La cantidad debe ser mayor a 0')
                return redirect('ventas_agregar')
            
            # Validar stock disponible
            if producto.stock < cantidad:
                messages.error(request, f'Stock insuficiente. Disponible: {producto.stock}')
                return redirect('ventas_agregar')
            
            # Calcular total
            total = float(producto.precio) * cantidad
            
            # Crear venta
            venta = Venta.objects.create(
                folio=folio,
                total=total,
                metodo_pago=request.POST['metodo_pago'],
                estado='completada',
                vendedor=vendedor,
                producto=producto,
                cliente=cliente,
                notas=request.POST.get('notas', '')
            )
            
            # Actualizar stock del producto
            producto.stock -= cantidad
            producto.save()
            
            messages.success(request, f'Venta registrada exitosamente. Folio: {folio}')
            return redirect('ventas_ver')
        except ValueError:
            messages.error(request, 'Datos numéricos inválidos')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    vendedores = Vendedor.objects.all()
    productos = Producto.objects.filter(stock__gt=0)
    clientes = Cliente.objects.all()
    
    return render(request, 'ventas/agregar.html', {
        'vendedores': vendedores,
        'productos': productos,
        'clientes': clientes,
        'folio': generar_folio_venta()
    })

def ventas_actualizar(request, pk):
    venta = get_object_or_404(Venta, id=pk)
    
    if request.method == 'POST':
        try:
            # Restaurar stock anterior si cambia el producto
            producto_anterior = venta.producto
            cantidad_anterior = venta.total / venta.producto.precio if venta.producto.precio > 0 else 0
            
            producto_nuevo = get_object_or_404(Producto, id=request.POST['producto'])
            cantidad_nueva = int(request.POST.get('cantidad', 1))
            
            # Si cambió el producto, restaurar stock del anterior
            if producto_anterior.id != producto_nuevo.id:
                producto_anterior.stock += int(cantidad_anterior)
                producto_anterior.save()
            
            # Validar stock del nuevo producto
            if producto_nuevo.stock < cantidad_nueva:
                messages.error(request, f'Stock insuficiente. Disponible: {producto_nuevo.stock}')
                return redirect('ventas_actualizar', pk=pk)
            
            # Actualizar venta
            venta.folio = request.POST['folio']
            venta.total = float(producto_nuevo.precio) * cantidad_nueva
            venta.metodo_pago = request.POST['metodo_pago']
            venta.estado = request.POST['estado']
            venta.vendedor = get_object_or_404(Vendedor, id=request.POST['vendedor'])
            venta.producto = producto_nuevo
            venta.cliente = get_object_or_404(Cliente, id=request.POST['cliente'])
            venta.notas = request.POST.get('notas', '')
            venta.save()
            
            # Actualizar stock del nuevo producto
            producto_nuevo.stock -= cantidad_nueva
            producto_nuevo.save()
            
            messages.success(request, 'Venta actualizada exitosamente')
            return redirect('ventas_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    vendedores = Vendedor.objects.all()
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    
    return render(request, 'ventas/actualizar.html', {
        'venta': venta,
        'vendedores': vendedores,
        'productos': productos,
        'clientes': clientes
    })

def ventas_borrar(request, pk):
    venta = get_object_or_404(Venta, id=pk)
    
    if request.method == 'POST':
        try:
            # Restaurar stock del producto
            producto = venta.producto
            cantidad = venta.total / producto.precio if producto.precio > 0 else 0
            producto.stock += int(cantidad)
            producto.save()
            
            venta.delete()
            messages.success(request, 'Venta eliminada exitosamente')
            return redirect('ventas_ver')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'ventas/borrar.html', {'venta': venta})

# ==================== REPORTES ====================
def reportes_ventas(request):
    """Reporte de ventas por fecha"""
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    ventas = Venta.objects.select_related('producto', 'cliente', 'vendedor').all()
    
    if fecha_inicio:
        ventas = ventas.filter(fecha_venta__date__gte=fecha_inicio)
    
    if fecha_fin:
        ventas = ventas.filter(fecha_venta__date__lte=fecha_fin)
    
    ventas = ventas.order_by('-fecha_venta')
    
    # Calcular estadísticas
    total_ventas = sum(v.total for v in ventas)
    promedio_venta = total_ventas / len(ventas) if ventas else 0
    
    return render(request, 'reportes/ventas.html', {
        'ventas': ventas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_ventas': total_ventas,
        'total_count': ventas.count(),
        'promedio_venta': promedio_venta
    })