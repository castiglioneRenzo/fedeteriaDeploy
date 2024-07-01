from datetime import date
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import status
from django.http import Http404
#Modelos
from publico.models import Image, Producto, Sucursal, CategoriaPrecio
from django.contrib.auth.models import User
from django.db.models import Q

class Image_APIView(APIView):
    ''' Recibo un id de producto en pk y devuelvo su imagen principal '''
    def get(self, request, pk):
        try:
            response = Image.objects.get(producto_id=pk, principal=True)
            serialize = ImageSerializer(response)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class Images_APIView(APIView):
    '''Recibo un id de producto en pk y devuelvo todas sus imagenes'''
    def get(self, request, pk):
        try:
            response = Image.objects.filter(producto_id=pk)
            serialize = ImageSerializer(response, many=True)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class Producto_APIView(APIView):
    ''' Recibo un id de producto en pk y devuelvo sus datos '''
    def get(self, request, pk):
        try:
            response = Producto.objects.get(id=pk)
            serialize = ProductoSerializer(response)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class ProductosUsuario_APIView(APIView):
    ''' Recibo un id de usuario en pk y devuelvo todos sus productos '''
    def get(self, request, pk):
        try:
            response = Producto.objects.filter(usuario_id=pk)
            serialize = ProductoSerializer(response, many=True)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class Productos_APIView(APIView):
    ''' Devuelvo todos los productos'''
    def get(self, request):
        try:
            response = Producto.objects.all()
            serialize = ProductoSerializer(response, many=True)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class Sucursal_APIView(APIView):
    ''' Devuelvo todas las sucursales'''
    def get(self, request):
        try:
            response = Sucursal.objects.all()
            serialize = SucursalSerializer(response, many=True)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class CategoriaPrecio_APIView(APIView):
    ''' Devuelvo todas las categorias de precios'''
    def get(self, request):
        try:
            response = CategoriaPrecio.objects.all()
            serialize = CategoriaPrecioSerializer(response, many=True)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class EstadoProducto_APIView(APIView):
    ''' Devuelvo todos los estados de productos'''
    def get(self, request):
        try:
            response = EstadoProducto.objects.all()
            serialize = EstadoProductoSerializer(response, many=True)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class EstadoProductoId_APIView(APIView):
    ''' Devuelvo el estado de producto correspondiente al id recibido'''
    def get(self, request, id):
        try:
            response = EstadoProducto.objects.get(id=id)
            serialize = EstadoProductoSerializer(response)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class Promocion_APIView(APIView):
    ''' Devuelvo todas las promociones activas'''
    def get(self, request):
        try:
            response = Promocion.objects.filter(Q (estado_pago='Pagado') & Q(fecha_inicio__lte=date.today()) & Q(fecha_fin__gte=date.today()))
            serialize = PromocionSerializer(response, many=True)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404

class Promocion_Producto_APIView(APIView):
    ''' Recibo un id de producto en pk y devuelvo todas sus promociones activas'''
    def get(self, request, pk):
        try:
            response = Promocion.objects.filter(Q (producto_id=pk) & Q(fecha_inicio__lte=date.today()) & Q(fecha_fin__gte=date.today()))
            # serialize = PromocionSerializer(response, many=True)
            if response.exists():
                response = {'id': pk,'es_promocionado': True, 'id_promocion': response.get().id, 'estado_pago': response.get().estado_pago}
            else:
                response = {'id': pk,'es_promocionado': False, 'id_promocion': None, 'estado_pago': None}
            serialize = EsPromocionadoSerializer(response)
            return Response(serialize.data)
        except Image.DoesNotExist:
            raise Http404