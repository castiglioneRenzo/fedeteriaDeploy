from django.shortcuts import render
from publico.models import *
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from fedeteria.utilities import darPermiso, tiempo_pasado
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.core.files.base import ContentFile

from publico.models import *
from trueques.models import *
from administracion.models import ImagenPromo, Promocion


@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
def inicio(request):
    return render(request, 'administracion/dashboard.html')

#

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
def verResumenTruequesPorSucursal(request):
    _suc = Sucursal.objects.all()
    return render(request, 'administracion/trueques/SeleccionResumenPorSucursal.html', {
        'sucursales': _suc,
        'cant_total': Trueque.objects.filter(estado="Realizado").count(),
        'cant_trueques_suc_1': Trueque.objects.filter(sucursal_id=1).filter(estado="Realizado").count(),
        'cant_trueques_suc_2': Trueque.objects.filter(sucursal_id=2).filter(estado="Realizado").count(),
        'cant_trueques_suc_3': Trueque.objects.filter(sucursal_id=3).filter(estado="Realizado").count(),
        'cant_trueques_suc_4': Trueque.objects.filter(sucursal_id=4).filter(estado="Realizado").count(),
        'cant_trueques_suc_5': Trueque.objects.filter(sucursal_id=5).filter(estado="Realizado").count(),
        'cant_trueques_suc_6': Trueque.objects.filter(sucursal_id=6).filter(estado="Realizado").count(),
        'sidebar_selected': "estadisticas-trueques-por-sucursal"})

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
def verTruequesSucursal(request, idsucursal):
    _suc = Sucursal.objects.get(id=idsucursal)
    trueques = Trueque.objects.filter(sucursal_id=_suc.id).filter(estado="Realizado")
    _trueques = [{'trueque': trueque,
                    'ventas': Venta.objects.filter(trueque_id=trueque.id).count(),
                    'producto_1': Producto.objects.get(id=trueque.producto_1.id),
                    'imagen_1': Image.objects.get(producto=Producto.objects.get(id=trueque.producto_1.id),principal=True),
                    'producto_2': Producto.objects.get(id=trueque.producto_2.id),
                    'imagen_2': Image.objects.get(producto=Producto.objects.get(id=trueque.producto_2.id),principal=True),
                } for trueque in trueques]
    return render(request, 'administracion/trueques/verPorSucursal.html', {'trueques': _trueques, 'sucursal': _suc, 'sidebar_selected': "estadisticas-trueques-por-sucursal"})

#

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
def verResumenVentasPorSucursal(request):
    _suc = Sucursal.objects.all()
    cant_ventas_suc_1 = Venta.objects.filter(trueque__sucursal_id=1, trueque__estado="Realizado").count() or 0
    cant_ventas_suc_2 = Venta.objects.filter(trueque__sucursal_id=2, trueque__estado="Realizado").count() or 0
    cant_ventas_suc_3 = Venta.objects.filter(trueque__sucursal_id=3, trueque__estado="Realizado").count() or 0
    cant_ventas_suc_4 = Venta.objects.filter(trueque__sucursal_id=4, trueque__estado="Realizado").count() or 0
    cant_ventas_suc_5 = Venta.objects.filter(trueque__sucursal_id=5, trueque__estado="Realizado").count() or 0
    cant_ventas_suc_6 = Venta.objects.filter(trueque__sucursal_id=6, trueque__estado="Realizado").count() or 0


    return render(request, 'administracion/ventas/SeleccionResumenPorSucursal.html', {
        'sucursales': _suc,
        'cant_total': Venta.objects.all().count(),
        'cant_ventas_suc_1': cant_ventas_suc_1,
        'cant_ventas_suc_2': cant_ventas_suc_2,
        'cant_ventas_suc_3': cant_ventas_suc_3,
        'cant_ventas_suc_4': cant_ventas_suc_4,
        'cant_ventas_suc_5': cant_ventas_suc_5,
        'cant_ventas_suc_6': cant_ventas_suc_6,
        'sidebar_selected': "estadisticas-ventas-por-sucursal"})

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
def verVentasSucursal(request, idsucursal):
    _suc = Sucursal.objects.get(id=idsucursal)
    ventas = Venta.objects.filter(trueque__sucursal_id=idsucursal, trueque__estado="Realizado")
    return render(request, 'administracion/ventas/verPorSucursal.html', {'ventas': ventas, 'sucursal': _suc, 'sidebar_selected': "estadisticas-ventas-por-sucursal"})


#
@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
def verPromociones(request):
    promociones = Promocion.objects.all()
    _promociones = []
    for promocion in promociones:
        try:
            imagen = ImagenPromo.objects.get(promocion=promocion)
        except ImagenPromo.DoesNotExist:
            imagen = None  # o algún valor predeterminado
        _promociones.append({
            'datos': promocion,
            'imagen': imagen,
        })
    return render(request, 'administracion/promociones/verPromociones.html', {"sidebar_selected": "promociones-ver-promociones", 'promociones': _promociones})


@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
@api_view(["GET","POST"])
def registrarPromocion(request):
    if request.method == 'POST':
        info = request.POST
        try:
            exists = Promocion.objects.get(id=info['id'])
            if exists is not None:
                messages.warning(request, "Error: El producto ya está promocionado.", extra_tags="text-yellow-400")
                return redirect('administracion:registrarPromocion')
        except:
            info = request.POST

            try:
                promocion = Promocion.objects.create(
                    id=info["id"],
                    nombre=info["nombre"],
                    promocion=info["promocion"]
                )

                imagen_principal = request.FILES.get('imagen_principal')

                if imagen_principal is not None:
                    img = ContentFile(imagen_principal.read())
                    imagen = ImagenPromo(promocion=promocion)
                    imagen.image.save(imagen_principal.name, img, save=True)
                else:
                    messages.error(request, "Error: Debe cargar una imagen principal", extra_tags="text-red-400")
                    promocion.delete()  # Elimina la promoción creada si no hay imagen
                    return redirect('administracion:registrarPromocion')

            except Exception as e:
                messages.error(request, f"Error al registrar la promoción: {str(e)}", extra_tags="text-red-400")
                return redirect('administracion:registrarPromocion')

        messages.success(request, "Promoción registrada exitosamente", extra_tags="text-green-400")
        return redirect('administracion:verPromociones')
    else:
        return render(request, 'administracion/promociones/registrarPromocion.html', {"sidebar_selected": "promociones-promocionar-producto"})

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
@api_view(["GET","POST"])
def eliminarPromocion(request, idpromo):
    try:
        promocion = Promocion.objects.get(id=idpromo)
    except Promocion.DoesNotExist:
        messages.error(request, "El producto que desea eliminar no existe.")
        return redirect('administracion:verPromociones')
    else:
        promocion.delete()
        messages.success(request, "El producto fue eliminado exitosamente.")
        return redirect('administracion:verPromociones')

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
@api_view(["GET","POST"])
def registrarEmpleado(request):
    if request.method == 'POST':
        info = request.POST
        if info["repeat_password"] != info["password"]:
            messages.error(request, "Error: Las contraseñas no coinciden!", extra_tags="text-red-400")
            return redirect('administracion:registrarEmpleado')

        try:
            exists = User.objects.get(username=info["dni"])
            if exists is not None:
                messages.warning(request, "Error: El DNI ya está registrado. Inténtalo de nuevo o inicia sesión.", extra_tags="text-yellow-400")
                return redirect('administracion:registrarEmpleado')
        except:
            sucursal = Sucursal.objects.get(id=info["sucursal"])

            new_user = User.objects.create_user(
                username=info["dni"],
                first_name=info["first-name"],
                last_name=info["last-name"],
                email=info["email"],
                password=info["password"],
            )
            new_user.save()
            user = User.objects.get(username=info["dni"])
            # dar permiso
            darPermiso(user, 'empleado')
            empleado = Usuario.objects.create(
                user=user,
                fecha_nacimiento=info["born"],
                avatar=info["avatar"],
                telefono=info["phone"],
                sucursal_id=sucursal.id,
            )
            empleado.save()
            return redirect('administracion:registrarEmpleadoSuccess')
    else:
        return render(request, 'administracion/registrarEmpleado.html', {"sidebar_selected":"registrar-empleados"})

@login_required(login_url='publico:login')
@user_passes_test(lambda u: u.has_perm('publico.admin'), redirect_field_name=None, login_url='publico:inicio')
def registrarEmpleadoSuccess(request):
    return render(request, "administracion/registrarEmpleadoSuccess.html")