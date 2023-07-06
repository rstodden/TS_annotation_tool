from django.urls import path, re_path, include
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    # path('home', views.home, name="home"),
    # re_path('^pairs_list', views.pairs_list, name='pairs_list'),
    # path('pairs_list/', views.PairsListView.as_view(), name='pairs_list'),
    # re_path(r'^rate_pair/', views.rate_pair, name='rate_pair'),
    path('transformations/', views.transformations, name='transformations'),
    path('error_operations/', views.error_operations, name='error_operations'),
    path('rating/', views.rating, name='rating'),
    path('rating/<int:pair_id>', views.rate_pair, name='rate_pair'),
    path('transformations/<int:pair_id>', views.select_transformations, name='select_transformation'),
    path('error_operations/<int:pair_id>', views.select_errors, name='select_errors'),
]