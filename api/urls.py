from django.urls import path
from .views import *

urlpatterns = [    
    path('v1/imgprincipal/<int:pk>', Image_APIView.as_view(), name='imgprincipal'),
    path('v1/imagenes/<int:pk>', Images_APIView.as_view(), name='imagenes'),
    path('v1/producto/<int:pk>', Producto_APIView.as_view(), name='producto'),
    path('v1/productosusuario/<int:pk>', ProductosUsuario_APIView.as_view(), name='productosusuario'),
    path('v1/productos', Productos_APIView.as_view(), name='productos'),
    path('v1/sucursales', Sucursal_APIView.as_view(), name='sucursales'),
    path('v1/categoriasprecio', CategoriaPrecio_APIView.as_view(), name='categoriasprecio'),
    path('v1/estado_producto', EstadoProducto_APIView.as_view(), name='estado_producto'),
    path('v1/estado_producto/<int:id>', EstadoProductoId_APIView.as_view(), name='estado_producto_id'),
    path('v1/promociones/', Promocion_APIView.as_view(), name='promociones'),
    path('v1/es_promocionado/<int:pk>', Promocion_Producto_APIView.as_view(), name='es_promocionado'),
    ]
