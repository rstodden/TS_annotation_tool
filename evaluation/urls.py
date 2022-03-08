from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.export, name="home"),
    path('export_alignment', views.export_alignment_view, name="export_alignments"),
    path('export_transformations', views.export_ratings_view, name="export_ratings"),
    path('export_ratings', views.export_transformations_view, name="export_transformations"),
    path('export_iaa_alignment', views.export_iaa_alignment, name="export_iaa_alignment"),
    path('export_iaa_transformation', views.export_iaa_transformation, name="export_iaa_transformation"),
    path('export_iaa_rating', views.export_iaa_rating, name="export_iaa_rating"),
    # path('export_full_document', views.full_document_export, name="full_document_export"),
    path('export_full_aligned_document', views.full_aligned_document_export, name="full_aligned_document_export"),
    path('meta_data', views.meta_data, name="meta_data"),
    path('meta_data_export', views.meta_data_export, name="meta_data_export"),
    path('export_transformations_as_iob', views.export_transformations_as_iob, name="export_transformations_as_iob"),

    path('export_data_sheet', views.export_data_sheet, name="export_data_sheet"),
    path('export_user_data', views.export_user_data, name="export_user_data"),
    path('export_meta_data', views.export_meta_data, name="export_meta_data"),
    path('export_all_in_csv_per_use', views.export_all_in_csv_per_use, name="export_all_in_csv_per_use"),
    path('export_alignment_for_crf', views.export_alignment_for_crf, name="export_alignment_for_crf"),



    # path('home', views.export, name="home"),
    # path('iaa/', views.iaa, name='iaa'),
]
