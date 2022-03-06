
from re import template
from . import views
from django.urls import path
from django.contrib.auth import views as auth_view

urlpatterns=[
    path('',views.home,name = 'home'),
    path('register/',views.register,name = 'register'),
    path('login/',auth_view.LoginView.as_view(template_name='users/login.html'),name='login')
]