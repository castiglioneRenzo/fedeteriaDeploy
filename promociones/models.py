from django.db import models
from publico.models import Producto

class Promocion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    estado_pago = models.CharField(max_length=50, default='Pendiente')
    duracion = models.IntegerField(null=True)
    fecha_inicio = models.DateField(null=True)
    fecha_fin = models.DateField(null=True)

    def __str__(self):
        return self.nombre