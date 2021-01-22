from django.shortcuts import render, redirect, get_object_or_404
import data.models

# Create your views here.
# simplification of complex texts, such as user generated texts
# add simplification to data model od data app


def home(request):
	return render(request, "simplification/home.html")

def simplify(request, doc_id):
	doc_tmp = get_object_or_404(data.models.Document, id=doc_id)
	# todo: simplification text field
	return render(request, "simplification/home.html", {"title": "Simplification - Text Simplification Annotation Tool"})
