from django import forms

from .models import Cliente, Producto, Venta


class FormularioProducto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ('nombre', 'codigo', 'precio', 'descripcion', 'stock')
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class FormularioCliente(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('rut', 'nombre')


class FormularioVenta(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ('producto', 'rut_cliente', 'cantidad', 'cliente_habitual')
        widgets = {
            'cantidad': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        producto = self.cleaned_data.get('producto')
        if producto and cantidad > producto.stock:
            raise forms.ValidationError(
                f'El stock disponible para este producto es {producto.stock}.'
            )
        return cantidad