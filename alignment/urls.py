from django.urls import path, re_path, include
from . import views

urlpatterns = [
    # path('', views.home, name="home"),
    #
    # path('change_alignment/<int:alignment_id>', views.change_alignment, name="change_alignment"),
    path('', views.show_alignments, name="change_alignment"),
    path('<int:pair_id>/delete', views.delete_alignment, name="delete_alignment"),
    path('<int:pair_id>/edit', views.edit_alignment, name="edit_alignment"),
    path('add', views.add_alignment, name="add_alignment"),
    path('save', views.save_alignment, name="save_alignment"),
    # path('doc/<int:doc_pair_id>/alignment/<int:pair_id>/save_edit', views.save_edit_alignment, name="save_edit_alignment"),
    path('not_possible', views.alignment_not_possible, name="not_possible"),
    path('<int:sent_id>/edit_by_sent', views.edit_alignment_of_sent, name="edit_alignment_of_sent"),
    # path("overview/", views.PairsListView.as_view()) # overview documents to align

]