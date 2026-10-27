from django.urls import path
from . import views

from .models import Producto
from rest_framework import routers, serializers, viewsets

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)

app_name = "inventario"

urlpatterns = [
    path("", views.lista_productos, name="lista_productos"),
    path("nuevo/", views.crear_producto, name="crear_producto"),
    path("<int:pk>/editar/", views.editar_producto, name="editar_producto"),
    path("<int:pk>/eliminar/", views.eliminar_producto, name="eliminar_producto"),
]
