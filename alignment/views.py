from django.shortcuts import render, redirect, get_object_or_404
from .models import Pair
import data.models
import alignment.forms
from django.contrib.auth.decorators import login_required
import datetime, json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from data.views import check_url_or_404

# def home(request):
# 	return render(request, 'overview.html')

def check_reading_direction(language):
	if language in ["fa", "ar", "dv", "he", "iw", "ku", "ur"]:
		# specify if language reading direction is right to left
		return "rtl"
	else:
		return "ltr"


def get_value_dict_based_on_pairs(doc_pair_tmp, sentence_pair_tmp, user, form, type_action, start_time=None, duration=None):
	output_dict = {"pairs": alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair_tmp.id, origin_annotator=user).order_by("id"),
				   "type": type_action,
				   "corpus_id": doc_pair_tmp.corpus.id,
				   "doc_simple_url": doc_pair_tmp.simple_document.url,
				   "doc_complex_url": doc_pair_tmp.complex_document.url,
				   "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
				   "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
				   "doc_pair_id": doc_pair_tmp.id,
				   "form": form,
				   "no_alignment_possible": doc_pair_tmp.no_alignment_possible,
				   "simple_language_direction": check_reading_direction(doc_pair_tmp.corpus.language),
				   "complex_language_direction": check_reading_direction("xx"),
				   "simple_elements": data.models.Sentence.objects.filter(document_id=doc_pair_tmp.simple_document.id).order_by("id"),
				   "complex_elements": data.models.Sentence.objects.filter(document_id=doc_pair_tmp.complex_document.id).order_by("id"),
					"simple_annotated_sents": doc_pair_tmp.get_all_simple_annotated_sentences_by_user(user, content=False),
					"complex_annotated_sents": doc_pair_tmp.get_all_complex_annotated_sentences_by_user(user, content=False),
				   "last_simple_item": None,
				   "last_complex_item": None,
				   "notes": "alignment"
	}

	output_dict["complex_sents_content"] = [sent.original_content for sent in output_dict["complex_elements"].all()]
	output_dict["simple_sents_content"] = [sent.original_content for sent in output_dict["simple_elements"].all()]
	if sentence_pair_tmp:
		output_dict["pair_id"] = sentence_pair_tmp.id
	else:
		output_dict["pair_id"] = None
	if type_action == "edit" and sentence_pair_tmp:
		output_dict["complex_sents"] = data.models.Sentence.objects.filter(complex_element=sentence_pair_tmp).order_by("-id")
		output_dict["simple_sents"] = data.models.Sentence.objects.filter(simple_element=sentence_pair_tmp).order_by("-id")
		output_dict["last_simple_item"] = output_dict["simple_sents"][0]
		output_dict["last_complex_item"] = output_dict["complex_sents"][0]
	# elif type_action == "add":
	# 	output_dict["last_simple_item"] = output_dict["simple_sents"][0]
	# 	output_dict["last_complex_item"] = output_dict["complex_sents"][0]
	elif type_action == "show":
		output_dict["complex_sents"] = []
		output_dict["simple_sents"] = []
		if output_dict["simple_annotated_sents"] and output_dict["complex_annotated_sents"]:
			output_dict["last_simple_item"], output_dict["last_complex_item"] = sorted(output_dict["simple_annotated_sents"], key=lambda x: x.id, reverse=True)[0], \
												  sorted(output_dict["complex_annotated_sents"], key=lambda x: x.id, reverse=True)[0]
		else:
			output_dict["last_simple_item"], output_dict["last_complex_item"] = None, None
	elif type_action == "save":
		output_dict["last_simple_item"], output_dict["last_complex_item"] = sentence_pair_tmp.save_sentence_alignment_from_form(form.cleaned_data["simple_element"],
															form.cleaned_data["complex_element"],
															[user], doc_pair_tmp, start_time=start_time)
		output_dict["simple_annotated_sents"] = doc_pair_tmp.get_all_simple_annotated_sentences_by_user(user, content=False)
		output_dict["complex_annotated_sents"] = doc_pair_tmp.get_all_complex_annotated_sentences_by_user(user, content=False)
	elif type_action == "save-edit":
		output_dict["last_simple_item"], output_dict["last_complex_item"] = sentence_pair_tmp.save_sentence_alignment_from_form(
			form.cleaned_data["simple_element"],
			form.cleaned_data["complex_element"],
			[user], doc_pair_tmp, start_time, duration=duration)
		output_dict["simple_annotated_sents"] = doc_pair_tmp.get_all_simple_annotated_sentences_by_user(user, content=False)
		output_dict["complex_annotated_sents"] = doc_pair_tmp.get_all_complex_annotated_sentences_by_user(user, content=False)
	elif type_action == "save-failed":
		if "complex_element" in form.cleaned_data.keys() and form.cleaned_data["complex_element"]:
			output_dict["complex_sents"] = form.cleaned_data["complex_element"]
			output_dict["last_complex_item"] = form.cleaned_data["complex_element"]
		elif sentence_pair_tmp:
				output_dict["complex_sents"] = data.models.Sentence.objects.filter(complex_element=sentence_pair_tmp).order_by("-id")
				output_dict["last_complex_item"] = output_dict["complex_sents"][0]
		if "simple_element" in form.cleaned_data.keys() and form.cleaned_data["simple_element"]:
			output_dict["simple_sents"] = form.cleaned_data["simple_element"]
			output_dict["last_simple_item"] = form.cleaned_data["simple_element"]
		elif sentence_pair_tmp:
			output_dict["simple_sents"] = data.models.Sentence.objects.filter(simple_element=sentence_pair_tmp).order_by("-id")
			output_dict["last_simple_item"] = output_dict["simple_sents"][0]

	return output_dict


@login_required
def save_alignment(request, corpus_id, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user, corpus__id=corpus_id)
	form = alignment.forms.AlignmentForm(request.POST)
	if form.is_valid():
		if request.POST.get("save-edit"):
			type_action = "save-edit"
			sentence_pair_tmp = get_object_or_404(alignment.models.Pair, id=request.POST.get("save-edit"), annotator=request.user,
												  document_pair__id=doc_pair_id)
			duration = sentence_pair_tmp.duration
			sentence_pair_tmp.delete()
			messages.add_message(request, messages.SUCCESS, 'Successfully edited.')
		else:
			sentence_pair_tmp = alignment.models.Pair()
			type_action = "save"
			duration = None
			messages.add_message(request, messages.SUCCESS, 'Sucessfully saved.')
	else:
		messages.add_message(request, messages.ERROR, 'Saving failed.')
		if request.POST.get("save-edit"):
			sentence_pair_tmp = get_object_or_404(alignment.models.Pair, id=request.POST.get("save-edit"),
												  annotator=request.user,
												  document_pair__id=doc_pair_id)
		else:
			sentence_pair_tmp = None
		type_action = "save-failed"
		output_params = get_value_dict_based_on_pairs(doc_pair_tmp, sentence_pair_tmp, request.user, form, type_action,
													  start_time=request.session["start"], duration=None)
		output_params["type"] = "add"
		return render(request, "alignment/change_alignment.html", output_params)
	output_params = get_value_dict_based_on_pairs(doc_pair_tmp, sentence_pair_tmp, request.user, form, type_action, start_time=request.session["start"], duration=duration)
	output_params["title"] = "Alignment - Text Simplification Annotation Tool"
	output_params["type"] = "add"
	return render(request, "alignment/change_alignment.html", output_params)


@login_required
def add_alignment(request, corpus_id, doc_pair_id):
	type_action = "add"
	request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user, corpus__id=corpus_id)
	form = alignment.forms.AlignmentForm()
	output_params = get_value_dict_based_on_pairs(doc_pair_tmp, None, request.user, form, type_action)
	output_params["title"] = "Add Alignment - Text Simplification Annotation Tool"
	return render(request, "alignment/change_alignment.html", output_params)


@login_required
def delete_alignment(request, corpus_id, doc_pair_id, pair_id):
	corpus_tmp, doc_pair_tmp, sentence_pair_tmp = check_url_or_404(user=request.user, corpus_id=corpus_id,
															  doc_pair_id=doc_pair_id, pair_id=pair_id)

	sentence_pair_tmp.delete()
	messages.add_message(request, messages.SUCCESS, 'Sucessfully deleted.')
	return redirect("alignment:change_alignment", corpus_id=corpus_id, doc_pair_id=doc_pair_id)


@login_required
def edit_alignment_of_sent(request, corpus_id, doc_pair_id, sent_id):
	corpus_tmp, doc_pair_tmp, sentence_tmp = check_url_or_404(user=request.user, corpus_id=corpus_id,
																   doc_pair_id=doc_pair_id, sentence_id=sent_id)
	if sentence_tmp.simple_element.filter(annotator=request.user):
		sentence_pair_tmp = sentence_tmp.simple_element.get(annotator=request.user)
		return redirect("alignment:edit_alignment", corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=sentence_pair_tmp.id)
	elif sentence_tmp.complex_element.filter(annotator=request.user):
			sentence_pair_tmp = sentence_tmp.complex_element.get(annotator=request.user)
			return redirect("alignment:edit_alignment", corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=sentence_pair_tmp.id)

	else:
		return redirect("alignment:edit_alignment", corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=None)


@login_required
def edit_alignment(request, corpus_id, doc_pair_id, pair_id):
	form = alignment.forms.AlignmentForm()
	type_action = "edit"
	request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
	corpus_tmp, doc_pair_tmp, sentence_pair_tmp = check_url_or_404(user=request.user, corpus_id=corpus_id,
																   doc_pair_id=doc_pair_id, pair_id=pair_id)
	output_params = get_value_dict_based_on_pairs(doc_pair_tmp, sentence_pair_tmp, request.user, form, type_action)
	output_params["title"] = "Edit Alignment - Text Simplification Annotation Tool"
	return render(request, "alignment/change_alignment.html", output_params)


@login_required
def show_alignments(request, corpus_id, doc_pair_id):
	form = alignment.forms.AlignmentForm()
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user, corpus__id=corpus_id)
	output_params = get_value_dict_based_on_pairs(doc_pair_tmp, None, request.user, form, "show")
	output_params["title"] = "Alignment - Text Simplification Annotation Tool"
	return render(request, "alignment/change_alignment.html", output_params)


def alignment_not_possible(request, corpus_id, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user, corpus__id=corpus_id)
	if doc_pair_tmp.no_alignment_possible:
		doc_pair_tmp.no_alignment_possible = False
	else:
		doc_pair_tmp.no_alignment_possible = True
	doc_pair_tmp.save(update_fields=['no_alignment_possible'])
	messages.add_message(request, messages.INFO, 'Option of Alignment changed.')
	return redirect("overview_per_corpus", corpus_id=corpus_id)



# @login_required
# def change_alignment(request, doc_pair_id):
# 	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user)
# 	simple_elements = data.models.Sentence.objects.filter(document_id=doc_pair_tmp.simple_document.id).order_by("id")
# 	complex_elements = data.models.Sentence.objects.filter(document_id=doc_pair_tmp.complex_document.id).order_by("id")
# 	simple_annotated_sents = doc_pair_tmp.get_all_simple_annotated_sentences_by_user(request.user, content=False)
# 	complex_annotated_sents = doc_pair_tmp.get_all_complex_annotated_sentences_by_user(request.user, content=False)
# 	complex_selected = []
# 	simple_selected = []
# 	type_action = "show"
# 	form = alignment.forms.AlignmentForm()
# 	sentence_pair_tmp_id = None
# 	last_simple_item, last_complex_item = None, None
# 	if simple_annotated_sents and complex_annotated_sents:
# 		last_simple_item, last_complex_item = sorted(simple_annotated_sents, key=lambda x: x.id, reverse=True)[0], sorted(complex_annotated_sents, key=lambda x: x.id, reverse=True)[0]
# 	if request.method == "POST":
# 		if request.POST.get("add"):
# 			type_action = "add"
# 			request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
# 		elif request.POST.get("edit"):
# 			type_action = "edit"
# 			request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
# 			sentence_pair_tmp = Pair.objects.get(id=request.POST.get("edit"), annotator=request.user)
# 			complex_selected = data.models.Sentence.objects.filter(complex_element=sentence_pair_tmp).order_by("-id")
# 			simple_selected = data.models.Sentence.objects.filter(simple_element=sentence_pair_tmp).order_by("-id")
# 			sentence_pair_tmp_id = sentence_pair_tmp.id
# 			last_simple_item, last_complex_item = simple_selected[0], complex_selected[0]
# 		elif request.POST.get("delete"):
# 			sentence_pair_tmp = Pair.objects.get(id=request.POST.get("delete"), annotator=request.user)
# 			sentence_pair_tmp.delete()
# 		# elif request.POST.get("rate"):
# 		# 	return redirect("rating:rate_pair", doc_pair_id=doc_pair_id, pair_id=request.POST.get("rate"))
# 		# elif request.POST.get("transformation"):
# 		# 	return redirect("rating:select_transformation", doc_pair_id=doc_pair_id, pair_id=request.POST.get("transformation"))
# 		elif request.POST.get("save-edit"):
# 			type_action = "add"
# 			form = alignment.forms.AlignmentForm(request.POST)
# 			if form.is_valid():
# 				sentence_pair_tmp = Pair.objects.get(id=request.POST.get("save-edit"), annotator=request.user)
# 				duration = sentence_pair_tmp.duration
# 				sentence_pair_tmp.delete()
# 				sentence_pair_tmp = alignment.models.Pair()
# 				last_simple_item, last_complex_item = sentence_pair_tmp.save_sentence_alignment_from_form(form.cleaned_data["simple_element"],
# 																	form.cleaned_data["complex_element"],
# 																	[request.user], doc_pair_tmp, request.session["start"], duration=duration)
# 			else:
# 				print(form.errors)
# 		elif request.POST.get("save"):
# 			type_action = "add"
# 			form = alignment.forms.AlignmentForm(request.POST)
# 			if form.is_valid():
# 				sentence_pair_tmp = alignment.models.Pair()
# 				last_simple_item, last_complex_item = sentence_pair_tmp.save_sentence_alignment_from_form(form.cleaned_data["simple_element"],
# 																	form.cleaned_data["complex_element"],
# 																	[request.user], doc_pair_tmp, start_time=request.session["start"])
# 				simple_annotated_sents = doc_pair_tmp.get_all_simple_annotated_sentences_by_user(request.user, content=False)
# 				complex_annotated_sents = doc_pair_tmp.get_all_complex_annotated_sentences_by_user(request.user, content=False)
#
# 			else:
# 				print(form.errors)
# 		elif request.POST.get("sentence-problem"):
# 			return redirect("data:sentence_problem", sentence_id=request.POST.get("sentence-problem"))
# 		elif request.POST.get("not-possible"):
# 			doc_pair_tmp.no_alignment_possible = request.POST.get("not-possible")
# 			doc_pair_tmp.save(update_fields=['no_alignment_possible'])
# 			return redirect("overview_per_corpus", corpus_id=doc_pair_tmp.corpus.id)
# 		else:
# 			last_simple_item, last_complex_item = None, None
# 	return render(request, "alignment/change_alignment.html", {"simple_elements": simple_elements,
# 															   "complex_elements": complex_elements,
# 															   "pairs": alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair_tmp.id, origin_annotator=request.user).order_by("id"),
# 															   "complex_sents": complex_selected,
# 															   "simple_sents": simple_selected,
# 															   "complex_sents_content": [sent.original_content for sent in complex_elements.all()],
# 															   "simple_sents_content": [sent.original_content for sent in simple_elements.all()],
# 															   "simple_annotated_sents" : simple_annotated_sents,
# 															   "complex_annotated_sents": complex_annotated_sents,
# 															   "type": type_action,
# 															   "corpus_id": doc_pair_tmp.corpus.id,
# 															   "doc_simple_url": doc_pair_tmp.simple_document.url,
# 															   "doc_complex_url": doc_pair_tmp.complex_document.url,
# 															   "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
# 															   "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
# 															   "doc_pair_id": doc_pair_tmp.id,
# 																"form": form, "pair_tmp_id": sentence_pair_tmp_id,
# 															   "title": "Alignment - Text Simplification Annotation Tool",
# 															   "last_simple_item": last_simple_item,
# 															   "last_complex_item": last_complex_item,
# 															   "no_alignment_possible": doc_pair_tmp.no_alignment_possible,
# 															   "simple_language_direction": check_reading_direction(doc_pair_tmp.corpus.language),
# 															   "complex_language_direction": check_reading_direction("xx"),
# 															   })
