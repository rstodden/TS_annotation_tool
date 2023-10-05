from django.contrib import admin
from .models import Rating, Transformation, Error_Operation

# Register your models here.

# admin.site.register(Pair)
admin.site.register(Rating)
admin.site.register(Transformation)
admin.site.register(Error_Operation)
