from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Cart
from billing.models import BillingProfile
from users.forms import GuestForm
from django.contrib.auth.forms import AuthenticationForm
from addresses.models import Address
from products.models import Product
from orders.models import Order
from addresses.forms import AddressForm


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [
        {
            'id': x.id,
            'title': x.title,
            'price': x.price,
            'url': x.get_absolute_url()
        }
        for x in cart_obj.products.all()
    ]

    cart_data = {
        'products': products,
        'subtotal': cart_obj.subtotal,
        'total': cart_obj.total,

    }
    return JsonResponse(cart_data)


def CartHome(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    context = {
        'cart': cart_obj
    }
    return render(request, 'carts/cart-view.html', context)


def CartUpdate(request):
    product_id = request.POST.get('product_id')

    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print('Massage to User: Product has gone')
            redirect('cart-home')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        request.session['cart_items'] = cart_obj.products.count()
        if is_ajax(request):
            print('Ajax')
            json_data = {
                'added': added,
                'removed': not added,
                'cartItemCount': cart_obj.products.count(),
            }
            return JsonResponse(json_data, status=200)
            # return JsonResponse({'message': 'Error 400'}, status=400)
        # cart_obj.products.add(product_id)
    return redirect('cart-home')


def checkout_view(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect('cart-home')

    login_form = AuthenticationForm()
    guest_form = GuestForm()
    address_form = AddressForm()

    billing_address_id = request.session.get('billing_address_id', None)
    shipping_address_id = request.session.get('shipping_address_id', None)

    billing_profile, billing_guest_profile_create = BillingProfile.objects.new_or_get(request)
    address_qs = None
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()

    if request.method == 'POST':
        is_done = order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            request.session['cart_items'] = 0
            del request.session['cart_id']
            return redirect('checkout-success')

    context = {
        'object': order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
    }
    return render(request, 'carts/checkout.html', context)


def checkout_done(request):
    return render(request, 'carts/checkout-done.html', {})
