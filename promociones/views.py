from datetime import date, timedelta
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

from promociones.models import Promocion
from publico.models import Producto

from django.conf import settings
from fedeteria.utilities import create_preference, getPrecioPromocion


@login_required(login_url='publico:login')
def promocionar_producto(request, idProducto):
    '''recibo el id del producto a promocionar en idProducto, creo una nueva promocion y la asocio al producto con idProducto, luego redirijo a la pagina de promociones'''
    producto = Producto.objects.get(id=idProducto)
    if request.method == 'POST':
        promocion = Promocion(producto=producto, duracion=(int(request.POST['duracion'])))
        # Esto se va a hacer posteriormente en el pago con mercado pago
        promocion.estado_pago = 'Pendiente'
        promocion.fecha_inicio = date.today()
        promocion.fecha_fin = promocion.fecha_inicio + timedelta(days=promocion.duracion)
        # Fin de lo que se va a hacer en el pago con mercado pago
        promocion.save()
        item_title = "Promocion de producto: " + producto.nombre + " \npor: " + str(promocion.duracion) + " dias"
        item_quantity = 1
        item_currency_id = "ARS"
        item_unit_price = getPrecioPromocion(int(request.POST['duracion']))

        preference = create_preference(promocion.id, item_title, item_quantity, item_currency_id, item_unit_price, promocion.id)
        print(preference['init_point'])
        return redirect(preference['init_point'])
        # return render(request, 'pago/payment.html', {
        #     'preference_id': preference['id'],
        #     'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
        # })
    return render(request, 'promociones/promocionar_producto.html', {'producto': producto})

@login_required(login_url='publico:login')
def pagar_promocion(request, idPromocion):
    '''redirijo a la pagina de pago de mercado pago'''
    if request.method == 'POST':
        # Aqui se deberia realizar la integracion con mercado pago
        # Una vez que se haya realizado el pago, se deberia cambiar el estado de la promocion a 'Pagado' y asignarle las fechas de inicio y fin
        promocion = Promocion.objects.get(id=idPromocion)
        promocion.estado_pago = 'Pagado'
        promocion.fecha_inicio = date.today()
        promocion.fecha_fin = promocion.fecha_inicio + date.timedelta(days=promocion.duracion)
        promocion.save()
        return redirect('promociones:ver_detalles_promocion', idPromocion=idPromocion)
    return redirect("/not-found")

@login_required(login_url='publico:login')
def ver_detalles_promocion(request, idPromocion):
    '''recibo el id de la promocion a ver en idPromocion y muestro los detalles de la promocion'''
    promocion = Promocion.objects.get(id=idPromocion)
    producto = Producto.objects.get(id=promocion.producto.id)
    return render(request, 'promociones/detalles_promocion.html', {'promocion': promocion, 'producto': producto})


# Integración con Mercado Pago

def payment_view(request):
    if request.method == "POST":
        # Datos de prueba para el ejemplo
        item_title = "Producto de prueba"
        item_quantity = 1
        item_currency_id = "ARS"
        item_unit_price = 100.0

        preference = create_preference(item_title, item_quantity, item_currency_id, item_unit_price)

        return render(request, 'pago/payment.html', {
            'preference_id': preference['id'],
            'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
        })
    return render(request, 'pago/checkout.html')

def success_view(request):
    status = request.GET.get('status')
    external_reference = request.GET.get('external_reference')
    print(status)
    print(external_reference)
    promocion = Promocion.objects.get(id=external_reference)
    promocion.estado_pago = 'Pagado'
    promocion.save()
    return render(request, 'pago/success.html')

def failure_view(request):
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    merchant_order_id = request.GET.get('merchant_order_id')
    print(payment_id)
    print(status)
    print(merchant_order_id)
    return render(request, 'pago/failure.html')

def pending_view(request):
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    merchant_order_id = request.GET.get('merchant_order_id')
    print(payment_id)
    print(status)
    print(merchant_order_id)
    return render(request, 'pago/pending.html')
