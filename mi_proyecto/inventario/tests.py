from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Producto, Venta


class PruebasVistasInventario(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Teclado', codigo='TEC-001', precio=10000, stock=5
        )
        self.cliente = Cliente.objects.create(rut='11.111.111-1', nombre='Ana')

    def test_panel_principal_esta_disponible(self):
        response = self.client.get(reverse('inventario:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_venta_actualiza_stock_y_aplica_descuento_habitual(self):
        response = self.client.post(
            reverse('inventario:venta_create'),
            {
                'producto': self.producto.pk,
                'rut_cliente': self.cliente.rut,
                'cantidad': 2,
                'cliente_habitual': 'on',
            },
        )
        self.assertRedirects(response, reverse('inventario:venta_list'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertEqual(Venta.objects.get().total, 18000)

    def test_venta_no_puede_superar_stock(self):
        response = self.client.post(
            reverse('inventario:venta_create'),
            {
                'producto': self.producto.pk,
                'rut_cliente': self.cliente.rut,
                'cantidad': 6,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Venta.objects.exists())
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)
