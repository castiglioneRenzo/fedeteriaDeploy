import datetime
from django.conf import settings

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
from django.db.models import Q
from fedeteria.utilities import actualizar_calificacion_usuario, iniciar_estados_productos, iniciar_sucursales, iniciar_tags, inicializar_categorias_precios, tiempo_pasado
from datetime import date

from promociones.models import Promocion
from publico.models import *
from trueques.models import Trueque

def inicio(request):
    iniciar_sucursales()
    iniciar_tags()
    inicializar_categorias_precios()
    iniciar_estados_productos()
    #productos = Producto.objects.all(filter(estado_publicacion="Activo")) #deberia hacer esto
    productos = Producto.objects.all()[:5] #me quedo con los primeros 5 productos
    _productos = [{'producto': producto,
                   'imagen': Image.objects.get(producto=producto,principal=True),
                   'tags': list(producto.tags.all()),
                   'tiempo_publicacion': tiempo_pasado(producto.fecha_publicacion),
                   } for producto in productos]
    #promociones activas de productos
    destacados = Promocion.objects.filter(Q(estado_pago='Pagado') & Q(fecha_inicio__lte=date.today()) & Q(fecha_fin__gte=date.today()))
    _destacados = [{'producto': Producto.objects.get(id=promocion.producto_id), 'imagen': Image.objects.get(producto_id=promocion.producto_id, principal=True)} for promocion in destacados]
    return render(request, 'publico/landingPage.html',{'productos':_productos, 'destacados':_destacados, 'selected': "inicio"})

def sucursales(request):
    sucursales = Sucursal.objects.all()
    return render(request, "publico/sucursales.html", {'sucursales': sucursales, 'selected': "sucursales"})

def notFound(request):
    return render(request, "publico/not-found.html")

def emailsRegister(request):
    return render(request, "emails/register.html", {'receiver_name': "Juan Manuel Vila"})


''' --------------- Login / Logout ------------------ '''

def logout_view(request):
    logout(request)
    return redirect('publico:inicio')

@api_view(["GET","POST"])
def userLogin(request):
    if request.user.is_authenticated:
        return redirect("/perfil")

    if request.method == 'POST':
        user = authenticate(request, username=request.POST["dni"], password=request.POST["password"])
        if user is not None:
            login(request, user)

            #acá un condicional para redirigir depende del privilegio que tenga el usuario
            if user.has_perm('publico.admin'):
                return redirect('administracion:inicio') #cambiar a pagina admin
            else:
                if user.has_perm('publico.empleado'):
                    return redirect('/moderacion') #cambiar a pagina empleado
                else:
                    return redirect('publico:perfil')
        else:
            messages.error(request, "Usuario o contraseña invalidos...")
            return redirect('publico:login') #redirect!
    else:
        return render(request, 'publico/login/login.html')

''' --------------- Usuarios ------------------ '''

@api_view(["GET","POST"])
def registrarUsuario(request):
    iniciar_sucursales()
    if request.user.is_authenticated:
        return redirect("/perfil")

    if request.method == 'POST':
        info = request.POST
        if info["repeat_password"] != info["password"]:
            messages.error(request, "Error: Las contraseñas no coinciden!", extra_tags="text-red-400")
            return redirect('publico:registrarUsuario')

        try:
            exists = User.objects.get(username=info["dni"], email=info["email"])
            if exists is not None:
                messages.error(request, "Error: Algunos datos ya estan registrados. Intentalo de nuevo o Inicia Sesion", extra_tags="text-yellow-400")
                return redirect('publico:registrarUsuario')
        except:
            #buscando la sucursal segun lo pasado desde el form
            sucursal = Sucursal.objects.get(id=info["sucursal"])

            new_user = User.objects.create_user(
                username= info["dni"],
                first_name = info["first-name"],
                last_name = info["last-name"],
                email = info["email"],
                password = info["password"],
            )
            new_user.save()
            user = User.objects.get(username = info["dni"])
            #Permiso de usuario cliente
            content_type = ContentType.objects.get_for_model(Permisos)
            permiso = Permission.objects.get(codename='cliente', content_type=content_type)
            # Asignar el permiso al usuario
            user.user_permissions.add(permiso)
            usuario = Usuario.objects.create(
                user = user,
                fecha_nacimiento = info["born"],
                avatar = info["avatar"],
                telefono = info["phone"],
                sucursal_id = sucursal.id,
                ofertas = info.get("offers") is not None,
            )
            usuario.save()

            subject = 'Bienvenido '+ user.first_name +'. Ahora a intercambiar!'
            convert_to_html_content =  render_to_string(
                template_name= 'emails/register.html',
                context= {
                    'user': user,
                    'usuario': usuario
                }
            )
            plain_message = strip_tags(convert_to_html_content)
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],   # recipient_list is self explainatory
                html_message=convert_to_html_content,
            )

            return redirect("/register/done")
    else:
        return render(request, 'publico/login/registrarUsuario.html')

def registrarSuccess(request):
    if request.user.is_authenticated:
        return redirect("/perfil")
    return render(request, "publico/login/registrarSuccess.html")


@api_view(["GET","POST"])
@login_required(login_url='publico:login')
def editarPerfil(request):
    if request.method == 'POST':
        info = request.POST
        user = User.objects.get(username=request.user.username)
        usuario = Usuario.objects.get(user_id=user.id)
        user.first_name = info["first-name"]
        user.last_name = info["last-name"]
        user.email = info["email"]
        user.save()
        usuario.avatar = info["avatar"]
        usuario.telefono = info["phone"]
        usuario.fecha_nacimiento = info["born"]
        usuario.ofertas = info.get("offers") is not None
        usuario.sucursal = Sucursal.objects.get(id=info["sucursal"])
        usuario.save()
        return render(request, 'publico/usuario/editarPerfilSuccess.html')
    usuario = Usuario.objects.get(user_id=request.user.id)
    return render(request, 'publico/usuario/editarPerfil.html', {'sidebar_selected': "tu-perfil-editar-perfil","usuario":usuario})

@login_required(login_url='publico:login')
def verPerfil(request):
    user = User.objects.get(username=request.user.username)
    usuario = Usuario.objects.get(user_id=user.id)
    avatar = usuario.avatar
    sucursal_usuario = Sucursal.objects.get(id=usuario.sucursal.id)
    return render(request, 'publico/usuario/verPerfil.html',{"usuario":usuario, "avatar":avatar, "sucursal":sucursal_usuario, 'sidebar_selected':"tu-perfil-mis-datos"})

@login_required(login_url='publico:login')
def cambiarContraseniaSuccess(request):
    return render(request, 'publico/usuario/cambiarContraseniaSuccess.html')

@api_view(["GET","POST"])
@login_required(login_url='publico:login')
def cambiarContrasenia(request):
    if (request.method == 'POST'):
        info = request.POST
        user = User.objects.get(username=request.user.username)
        if check_password(info["current_password"],user.password):
            if check_password(info["new_password"],user.password):
                messages.error(request, "Error: La contraseña nueva es igual a la anterior. Intentalo de nuevo.", extra_tags="text-red-400")
                return redirect('publico:cambiarContrasenia')
            else:
                if (info["new_password"]==info["repeat_password"]):
                    user.set_password(info["new_password"])
                    user.save()
                    login(request,user)
                    return redirect('publico:cambiarContraseniaSuccess')
                else:
                    messages.error(request, "Error: Las contraseñas no coinciden. Intentalo de nuevo.", extra_tags="text-red-400")
                    return redirect('publico:cambiarContrasenia')
        else:
            messages.error(request, "Error: La contraseña actual es incorrecta. Intentalo de nuevo.", extra_tags="text-red-400")
            return redirect('publico:cambiarContrasenia')
    else:
        return render(request, 'publico/usuario/cambiarContrasenia.html')

def verUsuario(request, username):
    user_buscado = User.objects.get(username=username)
    usuario_buscado = Usuario.objects.get(user_id=user_buscado.id)
    avatar = usuario_buscado.avatar
    sucursal_usuario = Sucursal.objects.get(id=usuario_buscado.sucursal.id)

    productos_user = list( Producto.objects.filter(usuario_id=username) )
    _productos = [{'p': producto, 'imagen': Image.objects.get(producto=producto,principal=True)} for producto in productos_user]

    return render(request, 'publico/usuario/verUsuario.html',{ 'datos_usuario': {"user": user_buscado, "usuario": usuario_buscado, "avatar": avatar, "sucursal": sucursal_usuario }, 'productos': _productos })

def calificarUsuario(request, id):
    if request.method == 'POST':
        info = request.POST
        try:
            calificacion_usuario = int(info['calificacion_usuario1'])
        except ValueError:
            calificacion_usuario = 1
        trueque = Trueque.objects.get(id=id)
        if trueque.producto_1.usuario == request.user:
            usuario = Usuario.objects.get(id=trueque.producto_2.usuario.pk)
        else:
            usuario = Usuario.objects.get(id=trueque.producto_1.usuario.pk)

        if calificacion_usuario is not None:
            actualizar_calificacion_usuario(usuario.id,calificacion_usuario)
            return redirect('publico:calificarUsuarioSuccess')

    else:
        trueque = Trueque.objects.get(id=id)
        if trueque.producto_1.usuario == request.user:
            usuario = Usuario.objects.get(id=trueque.producto_2.usuario.pk)
        else:
            usuario = Usuario.objects.get(id=trueque.producto_1.usuario.pk)

        return render(request, 'publico/usuario/calificarUsuario.html', {'usuario': usuario})

def calificarUsuarioSuccess(request):
    return render(request, 'publico/usuario/calificarUsuarioSuccess.html')

#def calificarEmpleado(request, id):
#    if request.method == 'POST':
#        info = request.POST
#        calificacion_usuario = info['calificacion_usuario1']
#        trueque = Trueque.objects.get(id=id)
#        if trueque.producto_1.usuario == request.user:
#            usuario = Usuario.objects.get(id=trueque.producto_2.usuario.pk)
#        else:
#            usuario = Usuario.objects.get(id=trueque.producto_1.usuario.pk)
#
#        if calificacion_usuario is not None:
#            actualizar_calificacion_usuario(usuario.id,calificacion_usuario)
#            return redirect('publico:calificarUsuarioSuccess')
#
#    else:
#        trueque = Trueque.objects.get(id=id)
#        if trueque.producto_1.usuario == request.user:
#            usuario = Usuario.objects.get(id=trueque.producto_2.usuario.pk)
#        else:
#            usuario = Usuario.objects.get(id=trueque.producto_1.usuario.pk)
#
#        return render(request, 'publico/usuario/calificarEmpleado.html', {'usuario': usuario})


''' -------------- Listado Trueques Usuario ------------------- '''
def listarSolicitudesTrueque(request):
    user = User.objects.get(username=request.user.username)
    trueques = Trueque.objects.filter(producto_1__usuario_id=user.username).filter(estado='Pendiente')
    truequesByMe = Trueque.objects.filter(producto_2__usuario_id=user.username).filter(estado='Pendiente')
    return render(request, 'publico/usuario/listarSolicitudesTrueques.html', {
        'trueques': trueques,
        'truequesByMe':truequesByMe,
        'sidebar_selected': "tu-perfil-mis-solicitudes"})

def verTrueque(request, id):
    trueque = Trueque.objects.get(id=id)
    if trueque.producto_1.usuario == request.user:
        miProducto = Producto.objects.get(id=trueque.producto_1.pk)
        productoAjeno = Producto.objects.get(id=trueque.producto_2.pk)
    else:
        miProducto = Producto.objects.get(id=trueque.producto_2.pk)
        productoAjeno = Producto.objects.get(id=trueque.producto_1.pk)
    imagenMiProducto = Image.objects.get(producto=miProducto, principal=True)
    imagenProdAjeno = Image.objects.get(producto=productoAjeno, principal=True)

    return render(request, 'publico/usuario/verTrueque.html', {'trueque':trueque,
                                                                'imagenMiProducto':imagenMiProducto,
                                                                'imagenProdAjeno':imagenProdAjeno,
                                                                'miProducto': miProducto,
                                                                'productoAjeno': productoAjeno})

def listarSolicitudesTruequesAceptados(request):
    user = User.objects.get(username=request.user.username)
    trueques = Trueque.objects.filter(Q(producto_1__usuario_id=user.username) | Q(producto_2__usuario_id=user.username)).filter(Q(estado='Aceptado') | Q(estado='En_Proceso'))
    print(trueques)
    return render(request, 'publico/usuario/listarSolicitudesAceptadas.html', {
        'trueques': trueques,
        'sidebar_selected': "intercambios-en-proceso"})

def listarTruequesTerminados(request):
    user = User.objects.get(username=request.user.username)
    trueques = Trueque.objects.filter(Q(producto_1__usuario_id=user.username) | Q(producto_2__usuario_id=user.username)).filter(estado='Realizado')
    print(trueques)
    return render(request, 'publico/usuario/listarTruequesTerminados.html', {
        'trueques': trueques,
        'sidebar_selected': "intercambios-terminados"})

def listarSolicitudesCanceladas(request):
    user = User.objects.get(username=request.user.username)
    trueques = Trueque.objects.filter(Q(producto_1__usuario_id=user.username) | Q(producto_2__usuario_id=user.username)).filter(estado='Cancelado')
    return render(request, 'publico/usuario/listarSolicitudesCanceladas.html', {
        'trueques': trueques,
        'sidebar_selected': "intercambios-cancelados"})

''' -------------- Productos ------------------- '''

puntajes = [
    {'id':0, 'value': "Más de 4"},
    {'id':1, 'value': "Más de 3"},
    {'id':2, 'value': "Más de 2"},
    {'id':3, 'value': "Más de 1"},
]
fecha_publicacion = [
    {'id':0, 'value': "Últimas 24 horas"},
    {'id':1, 'value': "Últimos 3 dias"},
    {'id':2, 'value': "Semana pasada"},
    {'id':3, 'value': "Último mes"}
]

def verProductos(request):
    query_params = request.GET

    fechas_id = query_params.get("fechas")
    puntajes_id = query_params.get("puntajes")
    estados_ids = query_params.getlist("estados")
    sucursales_ids = query_params.getlist("sucursales")
    categorias_ids = query_params.getlist("categorias")
    rango_precios_ids = query_params.getlist("rango_precios")

    productos = Producto.objects.all().filter(estado_publicacion="Activo").select_related('usuario', 'usuario__usuario', 'estado_producto')

    if fechas_id:
        if fechas_id == "0":
            productos = productos.filter(fecha_publicacion__date__gte=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        elif fechas_id == "1":
            productos = productos.filter(fecha_publicacion__date__gte=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3))
        elif fechas_id == "2":
            productos = productos.filter(fecha_publicacion__date__gte=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7))
        elif fechas_id == "3":
            productos = productos.filter(fecha_publicacion__date__gte=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30))
    if puntajes_id:
        if puntajes_id == "0":
            productos = productos.filter(usuario__usuario__calificacion__gte=4)
        elif puntajes_id == "1":
            productos = productos.filter(usuario__usuario__calificacion__gte=3)
        elif puntajes_id == "2":
            productos = productos.filter(usuario__usuario__calificacion__gte=2)
        elif puntajes_id == "3":
            productos = productos.filter(usuario__usuario__calificacion__gte=1)

    if estados_ids:
        productos = productos.filter(estado_producto__id__in=estados_ids)
    if rango_precios_ids:
        productos = productos.filter(cat_precio__id__in=rango_precios_ids)
    if categorias_ids:
        productos = productos.filter(tags__id__in=categorias_ids)
    if sucursales_ids:
        productos = productos.filter(usuario__usuario__sucursal__id__in=sucursales_ids)

    _productos = [{'producto': producto,
                   'imagen': Image.objects.get(producto=producto,principal=True),
                   'tags': list(producto.tags.all()),
                   'tiempo_publicacion': tiempo_pasado(producto.fecha_publicacion),
                   } for producto in productos]
    return render(request, 'publico/productos/verProductos.html', {
        'productos': _productos,
        'selected': 'productos',
        'sucursales': Sucursal.objects.all(),
        'categorias': Tag.objects.all(),
        'rango_precios': CategoriaPrecio.objects.all(),
        'estados_productos': EstadoProducto.objects.all(),
        'fecha_publicacion': fecha_publicacion,
        'puntajes': puntajes,
        'filtros': {
            'categorias': [int(id) for id in categorias_ids],
            'sucursales': [int(id) for id in sucursales_ids],
            'estados_ids': [int(id) for id in estados_ids],
            'rango_precios_ids': [int(id) for id in rango_precios_ids],
            'fechas_id': int(fechas_id) if fechas_id else None,
            'puntajes_id': int(puntajes_id) if puntajes_id else None
        }
    })

def verProducto(request, id):
    producto = Producto.objects.get(pk=id)
    if producto is None:
        return redirect("/not-found")

    user_owner = User.objects.get(username=producto.usuario_id)
    usuario_owner = Usuario.objects.get(user_id=user_owner.id)
    sucursal_usuario = Sucursal.objects.get(id=usuario_owner.sucursal.id)
    _imagenPrincipal = Image.objects.get(producto=producto, principal=True)
    _imagenesSecundarias = Image.objects.filter(producto=producto, principal=False)
    tags = list(producto.tags.all())
    return render(request, 'publico/productos/verProducto.html', {
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
        'imagenes_secundarias': _imagenesSecundarias
    })

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.cliente'), redirect_field_name=None, login_url='publico:perfil')
def verProductosPerfil(request):
    productos_user = list( Producto.objects.filter(usuario_id=request.user.username) )
    _productos = [{'p': producto,'tiempo_publicacion': tiempo_pasado(producto.fecha_publicacion),
                   'imagen': Image.objects.get(producto=producto,principal=True)
                   } for producto in productos_user]
    return render(request, 'publico/usuario/verProductosPerfil.html', {
        'sidebar_selected': "productos-mis-productos",
        "productos": _productos
    })

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.cliente'), redirect_field_name=None, login_url='publico:perfil')
def verProductoPerfil(request, id):
    producto = Producto.objects.get(pk=id)
    if producto is None or producto.usuario_id != request.user.username:
        return redirect("/perfil/productos")


    # usuario = Usuario.objects.get(user_id=request.user.id)
    # print("calificacion nueva: ", usuario.calificacion, " | nuemero calificaciones: ", usuario.num_calificaciones)
    # actualizar_calificacion_usuario(usuario_id=request.user.id, nueva_calificacion=1)
    # usuario = Usuario.objects.get(user_id=request.user.id)
    # print("calificacion nueva: ", usuario.calificacion, " | nuemero calificaciones: ", usuario.num_calificaciones)

    tags = list(producto.tags.all())
    return render(request, 'publico/usuario/verProductoPerfil.html', {
        'sidebar_selected': "productos-mis-productos",
        'producto': producto,
        'tiempo_publicacion': tiempo_pasado(producto.fecha_publicacion),
        'categorias': tags,
        'imagen_principal': Image.objects.get(producto=producto, principal=True),
        'imagenes_secundarias': Image.objects.filter(producto=producto, principal=False)
    })

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.cliente'), redirect_field_name=None, login_url='publico:perfil')
def eliminarProducto(request, id):
    try:
        producto = Producto.objects.get(id=id)
    except Producto.DoesNotExist:
        messages.error(request, "El producto que desea eliminar no existe.")
        return redirect("/perfil/productos")

    if producto is None or producto.usuario_id != request.user.username:
        messages.error(request, "Debes ser el dueño de este producto para eliminarlo.")
        return redirect("/perfil/productos")
    else:
        producto.delete()
        messages.success(request, "El producto fue eliminado exitosamente.")
        return redirect("/perfil/productos")

@api_view(["GET","POST"])
@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.cliente'), redirect_field_name=None, login_url='publico:login')
def cargarProducto(request):
    ''' Cargar un nuevo producto '''

    if request.user is None:
        return redirect("publico:login")

    if request.method == 'POST':
        info = request.POST
        # Cargar informacion de producto
        user = User.objects.get(username=request.user.username)
        producto = Producto(nombre=info['nombre'],
                            descripcion=info['descripcion'],
                            estado_producto=EstadoProducto.objects.get(id=info['estado']),
                            usuario=user
                            )
        # Cargar imagen principal
        if request.FILES.get('imagen_principal') is not None:
            producto.save()
            img = request.FILES.get('imagen_principal')
            imagen = Image(producto=producto, principal=True)
            imagen.image.save(img.name, ContentFile(img.read()), save=True)
        else:
            messages.error(request, "Error: Debe cargar una imagen principal", extra_tags="text-red-400")
            return redirect('publico:cargarProducto')
        # Cargar imagenes secundarias
        for i in range(1, 4):
            img = request.FILES.get(f'imagen_sec_{i}', None)
            if img is not None:
                imagen = Image(producto=producto)
                imagen.image.save(img.name, ContentFile(img.read()), save=True)
        # Cargar categorias
        _tags = [Tag.objects.get(nombre=tag) for tag in info.getlist('categorias')]
        for _tag in _tags:
            producto.tags.add(_tag)
        return redirect('publico:cargarProductoSuccess')
    else:
        tags = Tag.objects.all()
        estados_productos = EstadoProducto.objects.all()
        return render(request, 'publico/productos/cargarProducto.html', {"sidebar_selected":"productos-agregar-producto", "tags":tags, 'estados_productos': estados_productos})

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.cliente'), redirect_field_name=None, login_url='publico:login')
def cargarProductoSuccess(request):
    return render(request, 'publico/productos/cargarProductoSuccess.html')

'''
Para restringir el uso de funcionalidades dependiendo del permiso del usuario (administrador, empleado o cliente)
se puede usar el siguiente decorador:
@user_passes_test(lambda u: u.has_perm('publico.cliente'), redirect_field_name=None, login_url='publico:perfil')
'''
