from django.urls import path
from promociones.views import *

urlpatterns = [    
    path('promocionar_producto/<int:idProducto>', promocionar_producto, name='promocionar_producto'),
    #path('pagar/', pagar_promocion, name='pagar'),
    path('detalles/<int:idPromocion>/', ver_detalles_promocion, name='detallePromocion'),
    path('checkout/', payment_view, name='checkout'),
    path('success/', success_view, name='success'),
    path('failure/', failure_view, name='failure'),
    path('pending/', pending_view, name='pending'),
    ]
