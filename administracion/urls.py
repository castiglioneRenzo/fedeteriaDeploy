from django.urls import path
from administracion.views import *

urlpatterns = [    
    path('', inicio, name='inicio'),
    path('dashboard', inicio, name='inicio'),
    
    # 
    
    path('estadisticas-trueques', verResumenTruequesPorSucursal, name='estadisticasTrueques'),
    path('estadisticas-trueques/<idsucursal>', verTruequesSucursal, name='estadisticasTruequesSucursal'),

    path('estadisticas-ventas', verResumenVentasPorSucursal, name='estadisticasVentas'),
    path('estadisticas-ventas/<idsucursal>', verVentasSucursal, name='estadisticasVentasSucursal'),


    # 
    
    path('promocionar-producto', registrarPromocion, name='registrarPromocion'),
    path('ver-promociones', verPromociones, name='verPromociones'),
    path('promocion/eliminar/<idpromo>', eliminarPromocion, name='eliminarPromocion'),
    
    # 
    
    path('registrarEmpleado', registrarEmpleado, name='registrarEmpleado'),
    path('registrar-empleado/done', registrarEmpleadoSuccess, name='registrarEmpleadoSuccess'),
    ]
#ARREGLAR ESOT QUE TIENE MIL COSAS