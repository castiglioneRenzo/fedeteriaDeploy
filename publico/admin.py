from django.contrib import admin
from publico.models import *
from trueques.models import Trueque

# Register your models here.
admin.site.register(Tag)
admin.site.register(Producto)
admin.site.register(Sucursal)
admin.site.register(Usuario)
admin.site.register(CategoriaPrecio)
admin.site.register(Trueque)