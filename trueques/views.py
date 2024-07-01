from django.core import serializers
from django.conf import settings
from django.shortcuts import render, redirect
from fedeteria.utilities import tiempo_pasado
from publico.models import Producto, Sucursal, Usuario, Image
from django.contrib.auth.models import User
from trueques.models import Trueque
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
# Para los emails
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@login_required(login_url='publico:login')
def iniciarTrueque(request):
    ''' Iniciar un trueque de 2 productos de productos publicados por usuarios registrados '''
    if request.method == 'POST':
        # Crear un nuevo trueque
        producto1=request.POST['producto_ext']
        producto2=request.POST['producto_int']
        producto1 = Producto.objects.get(pk=producto1)
        producto2 = Producto.objects.get(pk=producto2)
        Trueque.objects.create(producto_1=producto1, producto_2=producto2)
        # Enviar un email al usuario del producto 1
        subject = 'Hola '+ producto1.usuario.first_name +'. Tienes una nueva solicitud de trueque!'
        convert_to_html_content =  render_to_string(
                template_name= 'emails/iniciarTrueque.html',
                context= {
                    'user': producto1.usuario,
                    'usuario': Usuario.objects.get(user=producto1.usuario),
                }
            )
        plain_message = strip_tags(convert_to_html_content)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[producto1.usuario.email],
            html_message=convert_to_html_content,
        )
        # Enviar un email al usuario del producto 2
        subject = 'Hola '+ producto2.usuario.first_name +'. Has iniciado un nuevo trueque'
        convert_to_html_content =  render_to_string(
                template_name= 'emails/iniciarTrueque.html',
                context= {
                    'user': producto2.usuario,
                    'usuario': Usuario.objects.get(user=producto2.usuario),
                }
            )
        plain_message = strip_tags(convert_to_html_content)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[producto2.usuario.email],
            html_message=convert_to_html_content,
        )
        messages.success(request, 'Trueque iniciado')
        return redirect('publico:solicitudesTrueques')

@login_required(login_url='publico:login')
def seleccionarProductoTrueque(request, id):
    producto = Producto.objects.get(pk=id)
    if producto is None:
        return redirect("/not-found")
    user_owner = User.objects.get(username=producto.usuario_id)
    if user_owner.id == request.user.id:
        return redirect("/productos/producto/" + str(producto.id))

    usuario_owner = Usuario.objects.get(user_id=user_owner.id)
    sucursal_usuario = Sucursal.objects.get(id=usuario_owner.sucursal.id)
    _imagenPrincipal = Image.objects.get(producto=producto, principal=True)
    _imagenesSecundarias = Image.objects.filter(producto=producto, principal=False)
    tags = list(producto.tags.all())
    productos = Producto.objects.filter(usuario_id=request.user.username).filter(cat_precio_id=producto.cat_precio_id).filter(estado_publicacion='Activo')
    jsonproductos = serializers.serialize('json', productos)
    imagenes = Image.objects.filter(producto__usuario_id=request.user.username)
    imagenes = serializers.serialize('json', imagenes)
    return render(request, 'trueques/index.html', {
        'productos': productos,
        'jsonproductos': jsonproductos,
        'imagenes': imagenes,
        'producto': producto,
        'tiempo_publicacion': tiempo_pasado(producto.fecha_publicacion),
        'categorias': tags,
        'duenio': {
            'username': user_owner.username,
            'email': user_owner.email,
            'nombre': user_owner.first_name,
            'apellido': user_owner.last_name,
            'avatar': usuario_owner.avatar,
            'telefono': usuario_owner.telefono,
            'sucursal': sucursal_usuario,
            'calificacion': usuario_owner.calificacion,
            'num_calificaciones': usuario_owner.num_calificaciones,
        },
        'imagen_principal': _imagenPrincipal,
        'imagenes_secundarias': _imagenesSecundarias})



@login_required(login_url='publico:login')
@user_passes_test(lambda u: ( u.has_perm('publico.empleado') or u.has_perm('publico.admin') ), redirect_field_name=None, login_url='publico:inicio')
def establecerEstadoRealizado(request):
    if request.method == 'POST':
        info = request.POST
        trueque = Trueque.objects.get(id=info["id_trueque"])
        trueque.estado = "Realizado"
        trueque.save()
        # AGREGAR UNA NOTIFICACION A LOS USUARIOS INVILUCRADOS

        producto1 = Producto.objects.get(pk=trueque.producto_1.id)
        producto1.estado_publicacion = "Intercambiado"
        producto1.save()
        producto2 = Producto.objects.get(pk=trueque.producto_2.id)
        producto2.estado_publicacion = "Intercambiado"
        producto2.save()

        return redirect('moderacion:calificarUsuarios',trueque.id)

@login_required(login_url='publico:login')
@user_passes_test(lambda u: ( u.has_perm('publico.empleado') or u.has_perm('publico.admin') ), redirect_field_name=None, login_url='publico:inicio')
def establecerEstadoNoRealizado(request):
    if request.method == 'POST':
        info = request.POST
        trueque = Trueque.objects.get(id=info["id_trueque"])
        trueque.estado = "No_Realizado"
        trueque.save()
        # AGREGAR UNA NOTIFICACION A LOS USUARIOS INVILUCRADOS

        producto1 = Producto.objects.get(pk=trueque.producto_1.id)
        producto1.estado_publicacion = "Activo"
        producto1.save()
        producto2 = Producto.objects.get(pk=trueque.producto_2.id)
        producto2.estado_publicacion = "Activo"
        producto2.save()

        return redirect('moderacion:penalizarUsuarios',trueque.id)

@login_required(login_url='publico:login')
def establecerSucursal(request, id):
    if request.method == 'POST':
        info = request.POST
        trueque = Trueque.objects.get(id=id)
        trueque.sucursal = Sucursal.objects.get(id=info["sucursal"])
        trueque.estado = "En_Proceso"
        trueque.save()
        return redirect('trueques:establecerSucursalSuccess')
    return render(request,'trueques/establecerSucursal.html',{"id":id})

def establecerSucursalSuccess(request):
    return render(request, 'trueques/establecerSucursalSuccess.html')

@login_required(login_url='publico:login')
def aceptarTrueque(request, id):
    ''' Aceptar un trueque '''
    trueque = Trueque.objects.get(pk=id)
    if trueque is None:
        return redirect("/not-found")
    trueque.estado = 'Aceptado'
    trueque.save()
    messages.success(request, 'Trueque aceptado')

    producto1 = Producto.objects.get(pk=trueque.producto_1.id)
    producto1.estado_publicacion = "En intercambio"
    producto2 = Producto.objects.get(pk=trueque.producto_2.id)
    producto2.estado_publicacion = "En intercambio"

    producto1.save(update_fields=["estado_publicacion"])
    producto2.save(update_fields=["estado_publicacion"])

    # Enviar un email al usuario del producto 1
    subject = 'Hola '+ trueque.producto_1.usuario.first_name +'. Has aceptado un trueque'
    convert_to_html_content =  render_to_string(
            template_name= 'emails/aceptarTrueque.html',
            context= {
                'user': trueque.producto_1.usuario,
                'usuario': Usuario.objects.get(user=trueque.producto_1.usuario),
                'producto1': producto1,
                'producto2': producto2,
            }
        )
    plain_message = strip_tags(convert_to_html_content)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[trueque.producto_1.usuario.email],
        html_message=convert_to_html_content,
    )
    # Enviar un email al usuario del producto 2
    subject = 'Hola '+ trueque.producto_2.usuario.first_name +'. Has aceptado un trueque'
    convert_to_html_content =  render_to_string(
            template_name= 'emails/aceptarTrueque.html',
            context= {
                'user': trueque.producto_2.usuario,
                'usuario': Usuario.objects.get(user=trueque.producto_2.usuario),
                'producto1': producto1,
                'producto2': producto2,
            }
        )
    plain_message = strip_tags(convert_to_html_content)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[trueque.producto_2.usuario.email],
        html_message=convert_to_html_content,
    )
    return redirect('publico:intercambiosEnProceso')

@login_required(login_url='publico:login')
def cancelarTrueque(request, id):
    '''Se cancela un trueque'''
    trueque = Trueque.objects.get(pk=id)
    if trueque is None:
        return redirect("/not-found")
    trueque.estado = 'Cancelado'
    trueque.save()

    producto2 = Producto.objects.get(pk=trueque.producto_2.id)
    producto2.estado_publicacion = "Activo"
    producto2.save()
    producto1 = Producto.objects.get(pk=trueque.producto_1.id)
    producto1.estado_publicacion = "Activo"
    producto1.save()

    messages.success(request, 'Trueque cancelado')
    return redirect('publico:solicitudesTrueques')