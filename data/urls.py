from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.insert_data, name="insert_data"),
    # path('', views.home, name="home"),
]
