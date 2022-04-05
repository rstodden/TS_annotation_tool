from django.urls import path, re_path, include
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    # path('home', views.home, name="home"),
    path('', views.show_simplification, name="simplify"),
    path('add', views.add_simplification, name="add"),
    path('get', views.get_simplification, name="get"),
    path('edit/<int:pair_id>', views.edit_simplification, name="edit"),
    path('save', views.save_simplification, name="save"),
    path('delete/<int:pair_id>', views.delete_simplification, name="delete"),
    path('<int:sent_id>/edit_by_sent', views.edit_simplification_of_sent, name="edit_simplification_of_sent"),

]