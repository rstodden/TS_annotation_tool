from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    #
    path('change_alignment/<int:alignment_id>', views.change_alignment, name="change_alignment"),
    path('change_alignment/', views.create_alignment, name="create_alignment"),
	# path("overview/", views.PairsListView.as_view()) # overview documents to align

]