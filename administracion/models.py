from django.db import models

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'administracion/promociones/{0}'.format(filename)

# Create your models here.
class Promocion(models.Model):
    id = models.CharField(max_length=40, null=False, primary_key=True)
    nombre = models.CharField(max_length=40, null=False)
    promocion = models.CharField(max_length=200, null=False)
    fecha_publicacion = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.nombre

class ImagenPromo(models.Model):
    promocion = models.ForeignKey(Promocion, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path)

    def __str__(self):
        return self.image.url