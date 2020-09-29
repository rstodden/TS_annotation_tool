from django.contrib import admin
from .models import AlignmentPair, Assessment, Sentence, Document

# Register your models here.

admin.site.register(AlignmentPair)
admin.site.register(Assessment)
admin.site.register(Sentence)
admin.site.register(Document)
