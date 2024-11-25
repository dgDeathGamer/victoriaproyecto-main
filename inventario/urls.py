from django.urls import path
from .views import inventario_view, editar_producto, eliminar_producto, agregar_producto

urlpatterns = [
    path('', inventario_view, name='inventario'),
    path('agregar/', agregar_producto, name='agregar_producto'),  # URL para agregar un nuevo producto
    path('editar/<int:id>/', editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', eliminar_producto, name='eliminar_producto'),
]
