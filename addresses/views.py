from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect
from billing.models import BillingProfile
from .forms import AddressForm
from .models import Address

def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)
    context = {
        'form': form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        print(request.POST)
        instance = form.save(commit=False)

        billing_profile, billing_guest_profile_create = BillingProfile.objects.new_or_get(request)
        print(billing_profile)
        if billing_profile is not None:
            address_type = request.POST.get('address_type', 'shipping')
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()
            request.session[address_type + '_address_id'] = instance.id
            print(address_type + '_address_id')
        else:
            print('Error')
            return redirect('checkout')

        if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
            return redirect(redirect_path)
    return redirect('checkout')


def checkout_address_reuse_view(request):
    if request.user.is_authenticated:
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == 'POST':
            print(request.POST)
            shipping_address = request.POST.get('shipping_address', None)
            address_type = request.POST.get('address_type', 'shipping')
            billing_profile, billing_guest_profile_create = BillingProfile.objects.new_or_get(request)
            if shipping_address is not None:
                qs = Address.objects.filter(id=shipping_address, billing_profile=billing_profile)
                if qs.exists():
                    request.session[address_type + '_address_id'] = shipping_address
                if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
                    return redirect(redirect_path)
    return redirect('checkout')