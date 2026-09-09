from django.db import models

# Create your models here.

class Producto(models.Model):
    nombre = models.CharField(max_length=64)
    codigo = models.CharField(max_length=20, unique=True)
    precio = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Cliente(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.nombre} ({self.rut})'


class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    rut_cliente = models.CharField(max_length=12)
    nombre_cliente = models.CharField(max_length=100, blank=True)
    cliente_habitual = models.BooleanField(default=False)
    cantidad = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Venta #{self.pk} - {self.producto.nombre}'

    def save(self, *args, **kwargs):
        if self.producto_id and not self.nombre_cliente:
            self.nombre_cliente = self.rut_cliente
        super().save(*args, **kwargs)
