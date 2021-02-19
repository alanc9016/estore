from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import stripe

# Create your views here.
from cart.cart import Cart 
from products.models import Product


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = 1
    cart = Cart(request)
    q = cart.add(product, product.price, quantity)
    if q == 1:
        messages.success(request, 'Added to your cart!')
    return redirect('cart')


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_cart(request):
    cart = list(Cart(request).cart_serializable().items())
    if request.is_ajax():
        return JsonResponse({'cart': cart}, status=200)
    return render(request, 'cart/cart.html')

def success_view(request):
    cart = Cart(request).clear()
    return render(request, 'cart/success.html')

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        # domain_url = 'http://127.0.0.1:8000'
        domain_url = 'https://salty-eyrie-13923'
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items= list(Cart(request).cart_serializable_stripe().values()),
                    mode='payment',
                    success_url=domain_url + '/success/',
                    cancel_url=domain_url + '/cart/',
                    shipping_address_collection={
                        'allowed_countries': ['US'],
                      },
                    allow_promotion_codes=True,
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error':str(e)})

