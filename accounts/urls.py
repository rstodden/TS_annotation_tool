from django.urls import path, re_path, include
from . import views

urlpatterns = [
    re_path('', include('django.contrib.auth.urls')),
    path("register/", views.register, name="register"),
]