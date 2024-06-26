from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from billing.models import BillingProfile
from .forms import UserRegistrationForm, GuestForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect, render
from .models import GuestEmail
from .signals import user_logged_in


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = 'users/login.html'
    success_message = 'You are successfully logged in'

    def dispatch(self, request, *args, **kwargs):
        try:
            del request.session['guest_email_id']
        except:
            pass
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form = super(UserLoginView, self).form_valid(form)  # Complete the Login Task First.
        request = self.request
        user = request.user  # Then get the uses
        user_logged_in.send(user.__class__, instance=user, request=request)
        # print(user)
        return form


class UserLogoutView(LogoutView):
    template_name = 'users/logout.html'
    next_page = 'home'


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'users/register.html'
    success_message = 'Registration is completed. Please Login in here'


def guest_register_view(request):
    form = GuestForm(request.POST or None)
    context = {
        'form': form,
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None

    if form.is_valid():
        email = form.cleaned_data.get('email')
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id
        if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect('users/register.html')
    return render(request, 'users/register.html', context)


class ProfileView(TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        billing_profiles = BillingProfile.objects.filter(user=user)
        context = {
            "billing_profiles": billing_profiles,
        }
        return context
