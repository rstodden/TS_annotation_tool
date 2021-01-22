from django.urls import path, re_path, include
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    # path('home', views.home, name="home"),
    # re_path('^pairs_list', views.pairs_list, name='pairs_list'),
    # path('pairs_list/', views.PairsListView.as_view(), name='pairs_list'),
    # re_path(r'^rate_pair/', views.rate_pair, name='rate_pair'),
    path('doc/<int:doc_pair_id>/rating/<int:pair_id>', views.rate_pair, name='rate_pair'),
    path('doc/<int:doc_pair_id>/transformation/<int:pair_id>', views.select_transformation, name='select_transformation')
]