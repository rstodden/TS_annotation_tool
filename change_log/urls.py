from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.show_changelog, name="change_log"),
    path('', views.show_changelog, name="show_changelog"),
    path('add_item', views.add_item, name="add_item"),
    path('save', views.save_finished, name="save_finished"),
]
