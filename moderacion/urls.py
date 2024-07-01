from django.urls import path
from moderacion.views import *

urlpatterns = [    
    path('', inicio, name='inicio'),
    path('productos/', productos, name='productos'),
    path('trueques-en-proceso', verTruequesEnProceso, name='verTruequesEnProceso'),
    path('calificarUsuarios/<id>', calificarUsuarios, name='calificarUsuarios'),
    path('calificarUsuariosDone/<id>', calificarUsuariosSuccess, name='calificarUsuariosSuccess'),
    path('penalizarUsuarios/<id>', penalizarUsuarios, name="penalizarUsuarios"),
    path('penalizarUsuariosDone/<id>', penalizarUsuariosSuccess, name='penalizarUsuariosSuccess'),
    path('cargarVentas/<id>', cargarVentas, name='cargarVentas'),
    ]
