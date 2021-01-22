from django.shortcuts import render, redirect, get_object_or_404
from .models import Pair
import data.models
import alignment.forms
from django.contrib.auth.decorators import login_required


# def home(request):
# 	return render(request, 'overview.html')


@login_required
def change_alignment(request, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user)
	simple_elements = data.models.Sentence.objects.filter(document_id=doc_pair_tmp.simple_document.id).order_by("id")
	complex_elements = data.models.Sentence.objects.filter(document_id=doc_pair_tmp.complex_document.id).order_by("id")
	complex_selected = []
	simple_selected = []
	type_action = "show"
	form = alignment.forms.AlignmentForm()
	sentence_pair_tmp_id = None
	if request.method == "POST":
		if request.POST.get("add"):
			type_action = "add"
		elif request.POST.get("edit"):
			type_action = "edit"
			sentence_pair_tmp = Pair.objects.get(id=request.POST.get("edit"), annotator=request.user)
			complex_selected = data.models.Sentence.objects.filter(complex_element=sentence_pair_tmp).order_by("id")
			simple_selected = data.models.Sentence.objects.filter(simple_element=sentence_pair_tmp).order_by("id")
			sentence_pair_tmp_id = sentence_pair_tmp.id
		elif request.POST.get("delete"):
			sentence_pair_tmp = Pair.objects.get(id=request.POST.get("delete"), annotator=request.user)
			sentence_pair_tmp.delete()
		elif request.POST.get("rate"):
			return redirect("rating:rate_pair", pair_id=request.POST.get("rate"))
		elif request.POST.get("transformation"):
			return redirect("rating:select_transformation", pair_id=request.POST.get("transformation"))
		elif request.POST.get("save-edit"):
			form = alignment.forms.AlignmentForm(request.POST)
			if form.is_valid():
				sentence_pair_tmp = Pair.objects.get(id=request.POST.get("save-edit"), annotator=request.user)
				sentence_pair_tmp.delete()
				sentence_pair_tmp = alignment.models.Pair()
				sentence_pair_tmp.save_sentence_alignment_from_form(form.cleaned_data["simple_element"],
																	form.cleaned_data["complex_element"],
																	request.user, doc_pair_tmp)
			else:
				print(form.errors)
		elif request.POST.get("save"):
			form = alignment.forms.AlignmentForm(request.POST)
			if form.is_valid():
				sentence_pair_tmp = alignment.models.Pair()
				sentence_pair_tmp.save_sentence_alignment_from_form(form.cleaned_data["simple_element"],
																	form.cleaned_data["complex_element"],
																	request.user, doc_pair_tmp)
			else:
				print(form.errors)
	simple_annotated_sents = doc_pair_tmp.get_all_simple_annotated_sentences_by_user(request.user, content=False)
	complex_annotated_sents = doc_pair_tmp.get_all_complex_annotated_sentences_by_user(request.user, content=False)
	return render(request, "alignment/change_alignment.html", {"simple_elements": simple_elements,
															   "complex_elements": complex_elements,
															   "pairs": alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair_tmp.id, origin_annotator=request.user).order_by("id"),
															   "complex_sents": complex_selected,
															   "simple_sents": simple_selected,
															   "complex_sents_content": [sent.original_content for sent in complex_elements.all()],
															   "simple_sents_content": [sent.original_content for sent in simple_elements.all()],
															   "simple_annotated_sents" : simple_annotated_sents,
															   "complex_annotated_sents": complex_annotated_sents,
															   "type": type_action,
															   "doc_simple_url": doc_pair_tmp.simple_document.url,
															   "doc_complex_url": doc_pair_tmp.complex_document.url,
															   "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
															   "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
															   "doc_pair_id": doc_pair_tmp.id,
																"form": form, "pair_tmp_id": sentence_pair_tmp_id,
															   "title": "Alignment - Text Simplification Annotation Tool"
															   })
