from django.contrib import admin

from .models import Cliente, Producto, Venta


@admin.register(Producto)
class AdministradorProducto(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'precio', 'stock')
    search_fields = ('codigo', 'nombre')


@admin.register(Cliente)
class AdministradorCliente(admin.ModelAdmin):
    list_display = ('rut', 'nombre')
    search_fields = ('rut', 'nombre')


@admin.register(Venta)
class AdministradorVenta(admin.ModelAdmin):
    list_display = ('id', 'producto', 'rut_cliente', 'cantidad', 'total', 'fecha')
    list_filter = ('cliente_habitual', 'fecha')
    search_fields = ('rut_cliente', 'nombre_cliente', 'producto__nombre')
