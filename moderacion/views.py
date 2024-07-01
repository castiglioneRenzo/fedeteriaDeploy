from django.shortcuts import render, redirect
from django.contrib import messages
from fedeteria.utilities import tiempo_pasado, actualizar_calificacion_usuario
from publico.models import *
from trueques.models import *
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required(login_url='publico:login')
@user_passes_test(lambda u: ( u.has_perm('publico.empleado') or u.has_perm('publico.admin') ), redirect_field_name=None, login_url='publico:inicio')
def inicio(request):
    return render(request, 'moderacion/dashboard.html')

@login_required(login_url='publico:login')
@user_passes_test(lambda u: ( u.has_perm('publico.empleado') or u.has_perm('publico.admin') ), redirect_field_name=None, login_url='publico:inicio')
def productos(request):
    if request.method == 'POST':
        info = request.POST
        cat_precio = CategoriaPrecio.objects.get(id=info["cat_precio"])
        producto = Producto.objects.get(id=info["producto_id"])
        producto.cat_precio = cat_precio
        producto.estado_publicacion = 'Activo'
        producto.save()
        messages.success(request, "Producto actualizado")
        return redirect('moderacion:productos')
    _productos = Producto.objects.filter(cat_precio=None)
    productos = [{'p':prod, 'imagen': Image.objects.get(producto=prod, principal=True), 'categorias': list(prod.tags.all()), 'tiempo_publicacion': tiempo_pasado(prod.fecha_publicacion),} for prod in _productos]
    cat_precios = CategoriaPrecio.objects.all()
    return render(request, 'moderacion/productos.html', {'sidebar_selected': 'productos-productos-sin-precio',"productos":productos, "cat_precios":cat_precios})


@login_required(login_url='publico:login')
@user_passes_test(lambda u: ( u.has_perm('publico.empleado') or u.has_perm('publico.admin') ), redirect_field_name=None, login_url='publico:inicio')
def verTruequesEnProceso(request):
    trueques = Trueque.objects.filter(estado="En_Proceso")
    return render(request, 'moderacion/trueques.html', { 'sidebar_selected': 'trueques-trueques-en-proceso', "trueques": trueques })

def calificarUsuarios(request, id):
    if request.method == 'POST':
        info = request.POST
        try:
            calificacion_usuario1 = int(info['calificacion_usuario1'])
        except ValueError:
            calificacion_usuario1 = 1
        try:
            calificacion_usuario2 = int(info['calificacion_usuario2'])
        except ValueError:
            calificacion_usuario2 = 1
        # Aquí deberías guardar las calificaciones en los usuarios correspondientes
        # Por ejemplo:
        trueque = Trueque.objects.get(id=id)
        _user1 = User.objects.get(pk=trueque.producto_1.usuario.id)
        _user2 = User.objects.get(pk=trueque.producto_2.usuario.id)
        usuario1 = Usuario.objects.get(user=_user1)
        usuario2 = Usuario.objects.get(user=_user2)
        if calificacion_usuario1 is not None and calificacion_usuario2 is not None:
            actualizar_calificacion_usuario(usuario1.id,calificacion_usuario1)
            actualizar_calificacion_usuario(usuario2.id,calificacion_usuario2)
            return redirect('moderacion:calificarUsuariosSuccess',trueque.id)
        #else:
        #    messages.error(request, "Error: No se ingresaron las dos calificaciones. Intente nuevamente.", extra_tags="text-red-400")
    else:
        trueque = Trueque.objects.get(id=id)
        _user1 = User.objects.get(pk=trueque.producto_1.usuario.id)
        _user2 = User.objects.get(pk=trueque.producto_2.usuario.id)
        usuario1 = Usuario.objects.get(user=_user1)
        usuario2 = Usuario.objects.get(user=_user2)
        return render(request, 'moderacion/calificarUsuarios.html', {'usuario1': usuario1, 'usuario2': usuario2})

def calificarUsuariosSuccess(request,id):
    return render(request, 'moderacion/calificarUsuariosSuccess.html',{'id': id})

def penalizarUsuarios(request, id):
    if request.method == 'POST':
        info = request.POST
        try:
            penalizacion_usuario1 = int(info['calificacion_usuario1'])
            penalizacion_usuario2 = int(info['calificacion_usuario2'])
        except ValueError:
            penalizacion_usuario1 = 0
            penalizacion_usuario2 = 0
            # return redirect('moderacion:inicio')
        # Aquí deberías guardar las calificaciones en los usuarios correspondientes
        # Por ejemplo:
        trueque = Trueque.objects.get(id=id)
        _user1 = User.objects.get(pk=trueque.producto_1.usuario.id)
        _user2 = User.objects.get(pk=trueque.producto_2.usuario.id)
        usuario1 = Usuario.objects.get(user=_user1)
        usuario2 = Usuario.objects.get(user=_user2)
        if penalizacion_usuario1 is not None and penalizacion_usuario2 is not None:
            if usuario1.calificacion is None or usuario2.calificacion is None:
                usuario1.calificacion = 0
                usuario2.calificacion = 0
            if usuario1.calificacion > penalizacion_usuario1:
                usuario1.calificacion -= penalizacion_usuario1
            if usuario2.calificacion > penalizacion_usuario2:
                usuario2.calificacion -= penalizacion_usuario2
            usuario1.save()
            usuario2.save()
            return redirect('moderacion:penalizarUsuariosSuccess',trueque.id)
        #else:
        #    messages.error(request, "Error: No se ingresaron las dos calificaciones. Intente nuevamente.", extra_tags="text-red-400")
    else:
        trueque = Trueque.objects.get(id=id)
        _user1 = User.objects.get(pk=trueque.producto_1.usuario.id)
        _user2 = User.objects.get(pk=trueque.producto_2.usuario.id)
        usuario1 = Usuario.objects.get(user=_user1)
        usuario2 = Usuario.objects.get(user=_user2)
    return render(request, 'moderacion/penalizarUsuarios.html', {'usuario1': usuario1, 'usuario2': usuario2})

def penalizarUsuariosSuccess(request,id):
    return render(request, 'moderacion/penalizarUsuariosSuccess.html',{'id':id})


def cargarVentas(request, id):
    if request.method == 'POST':
        info = request.POST
        trueque = Trueque.objects.get(id=id)
        venta = Venta()
        venta.producto = info['id_producto']
        venta.trueque = trueque
        venta.cantidad_vendida = info['cantidad_vendida']
        venta.precio_total = float(info['precio_por_unidad']) * int(info['cantidad_vendida'])
        venta.save()
        messages.success(request, "Venta cargada con éxito")
        return redirect('moderacion:cargarVentas', trueque.id)
    return render(request, 'moderacion/cargarVentas.html')
