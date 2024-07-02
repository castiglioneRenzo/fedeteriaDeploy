from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from publico.models import Permisos, Sucursal, Tag, CategoriaPrecio, EstadoProducto, Usuario
import mercadopago
from django.conf import settings

import datetime

def darPermiso(user, p):
    ''' Dar permiso a un usuario. Los permisos son: 'admin', 'empleado', 'cliente' '''
    content_type = ContentType.objects.get_for_model(Permisos)
    permiso = Permission.objects.get(codename=p, content_type=content_type)
    user.user_permissions.add(permiso)
    user.save()
    return True

def iniciar_sucursales():
    ''' Inicializa las sucursales en la base de datos '''
    sucursales = [
        {"localidad": "Capital Federal", "direccion": "Av. Monroe | num. 1428"},{"localidad": "La Plata", "direccion": "Calle 55 | num. 483 e/ 4 y 5"},{"localidad": "Chivilcoy", "direccion": "Calle 25 de mayo | num. 212"},{ "localidad": "Dolores", "direccion": "Bartolomé Mitre | num. 76"},{ "localidad": "Berazategui", "direccion": "Av. 21 | num. 3955"},{ "localidad": "Bahia Blanca", "direccion": "Av. Leandro Niceforo Alem | num. 455"}
    ]
    for sucursal in sucursales:
        Sucursal.objects.get_or_create(**sucursal)

def iniciar_estados_productos():
    ''' Inicializa los estados_productos en la base de datos '''
    estados_productos = [
        {"nombre": "Nuevo"},
        {"nombre": "Casi nuevo"},
        {"nombre": "Reacondicionado"},
        {"nombre": "Usado"},
        {"nombre": "Dañado"},
    ]
    for estado in estados_productos:
        EstadoProducto.objects.get_or_create(**estado)

def iniciar_tags():
    ''' Inicializa los tags en la base de datos '''
    tags = [
        {"nombre": "Carpinteria"},
        {"nombre": "Electricidad"},
        {"nombre": "Electronica"},
        {"nombre": "Hogar"},
        {"nombre": "Industrial"},
        {"nombre": "Jardineria"},
        {"nombre": "Construccion"},
    ]
    for tag in tags:
        Tag.objects.get_or_create(**tag)

def inicializar_categorias_precios():
    ''' Inicializa las categorias de precios en la base de datos '''
    categorias_precios = [
        ("I",  "$1-1000"),
        ("II",  "$1000-2500"),
        ("III",  "$2500-5000"),
        ("IV",  "$5000-7500"),
        ("V",  "$7500-10000"),
        ("VI",  "$10000-$20000"),
        ("VII",  "$20000-40000"),
        ("VIII",  "$40000-70000"),
        ("IX",  "$70000-100000"),
        ("X",  ">$10000"),
    ]

    for nombre, rango_precios in categorias_precios:
        CategoriaPrecio.objects.get_or_create(nombre=nombre, rango=rango_precios)

def tiempo_pasado(fecha_creacion):
    #obtener la fecha actual
    fecha_actual = datetime.datetime.now(datetime.timezone.utc)
    #calcular los dias que pasaron desde la fecha de nacimiento
    segundos = (fecha_actual - fecha_creacion).seconds
    minutos = segundos / 60
    horas = int(minutos / 60)
    dias = (fecha_actual - fecha_creacion).days
    meses = int(dias / 30)

    print( segundos, minutos, horas, dias, meses)

    if dias >= 1 and dias < 30:
        #retornar los dias
        if dias == 1:
            return "hace un dia"
        else:
            return "hace " + str(dias) + " dias"
    else:
        if dias >= 30:
            if meses <= 1:
                return "hace un mes"
            else:
                return "hace " + str(meses) + " meses"
        else:
            if horas <= 1:
                return "hace una hora"
            else:
                return "hace " + str(horas) + " horas"

from decimal import Decimal, ROUND_HALF_UP

def actualizar_calificacion_usuario(usuario_id, nueva_calificacion):
    usuario = Usuario.objects.get(pk=usuario_id)

    if usuario.calificacion is None:
        usuario.calificacion = Decimal('0.0')

    # Calcular la nueva calificación ponderada
    calificacion_total = usuario.calificacion * usuario.num_calificaciones
    calificacion_total += Decimal(str(nueva_calificacion))
    usuario.num_calificaciones += 1
    nueva_calificacion_promedio = calificacion_total / usuario.num_calificaciones

    # Redondear a un decimal
    nueva_calificacion_promedio = nueva_calificacion_promedio.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    # Asegurarse de que la calificación final no sea mayor a 5
    usuario.calificacion = min(nueva_calificacion_promedio, Decimal('5.0'))

    # Guardar los cambios en la base de datos
    usuario.save()

# services

sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

def create_preference(id, item_title, item_quantity, item_currency_id, item_unit_price, promocion_id):
    preference_data = {
        "items": [
            {
                "id": id,
                "title": item_title,
                "quantity": item_quantity,
                "currency_id": item_currency_id,
                "unit_price": item_unit_price
            }
        ],
        "back_urls": {
            "success": "https://fedeteria.pythonanywhere.com/promociones/success",
            "failure": "https://fedeteria.pythonanywhere.com/promociones/failure",
            "pending": "https://fedeteria.pythonanywhere.com/promociones/pending"
        },
        "auto_return": "approved",
        "external_reference": promocion_id,
    }
    preference_response = sdk.preference().create(preference_data)
    return preference_response["response"]

def getPrecioPromocion(duracion):
    ''' Devuelve el precio de la promocion segun la duracion '''
    match duracion:
        case 7:
            return 1000.0
        case 15:
            return 1800.0
        case 30:
            return 3500.0
        case _:
            return 0.0