from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.export, name="home"),
    # path('home', views.export, name="home"),
    # path('iaa/', views.iaa, name='iaa'),
]
