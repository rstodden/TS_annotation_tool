from django.contrib import admin
from .models import Sentence, Document, Corpus

admin.site.register(Sentence)
admin.site.register(Document)
admin.site.register(Corpus)
