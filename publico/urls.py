from django.contrib import admin
from django.urls import path, include
from publico.views import *

urlpatterns = [
    # _-_-_-_ _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
    # _-_-_-_ urls sin login required _-_-_-_
    path('', inicio, name='inicio'),
    path('sucursales', sucursales, name='sucursales'),
    path('not-found', notFound, name='not-found'),
    path('emails/register', emailsRegister),

        # productos visualizacion y acciones
    path('productos', verProductos, name='productos'),
    path('productos/producto/<id>', verProducto),

    path('usuario/<username>', verUsuario, name='verUsuario'),   #dni basicamente

        # relacionado a auth
    path('register', registrarUsuario, name='registrarUsuario'),
    path('register/done', registrarSuccess, name='registrarSuccess'),
    path('login', userLogin, name='login'),
    path('logout', logout_view, name='logout'),

    # _-_-_-_ _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
    # _-_-_-_ urls con login required _-_-_-_
    path('perfil', verPerfil, name='perfil'),
    path('perfil/editar', editarPerfil, name='editarPerfil'),

    path('perfil/cambiarcontrasenia', cambiarContrasenia, name='cambiarContrasenia'),
    path('perfil/cambiarcontrasenia/done', cambiarContraseniaSuccess, name='cambiarContraseniaSuccess'),

    # a partir de aca accedido solo por clientes!
    path('perfil/cargarProducto', cargarProducto, name='cargarProducto'),
    path('perfil/cargarProducto/done', cargarProductoSuccess, name='cargarProductoSuccess'),

    path('perfil/productos', verProductosPerfil, name='verProductosPerfil'),
    path('perfil/productos/producto/<id>', verProductoPerfil),
    path('perfil/productos/producto/eliminar/<id>', eliminarProducto, name='eliminarProducto'),
    path('perfil/solicitudes', listarSolicitudesTrueque, name='solicitudesTrueques'),
    path('perfil/solicitudesAceptadas', listarSolicitudesTruequesAceptados, name='intercambiosEnProceso'),
    path('perfil/intercambiosTerminados', listarTruequesTerminados, name='intercambiosTerminados'),
    path('perfil/solicitudesCanceladas', listarSolicitudesCanceladas, name='intercambiosCancelados'),
    path('perfil/verTrueque/<id>', verTrueque, name='verTrueque'),
    path('perfil/calificarUsuario/<id>', calificarUsuario, name='calificarUsuario'),
    path('perfil/calificarUsuarioDone', calificarUsuarioSuccess, name='calificarUsuarioSuccess'),
    ]
