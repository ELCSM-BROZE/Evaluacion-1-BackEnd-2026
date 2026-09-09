from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FormularioCliente, FormularioProducto, FormularioVenta
from .models import Cliente, Producto, Venta


def dashboard(request):
    context = {
        'productos_count': Producto.objects.count(),
        'clientes_count': Cliente.objects.count(),
        'ventas_count': Venta.objects.count(),
        'stock_bajo': Producto.objects.filter(stock__lt=5).order_by('stock', 'nombre')[:5],
        'ventas_recientes': Venta.objects.select_related('producto')[:5],
    }
    return render(request, 'inventario/dashboard.html', context)


def producto_list(request):
    productos = Producto.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        productos = productos.filter(nombre__icontains=query) | productos.filter(
            codigo__icontains=query
        )
    return render(request, 'inventario/producto_list.html', {'productos': productos, 'query': query})


def producto_create(request):
    form = FormularioProducto(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto creado correctamente.')
        return redirect('inventario:producto_list')
    return render(request, 'inventario/form.html', {'form': form, 'title': 'Nuevo producto', 'back_url': 'inventario:producto_list'})


def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = FormularioProducto(request.POST or None, instance=producto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('inventario:producto_list')
    return render(request, 'inventario/form.html', {'form': form, 'title': 'Editar producto', 'back_url': 'inventario:producto_list'})


def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('inventario:producto_list')
    return render(request, 'inventario/confirm_delete.html', {'object': producto, 'title': 'Eliminar producto', 'back_url': 'inventario:producto_list'})


def cliente_list(request):
    clientes = Cliente.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        clientes = clientes.filter(rut__icontains=query) | clientes.filter(nombre__icontains=query)
    return render(request, 'inventario/cliente_list.html', {'clientes': clientes, 'query': query})


def cliente_create(request):
    form = FormularioCliente(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente creado correctamente.')
        return redirect('inventario:cliente_list')
    return render(request, 'inventario/form.html', {'form': form, 'title': 'Nuevo cliente', 'back_url': 'inventario:cliente_list'})


def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = FormularioCliente(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente actualizado correctamente.')
        return redirect('inventario:cliente_list')
    return render(request, 'inventario/form.html', {'form': form, 'title': 'Editar cliente', 'back_url': 'inventario:cliente_list'})


def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
        return redirect('inventario:cliente_list')
    return render(request, 'inventario/confirm_delete.html', {'object': cliente, 'title': 'Eliminar cliente', 'back_url': 'inventario:cliente_list'})


def venta_list(request):
    ventas = Venta.objects.select_related('producto').all()
    return render(request, 'inventario/venta_list.html', {'ventas': ventas})


@transaction.atomic
def venta_create(request):
    form = FormularioVenta(request.POST or None)
    if form.is_valid():
        venta = form.save(commit=False)
        producto = Producto.objects.select_for_update().get(pk=venta.producto_id)
        if venta.cantidad > producto.stock:
            form.add_error('cantidad', f'El stock disponible es {producto.stock}.')
        else:
            cliente = Cliente.objects.filter(rut=venta.rut_cliente).first()
            venta.nombre_cliente = cliente.nombre if cliente else venta.rut_cliente
            subtotal = producto.precio * venta.cantidad
            venta.total = subtotal * 90 // 100 if venta.cliente_habitual else subtotal
            producto.stock -= venta.cantidad
            producto.save(update_fields=('stock',))
            venta.save()
            messages.success(request, 'Venta registrada y stock actualizado.')
            return redirect('inventario:venta_list')
    return render(request, 'inventario/form.html', {'form': form, 'title': 'Nueva venta', 'back_url': 'inventario:venta_list'})
