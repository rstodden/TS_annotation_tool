from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('insert_data', views.insert_data, name="insert_data"),
    path('insert_plain_data', views.insert_data_by_plain_text, name="insert_plain_data"),
    path('insert_web_data', views.insert_data_by_url, name="insert_web_data"),
    path('<int:corpus_id>/doc/<int:doc_pair_id>/sentence/<int:sentence_id>', views.sentence_problem, name="sentence_problem"),
    # path('', views.home, name="home"),
]
