from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('alignment/', include(('alignment.urls', "alignment"), namespace="alignment")),
    path('rating/', include(('rating.urls', "rating"), namespace="rating")),
    path('evaluation/', include(('evaluation.urls', "evaluation"), namespace="evaluation")),
    path('accounts/', include(('accounts.urls', "accounts"), namespace="accounts")),
    path('data/', include(('data.urls', "data"), namespace="data")),
    path('data/', include(('simplification.urls', "simplification"), namespace="simplification")),
    re_path('^$', views.home, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)