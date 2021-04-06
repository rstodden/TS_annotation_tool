from django.shortcuts import render, redirect, get_object_or_404
import data.models
import alignment.models

# Create your views here.
# simplification of complex texts, such as user generated texts
# add simplification to data model od data app


def home(request):
	return render(request, "simplification/home.html")

def simplify(request, doc_pair_id):
	doc_tmp = get_object_or_404(data.models.Document, id=doc_pair_id)
	# todo: simplification text field
	return render(request, "simplification/simplification.html", {"title": "Simplification - Text Simplification Annotation Tool",
																  # "doc_pair_id": doc_pair_id,
																  # "doc_simple_url": doc_pair_tmp.simple_document.url,
																  "doc_complex_url": doc_tmp.url,
																  # "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
																  "doc_complex_access_date": doc_tmp.access_date,
																  "complex_elements": doc_tmp.sentences.all(),
																  # "simple_elements": simple_elements,

																  })
