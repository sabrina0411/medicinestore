from django.urls import path
from .views import (
    UserLoginView, UserLogoutView, RegisterView, guest_register_view,
    ProfileView
)

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/guest/', guest_register_view, name='guest_register'),
    path('profile/', ProfileView.as_view(), name='profile'),

]

