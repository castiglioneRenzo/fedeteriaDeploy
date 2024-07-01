from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    user_id=instance.producto.usuario.id
    return 'productos/user_{0}/{1}'.format(user_id, filename)

class Tag(models.Model):
    nombre = models.CharField(max_length=20)
    
    def __str__(self) -> str:
        return self.nombre
    
class EstadoProducto(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.nombre
    
class CategoriaPrecio(models.Model):
    nombre = models.CharField(max_length=10, null=True)
    rango = models.CharField(max_length=30, null=True)

    def __str__(self) -> str:
        return self.nombre

class Producto(models.Model):
    usuario = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE, blank=False) #creo que poniendo que esto se relacione al username (dni) es mas comodo. No se como cambiar el nombre de la columna sin ques e rompa todo
    nombre = models.CharField(max_length=40, null=False)
    descripcion = models.CharField(max_length=200, null=False)        
    estado_producto = models.ForeignKey(EstadoProducto, on_delete=models.DO_NOTHING, related_name='estado_producto', null=True)
    estado_publicacion = models.CharField(max_length=20, default="Pausado")
    fecha_publicacion = models.DateTimeField(auto_now=True)
    cat_precio = models.ForeignKey(CategoriaPrecio, on_delete=models.DO_NOTHING, related_name='cat_precio', null=True)
    tags = models.ManyToManyField(Tag, related_name='tags')

    def __str__(self) -> str:
        return self.nombre

class Image(models.Model):
    producto = models.ForeignKey(Producto, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path)
    principal = models.BooleanField(default=False)

    def __str__(self):
        return self.image.url

class Sucursal(models.Model):
    localidad = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.localidad
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField()
    avatar = models.CharField(max_length=200)
    telefono = models.IntegerField()
    sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING, related_name='sucursal_user')
    ofertas = models.BooleanField(default=True)
    puntos = models.IntegerField(default=0)
    calificacion = models.DecimalField(null=True, blank=True, default=0.0, max_digits=3, decimal_places=1)
    num_calificaciones = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.user.username + ' ' + self.user.first_name

class Permisos(models.Model):
    class Meta:
        permissions = (
            ('admin', 'Administrador de sistema'),
            ('empleado', 'Empleado de la sucursal'),
            ('cliente', 'Cliente registrado'),
        )