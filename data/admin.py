from django.contrib import admin
from .models import Sentence, Document, Corpus, Token, DocumentPair  #, Language

admin.site.register(Sentence)
admin.site.register(Document)
admin.site.register(Corpus)
admin.site.register(Token)
admin.site.register(DocumentPair)
# admin.site.register(Language)
