from django.shortcuts import render, redirect, get_object_or_404
from .models import Pair
import data.models
import alignment.forms
import rating.models
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def home(request):
	return render(request, 'overview.html')


@login_required
def change_alignment(request, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user)
	simple_elements = data.models.Sentence.objects.filter(document_id=doc_pair_tmp.simple_document.id)
	complex_elements = data.models.Sentence.objects.filter(document_id=doc_pair_tmp.complex_document.id)
	complex_selected = []
	simple_selected = []
	type_action = "show"
	# form = alignment.forms.AlignmentForm()
	if request.method == "POST":
		if request.POST.get("add"):
			type_action = "add"
		elif request.POST.get("edit"):
			type_action = "add"
			sentence_pair_tmp = Pair.objects.get(id=request.POST.get("edit"), annotator=request.user)
			complex_selected = data.models.Sentence.objects.filter(complex_element=sentence_pair_tmp)
			simple_selected = data.models.Sentence.objects.filter(simple_element=sentence_pair_tmp)
			print(complex_selected, simple_selected)
			# todo: remove previous element and keep only new element. how to get the old id? only the new id is sent.
			# todo: call also delete function
		elif request.POST.get("delete"):
			sentence_pair_tmp = Pair.objects.get(id=request.POST.get("delete"), annotator=request.user)
			sentence_pair_tmp.delete()
		elif request.POST.get("rate"):
			return redirect("rating:rate_pair", pair_id=request.POST.get("rate"))
		elif request.POST.get("transformation"):
			return redirect("rating:select_transformation", pair_id=request.POST.get("transformation"))
		elif request.POST.get("save"):
			# form = alignment.forms.AlignmentForm(request.POST)
			if request.POST.getlist("simple_element") and request.POST.getlist("complex_element"):
				sentence_pair_tmp = alignment.models.Pair()
				sentence_pair_tmp.save_sentence_alignment_from_form(request.POST.getlist("simple_element"),
																	request.POST.getlist("complex_element"),
																	request.user, doc_pair_tmp)
			# if form.is_valid():
			# 	print(form.cleaned_data)
			# 	sentence_pair_tmp = alignment.models.Pair()
			# 	sentence_pair_tmp.save_sentence_alignment_from_form(form, request.user, doc_pair_tmp)
			# else:
			# 	print(form.errors)
			print(request.POST.get("simple_element"), request.POST.getlist("simple_element"))
			print(request.POST.get("complex_element"), request.POST.getlist("complex_element"))
				# todo: correct ids of sentence saved but not accepted in form. WHY?
	return render(request, "alignment/change_alignment.html", {"simple_elements": simple_elements,
															   "complex_elements": complex_elements,
															   "pairs": alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair_tmp.id, origin_annotator=request.user),
															   "complex_sents": complex_selected,
															   "simple_sents": simple_selected,
															   "type": type_action,
															   "doc_simple_url": doc_pair_tmp.simple_document.url,
															   "doc_complex_url": doc_pair_tmp.complex_document.url,
															   "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
															   "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
															   "doc_pair_id": doc_pair_tmp.id
															# , "form":form,
															   })
