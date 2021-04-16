from django.shortcuts import render, redirect, get_object_or_404
from .models import Pair
import data.models
import alignment.forms
from django.contrib.auth.decorators import login_required
import datetime, json
from django.core.serializers.json import DjangoJSONEncoder

# def home(request):
# 	return render(request, 'overview.html')


@login_required
def change_alignment(request, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user)
	simple_elements = data.models.Sentence.objects.filter(document_id=doc_pair_tmp.simple_document.id).order_by("id")
	complex_elements = data.models.Sentence.objects.filter(document_id=doc_pair_tmp.complex_document.id).order_by("id")
	simple_annotated_sents = doc_pair_tmp.get_all_simple_annotated_sentences_by_user(request.user, content=False)
	complex_annotated_sents = doc_pair_tmp.get_all_complex_annotated_sentences_by_user(request.user, content=False)
	complex_selected = []
	simple_selected = []
	type_action = "show"
	form = alignment.forms.AlignmentForm()
	sentence_pair_tmp_id = None
	last_simple_item, last_complex_item = None, None
	if simple_annotated_sents and complex_annotated_sents:
		last_simple_item, last_complex_item = sorted(simple_annotated_sents, key=lambda x: x.id, reverse=True)[0], sorted(complex_annotated_sents, key=lambda x: x.id, reverse=True)[0]
	if request.method == "POST":
		if request.POST.get("add"):
			type_action = "add"
			request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
		elif request.POST.get("edit"):
			type_action = "edit"
			request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
			sentence_pair_tmp = Pair.objects.get(id=request.POST.get("edit"), annotator=request.user)
			complex_selected = data.models.Sentence.objects.filter(complex_element=sentence_pair_tmp).order_by("-id")
			simple_selected = data.models.Sentence.objects.filter(simple_element=sentence_pair_tmp).order_by("-id")
			sentence_pair_tmp_id = sentence_pair_tmp.id
			last_simple_item, last_complex_item = simple_selected[0], complex_selected[0]
		elif request.POST.get("delete"):
			sentence_pair_tmp = Pair.objects.get(id=request.POST.get("delete"), annotator=request.user)
			sentence_pair_tmp.delete()
		elif request.POST.get("rate"):
			return redirect("rating:rate_pair", doc_pair_id=doc_pair_id, pair_id=request.POST.get("rate"))
		elif request.POST.get("transformation"):
			return redirect("rating:select_transformation", doc_pair_id=doc_pair_id, pair_id=request.POST.get("transformation"))
		elif request.POST.get("save-edit"):
			type_action = "add"
			form = alignment.forms.AlignmentForm(request.POST)
			if form.is_valid():
				sentence_pair_tmp = Pair.objects.get(id=request.POST.get("save-edit"), annotator=request.user)
				duration = sentence_pair_tmp.duration
				sentence_pair_tmp.delete()
				sentence_pair_tmp = alignment.models.Pair()
				last_simple_item, last_complex_item = sentence_pair_tmp.save_sentence_alignment_from_form(form.cleaned_data["simple_element"],
																	form.cleaned_data["complex_element"],
																	request.user, doc_pair_tmp, request.session["start"], duration=duration)
			else:
				print(form.errors)
		elif request.POST.get("save"):
			type_action = "add"
			form = alignment.forms.AlignmentForm(request.POST)
			if form.is_valid():
				sentence_pair_tmp = alignment.models.Pair()
				last_simple_item, last_complex_item = sentence_pair_tmp.save_sentence_alignment_from_form(form.cleaned_data["simple_element"],
																	form.cleaned_data["complex_element"],
																	request.user, doc_pair_tmp, start_time=request.session["start"])
				simple_annotated_sents = doc_pair_tmp.get_all_simple_annotated_sentences_by_user(request.user, content=False)
				complex_annotated_sents = doc_pair_tmp.get_all_complex_annotated_sentences_by_user(request.user, content=False)

			else:
				print(form.errors)
		elif request.POST.get("sentence-problem"):
			return redirect("data:sentence_problem", sentence_id=request.POST.get("sentence-problem"))
		elif request.POST.get("not-possible"):
			doc_pair_tmp.no_alignment_possible = request.POST.get("not-possible")
			doc_pair_tmp.save(update_fields=['no_alignment_possible'])
			return redirect("overview_per_corpus", corpus_id=doc_pair_tmp.corpus)
		else:
			last_simple_item, last_complex_item = None, None
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
															   "corpus_id": doc_pair_tmp.corpus.id,
															   "doc_simple_url": doc_pair_tmp.simple_document.url,
															   "doc_complex_url": doc_pair_tmp.complex_document.url,
															   "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
															   "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
															   "doc_pair_id": doc_pair_tmp.id,
																"form": form, "pair_tmp_id": sentence_pair_tmp_id,
															   "title": "Alignment - Text Simplification Annotation Tool",
															   "last_simple_item": last_simple_item,
															   "last_complex_item": last_complex_item,
															   "no_alignment_possible": doc_pair_tmp.no_alignment_possible
															   })
