from django.db import models
from publico.models import Producto, Sucursal


    
class Trueque(models.Model):
    producto_1 = models.ForeignKey(Producto, on_delete=models.DO_NOTHING, related_name='producto_1')
    producto_2 = models.ForeignKey(Producto, on_delete=models.DO_NOTHING, related_name='producto_2')
    fecha_inicio = models.DateTimeField(auto_now=True)
    fecha_fin = models.DateTimeField(null=True)
    estado = models.CharField(max_length=30, default='Pendiente')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING, null=True)

class Venta(models.Model):
    producto = models.IntegerField()
    cantidad_vendida= models.IntegerField()
    precio_total = models.FloatField()
    trueque = models.ForeignKey(Trueque, on_delete=models.DO_NOTHING, null=True)
                                 
                                 

# Iniciado: Solicitud de trueque creada por usuario del productoX -> No es aun nada. Falta que el usuario del productoY lo acepte. ->
# Aceptado: El usuario 2 lo acepta y se espera a que pongan sucursal cualquiera de los dos. O se puede cancelar ->
# Cancelado: canelones
# En_Proceso: Truque en curso (Van a la fedeteria y se chupan la pija) -> Se espera a que el empleado lo finalice tanto como Realizado o como No_Realizado ->
# Realizado o No_Realizado: Aca se termina la wea