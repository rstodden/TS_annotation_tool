from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.pairs_list, name='pairs_list'),
    # path('home', views.home, name="home"),
    path('pairs_list', views.pairs_list, name='pairs_list'),
    re_path(r'^rate_pair/', views.rate_pair, name='rate_pair'),
]