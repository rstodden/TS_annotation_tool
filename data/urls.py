from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.insert_data, name="insert_data"),
    path('sentence/<int:sentence_id>', views.sentence_problem, name="sentence_problem"),
    # path('', views.home, name="home"),
]
