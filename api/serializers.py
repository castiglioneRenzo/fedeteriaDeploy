from rest_framework import serializers
from publico.models import *
from promociones.models import Promocion
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image  
        exclude = ['principal']

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        exclude = ['tags']
    
class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'

class CategoriaPrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPrecio
        fields = '__all__'

class EstadoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoProducto
        fields = '__all__'

class PromocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocion
        fields = '__all__'

class EsPromocionadoSerializer(serializers.Serializer):    
    id = serializers.IntegerField()
    es_promocionado = serializers.BooleanField()
    id_promocion = serializers.IntegerField()
    estado_pago = serializers.CharField()