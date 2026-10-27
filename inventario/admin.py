import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Producto

# Register your models here.


class StockRangeFilter(admin.SimpleListFilter):
    """Filter products by practical stock ranges in the admin list."""

    title = "rango de stock"
    parameter_name = "stock_range"

    def lookups(self, request, model_admin):
        return (
            ("out_of_stock", "Sin stock (0)"),
            ("low", "Stock bajo (1-10)"),
            ("medium", "Stock medio (11-50)"),
            ("high", "Stock alto (51 o más)"),
        )

    def queryset(self, request, queryset):
        filters = {
            "out_of_stock": {"stock": 0},
            "low": {"stock__range": (1, 10)},
            "medium": {"stock__range": (11, 50)},
            "high": {"stock__gte": 51},
        }

        selected_filter = filters.get(self.value())
        return queryset.filter(**selected_filter) if selected_filter else queryset


@admin.action(description="Exportar productos seleccionados a CSV")
def exportar_productos_csv(modeladmin, request, queryset):
    """Return the selected products as a UTF-8 CSV download."""

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="productos.csv"'

    writer = csv.writer(response)
    writer.writerow(("Nombre", "Descripción", "Precio", "Stock", "Activo"))

    for producto in queryset.iterator():
        writer.writerow(
            (
                producto.nombre,
                producto.descripcion,
                producto.precio,
                producto.stock,
                "Sí" if producto.activo else "No",
            )
        )

    return response


class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock", "activo")
    search_fields = ("nombre",)
    list_filter = ("activo", StockRangeFilter)
    actions = (exportar_productos_csv,)
    ordering = ("nombre", "stock")

admin.site.register(model_or_iterable=Producto, admin_class=ProductoAdmin)
