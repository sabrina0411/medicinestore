from django.shortcuts import render
from .forms import ContactForm
from django.http import JsonResponse, HttpResponse


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {
        'title': 'Contact',
        'content': ' Welcome to the contact page.',
        'form': contact_form,
    }

    if contact_form.is_valid():
        print(contact_form.cleaned_data)
        if is_ajax(request):
            data = {
                'message': 'Thank you for your submission'
            }
            return JsonResponse(data)

    if contact_form.errors:
        errors = contact_form.errors.as_json()
        if is_ajax(request):
            return HttpResponse(errors, status=400, content_type='application/json')

    return render(request, 'contact_us/contact_view.html', context)
