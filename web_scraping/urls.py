from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.home, name="home")
    # path('iaa/', views.iaa, name='iaa'),
]
