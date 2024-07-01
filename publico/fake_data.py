import os
import django
import uuid
import requests
from random import *
from django.core.files.base import ContentFile
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from faker import Faker

from publico.models import *

# como usar esta wea: Solo genera usuarios (clientes) y productos (descarga las imagenes, lo unico que no pude ponerle que funque bien es que ponga mas de una categoria).
#  Si quieren hacer un flush es cuestiuon de ustedes.
# Tienen que poner en la consola lo siguiente: 
# 1- Si hicieron un fluish al menos inicien una vez el server asi genera categorias y esas cosas
# 2- Instalen : pip install requests  y pip install faker
# 3- python manage.py shell -> cuando les deja entrar mas comandos ponen -> 4
# 4- from publico.fake_data import crear_productos, crear_usuarios
# 5- crear_usuarios(10) -> donde dice 10 pongan los que quieran generar
# 6- crear_productos(20) -> donde dice 20 pongan los que quieran generar
# despues meto para que genere trueques tambien

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

fake = Faker('es')

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return ContentFile(response.content)
    else:
        print(f'Failed to download image from {url}')
        return None
        
def crear_usuarios(cantidad):
    sucursales = Sucursal.objects.all()
    # Crear algunos usuarios y sus perfiles
    for _ in range(cantidad):
        dni = fake.unique.random_number(digits=8, fix_len=True)
        info = {
            "dni": dni,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "password": "Abcd1234",
            "born": fake.date_of_birth(minimum_age=18, maximum_age=80),
            "avatar": fake.random_element(['/avatars/avatar_1.avif', '/avatars/avatar_2.avif', '/avatars/avatar_3.avif', '/avatars/avatar_4.avif', '/avatars/avatar_5.avif']),
            "phone": fake.random_number(digits=9, fix_len=True),
            "sucursal": fake.random_element(sucursales).id,
            "offers": fake.boolean(chance_of_getting_true=70)
        }

        new_user = User.objects.create_user(
            username=info["dni"],
            first_name=info["first_name"],
            last_name=info["last_name"],
            email=info["email"],
            password=info["password"],
        )
        new_user.save()
        user = User.objects.get(username=info["dni"])
        # Permiso de usuario cliente
        content_type = ContentType.objects.get_for_model(Permisos)
        permiso = Permission.objects.get(codename='cliente', content_type=content_type)
        # Asignar el permiso al usuario
        user.user_permissions.add(permiso)
        usuario = Usuario.objects.create(
            user=user,
            fecha_nacimiento=info["born"],
            avatar=info["avatar"],
            telefono=info["phone"],
            sucursal_id=info["sucursal"],
            ofertas=info["offers"],
        )
        usuario.save()

def crear_productos(cantidad):
    tags = Tag.objects.all()
    estados_producto = EstadoProducto.objects.all()
    categorias_precio = CategoriaPrecio.objects.all()
    # Crear algunos productos
    for _ in range(cantidad):
        user = User.objects.order_by('?').first()

        herramienta_aleatoria = fake.random_element([
    "Taladro", "Martillo", "Llave inglesa", "Sierra circular", "Destornillador",
    "Alicates", "Cinta métrica", "Nivel de burbuja", "Lijadora", "Pistola de clavos",
    "Soldadora", "Serrucho", "Corta alambre", "Tenazas", "Pinza de presión",
    "Broca", "Cepillo de carpintero", "Cúter", "Caladora", "Llave de tubo",
    "Llave Allen", "Multímetro", "Pistola de calor", "Espátula", "Amoladora",
    "Maza", "Tornillo de banco", "Compresor de aire", "Pulverizador de pintura", "Detector de metales"
])
        info = {
            'nombre': herramienta_aleatoria,
            'descripcion': fake.text(max_nb_chars=200).replace('\n', ''),
            'estado': fake.random_element(estados_producto).id,
            'cat_precio': fake.random_element(categorias_precio).id,
        }
        if fake.boolean(chance_of_getting_true=70):
            producto = Producto(
                nombre=info['nombre'],
                descripcion=info['descripcion'],
                estado_producto=EstadoProducto.objects.get(id=info['estado']),
                usuario=user,
                cat_precio=CategoriaPrecio.objects.get(id=info['cat_precio']),
                estado_publicacion="Activo"
            )
            producto.save()
            
            # Descargar y guardar imágenes principales y secundarias
            for i in range(1, 5):
                img_url =   "https://picsum.photos/800/600"
                img_content = download_image(img_url)
                if img_content:
                    img_uuid = uuid.uuid4()
                    img_name = f'{img_uuid}.jpg'

                    imagen = Image(
                        producto=producto,
                        principal=(i == 1)
                    )
                    imagen.image.save(img_name, img_content, save=True)



            producto.tags.add(fake.random_element(tags))
        else:
            producto = Producto(
                nombre=info['nombre'],
                descripcion=info['descripcion'],
                estado_producto=EstadoProducto.objects.get(id=info['estado']),
                usuario=user,
                estado_publicacion="Pausado"
            )
            producto.save()

            # Descargar y guardar imágenes principales y secundarias
            for i in range(1, 5):
                img_url =   "https://picsum.photos/800/600"
                img_content = download_image(img_url)
                if img_content:
                    img_uuid = uuid.uuid4()
                    img_name = f'{img_uuid}.jpg'

                    imagen = Image(
                        producto=producto,
                        principal=(i == 1)
                    )
                    imagen.image.save(img_name, img_content, save=True)



            producto.tags.add(fake.random_element(tags))


import random
from trueques.models import Trueque, Venta

def actualizar_estado_producto(producto, estado_trueque):
    if estado_trueque == 'Pendiente':
        producto.estado_publicacion = 'Activo'
    elif estado_trueque in ['Aceptado', 'En_Proceso']:
        producto.estado_publicacion = 'En intercambio'
    elif estado_trueque == 'Realizado':
        producto.estado_publicacion = 'Intercambiado'
    elif estado_trueque in ['Cancelado', 'No_Realizado']:
        producto.estado_publicacion = 'Activo'
    producto.save()

def generar_trueques():
    productos = list(Producto.objects.filter(estado_publicacion='Activo'))
    num_productos = len(productos)
    sucursales = list(Sucursal.objects.all())
    estados_posibles = ['Pendiente', 'Aceptado', 'Cancelado', 'En_Proceso', 'Realizado', 'No_Realizado']

    if num_productos < 2:
        print("No hay suficientes productos activos para generar trueques.")
        return
    
    # Generar trueques (al menos la mitad del total posible)
    num_trueques = num_productos * (num_productos - 1) // 2 // 2

    for _ in range(num_trueques):
        producto_1 = random.choice(productos)
        producto_2 = random.choice([p for p in productos if p != producto_1])
        estado = random.choice(estados_posibles)
        sucursal = random.choice(sucursales) if sucursales else None

        trueque = Trueque(
            producto_1=producto_1,
            producto_2=producto_2,
            estado=estado,
            sucursal=sucursal
        )
        trueque.save()

        # Actualizar estado de los productos involucrados
        actualizar_estado_producto(producto_1, estado)
        actualizar_estado_producto(producto_2, estado)

        # Generar ventas solo si el trueque ha finalizado
        if estado in ['Realizado', 'No_Realizado']:
            generar_ventas_para_trueque(trueque)
        

def generar_ventas_para_trueque(trueque):
    # Generar una cantidad aleatoria de ventas
    num_ventas = random.randint(1, 10)

    for _ in range(num_ventas):
        cantidad_vendida = random.randint(1, 100)
        precio_total = random.uniform(10, 1000)
        producto = random.choice([trueque.producto_1, trueque.producto_2])

        Venta.objects.create(
            producto=producto.id,
            cantidad_vendida=cantidad_vendida,
            precio_total=precio_total,
            trueque=trueque
        )
