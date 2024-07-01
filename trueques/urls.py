from django.urls import path
from trueques.views import *

urlpatterns = [    
    path('iniciar/<int:id>', seleccionarProductoTrueque, name='iniciar'),
    path('iniciar', iniciarTrueque, name='iniciarTrueque'),
    path('establecer-como-realizado', establecerEstadoRealizado, name='establecerEstadoRealizado'),
    path('establecer-como-no-realizado', establecerEstadoNoRealizado, name='establecerEstadoNoRealizado'),
    path('establecerSucursal/<id>', establecerSucursal, name='establecerSucursal'),
    path('establecerSucursalDone', establecerSucursalSuccess, name='establecerSucursalSuccess'),
    path('aceptartrueque/<int:id>', aceptarTrueque, name='aceptar_trueque'),
    path('cancelartrueque/<int:id>', cancelarTrueque, name='cancelar_trueque'),
]
