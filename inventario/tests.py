import csv
import io

from django.contrib.admin.sites import AdminSite
from django.http import QueryDict
from django.test import RequestFactory, TestCase

from .admin import ProductoAdmin, StockRangeFilter, exportar_productos_csv
from .models import Producto


class StockRangeFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.out_of_stock = Producto.objects.create(nombre="Agotado", precio=100, stock=0)
        cls.low_stock = Producto.objects.create(nombre="Bajo", precio=100, stock=10)
        cls.medium_stock = Producto.objects.create(nombre="Medio", precio=100, stock=50)
        cls.high_stock = Producto.objects.create(nombre="Alto", precio=100, stock=51)

    def filtered_names(self, value):
        params = QueryDict(mutable=True)
        params["stock_range"] = value
        request = RequestFactory().get("/admin/inventario/producto/", params)
        filter_instance = StockRangeFilter(
            request,
            params,
            Producto,
            ProductoAdmin,
        )
        return set(filter_instance.queryset(request, Producto.objects.all()).values_list("nombre", flat=True))

    def test_filters_each_stock_range(self):
        self.assertEqual(self.filtered_names("out_of_stock"), {"Agotado"})
        self.assertEqual(self.filtered_names("low"), {"Bajo"})
        self.assertEqual(self.filtered_names("medium"), {"Medio"})
        self.assertEqual(self.filtered_names("high"), {"Alto"})


class ProductCsvExportTests(TestCase):
    def test_exports_selected_products(self):
        producto = Producto.objects.create(
            nombre="Café",
            descripcion="Grano tostado",
            precio=2500,
            stock=7,
            activo=True,
        )
        request = RequestFactory().get("/admin/inventario/producto/")
        response = exportar_productos_csv(
            ProductoAdmin(Producto, AdminSite()), request, Producto.objects.filter(pk=producto.pk)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="productos.csv"')

        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8"))))
        self.assertEqual(rows[0], ["Nombre", "Descripción", "Precio", "Stock", "Activo"])
        self.assertEqual(rows[1], ["Café", "Grano tostado", "2500", "7", "Sí"])
