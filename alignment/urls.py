from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('change_alignment/<int:doc_id>', views.change_alignment, name="change_alignment"),
	# path("overview/", views.PairsListView.as_view()) # overview documents to align
    path("overview/", views.overview, name="overview"),
]