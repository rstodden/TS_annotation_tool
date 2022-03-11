from django.shortcuts import render, redirect, get_object_or_404
import data.models
import alignment.models
import simplification.forms
import json, datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from muss.muss.simplify import simplify_sentences
from settings_annotation.config_simplification import simplification_model, load_simplification_model
from django.contrib import messages

# Create your views here.
# simplification of complex texts, such as user generated texts
# add simplification to data model od data app


# @login_required
# def home(request):
# 	return render(request, "simplification/home.html")


def auto_simplify(source_sentences, language):
	if language in["en", "es", "fr"]:
		model_name = 'muss_'+language+'_mined'
		# return simplify_sentences(source_sentences, model_name)
		return source_sentences[0][::-1]
	else:
		assert Exception("No simplification model in your language is available.")
		return None


def get_output_dict(corpus_id, doc_pair_tmp, sentence_pair_tmp, type_action, form, user, start=None, duration=None):
	complex_doc_tmp = doc_pair_tmp.complex_document
	if sentence_pair_tmp:
		sentence_pair_tmp_id = sentence_pair_tmp.id
	else:
		sentence_pair_tmp_id = None
	output_dict = {"doc_pair_id": doc_pair_tmp.id,
				   "doc_complex_url": complex_doc_tmp.url,
				   "doc_complex_access_date": complex_doc_tmp.access_date,
				   "complex_elements": data.models.Sentence.objects.filter(document=complex_doc_tmp).order_by("id"),
				   "type": type_action, "form": form, "corpus_id": corpus_id,
				   "pair_tmp_id": sentence_pair_tmp_id,
				   "complex_sents": [],
				   "simple_text": "",
				   "simplification_model_name": simplification_model,
				   "suggestion_simplification": "",
				   "last_complex_item": None,
				   "load_simplification_model": load_simplification_model,
				   }
	if type_action == "edit":
		output_dict["complex_sents"] = data.models.Sentence.objects.filter(complex_element=sentence_pair_tmp).order_by("-id")
		output_dict["simple_text"] = " ".join(data.models.Sentence.objects.filter(simple_element=sentence_pair_tmp).order_by("id").values_list("original_content", flat=True))
		output_dict["type"] = "edit"
	output_dict["pairs"] = alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair_tmp.id, origin_annotator=user).order_by("id")
	output_dict["complex_simplified"] = output_dict["pairs"].all().values_list("complex_elements", flat=True)
	return output_dict


@login_required
def show_simplification(request, corpus_id, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user, corpus__id=corpus_id)
	form = simplification.forms.SimplificationForm()
	output_dict = get_output_dict(corpus_id, doc_pair_tmp, None, "show", form, request.user)
	return render(request, "simplification/simplification.html", output_dict)


@login_required
def delete_simplification(request, corpus_id, doc_pair_id, pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user, corpus__id=corpus_id)
	sentence_pair_tmp = get_object_or_404(alignment.models.Pair, id=pair_id, annotator=request.user, document_pair_id=doc_pair_id)
	sentence_pair_tmp.delete()
	messages.add_message(request, messages.SUCCESS, 'Sucessfully deleted.')
	return redirect("simplification:simplify", corpus_id=corpus_id, doc_pair_id=doc_pair_id)


@login_required
def add_simplification(request, corpus_id, doc_pair_id):
	type_action = "add"
	request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user,
									 corpus__id=corpus_id)
	form = simplification.forms.SimplificationForm()
	output_dict = get_output_dict(corpus_id, doc_pair_tmp, None, type_action, form, request.user, request.session["start"])
	return render(request, "simplification/simplification.html", output_dict)


@login_required
def edit_simplification(request, corpus_id, doc_pair_id, pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user,
									 corpus__id=corpus_id)
	sentence_pair_tmp = get_object_or_404(alignment.models.Pair, id=pair_id, annotator=request.user, document_pair_id=doc_pair_id)
	type_action = "edit"
	form = simplification.forms.SimplificationForm()
	request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
	output_dict = get_output_dict(corpus_id, doc_pair_tmp, sentence_pair_tmp, type_action, form, request.user, request.session["start"])
	return render(request, "simplification/simplification.html", output_dict)


def get_simplification(request, corpus_id, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user,  corpus__id=corpus_id)
	form = simplification.forms.SimplificationForm(request.POST)
	output_params = get_output_dict(corpus_id, doc_pair_tmp, None, "add", form, request.user,
									start=None, duration=None)
	if request.POST.get("complex_element"):
		id_list = request.POST.getlist("complex_element")
		simple_text = request.POST.get("simple_text")
		output_params["simple_text"] = simple_text
		complex_selected = data.models.Sentence.objects.filter(id__in=id_list).order_by("-id")
		output_params["complex_sents"] = complex_selected
		complex_selected_text = data.models.Sentence.objects.filter(id__in=id_list).values_list("original_content", flat=True)
		output_params["suggestion_simplification"] = " ".join(auto_simplify(complex_selected_text, doc_pair_tmp.corpus.language))
	else:
		messages.add_message(request, messages.ERROR, 'No complex sentence was selected. Please try again.')
	return render(request, "simplification/simplification.html", output_params)


def get_simple_doc(doc_pair_tmp, complex_doc_tmp):
	if doc_pair_tmp.simple_document:
		simple_doc_tmp = doc_pair_tmp.simple_document
	else:
		simple_doc_tmp = data.models.Document(title=complex_doc_tmp.title + " (manually simplified)", url="", level="a2", manually_simplified=True)
		simple_doc_tmp.save()
		doc_pair_tmp.simple_document = simple_doc_tmp
		doc_pair_tmp.save()
	return simple_doc_tmp


@login_required
def save_simplification(request, corpus_id, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user, corpus__id=corpus_id)
	complex_doc_tmp = doc_pair_tmp.complex_document
	form = simplification.forms.SimplificationForm(request.POST)
	print("save")
	if request.POST.get("suggestion"):
		return get_simplification(request, corpus_id, doc_pair_id)
	if form.is_valid():
		print("valid", request.POST.get("save-edit"))
		if request.POST.get("save-edit"):
			sentence_pair_tmp = alignment.models.Pair.objects.get(id=request.POST.get("save-edit"), annotator=request.user)
			duration = sentence_pair_tmp.duration
			sentence_pair_tmp.delete()
		else:
			duration = datetime.timedelta()
		sentence_pair_tmp = alignment.models.Pair(type="translated")
		nlp = data.models.get_spacy_model(doc_pair_tmp.corpus.language)
		sents = list(nlp(form.cleaned_data["simple_text"].strip()).sents)
		number_sentences = len([sent for sent in sents])
		simple_doc_tmp = get_simple_doc(doc_pair_tmp, complex_doc_tmp)
		new_sentences = simple_doc_tmp.add_sentences(sents, par_nr=-1, language_level=simple_doc_tmp.level,
													 selected_license=complex_doc_tmp.license,
													 number_sentences=number_sentences, author=request.user)
		simple_doc_tmp.save()
		simple_element = data.models.Sentence.objects.filter(id__in=new_sentences)
		last_simple_item, last_complex_item = sentence_pair_tmp.save_sentence_alignment_from_form(simple_element, form.cleaned_data["complex_element"], [request.user], doc_pair_tmp, start_time=request.session["start"], duration=duration)
		output_params = get_output_dict(corpus_id, doc_pair_tmp, sentence_pair_tmp, "save", form, request.user,
										start=request.session["start"], duration=duration)
		messages.add_message(request, messages.SUCCESS, 'Successfully edited/saved.')
	else:
		output_params = get_output_dict(corpus_id, doc_pair_tmp, None, "add", form, request.user,
										start=None, duration=None)
		messages.add_message(request, messages.ERROR, 'Saving failed.')
	output_params["title"] = "Alignment - Text Simplification Annotation Tool"
	output_params["type"] = "add"
	return render(request, "simplification/simplification.html", output_params)
#
# @login_required
# def simplify(request, corpus_id, doc_pair_id):
# 	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id)
# 	complex_doc_tmp = doc_pair_tmp.complex_document
# 	sentence_pair_tmp_id = None
# 	if doc_pair_tmp.simple_document:
# 		simple_doc_tmp = doc_pair_tmp.simple_document
# 	else:
# 		simple_doc_tmp = data.models.Document(title=complex_doc_tmp.title + " (manually simplified)", url="", level="a2", manually_simplified=True)
# 		simple_doc_tmp.save()
# 		doc_pair_tmp.simple_document = simple_doc_tmp
# 		doc_pair_tmp.save()
# 	complex_elements = data.models.Sentence.objects.filter(document=complex_doc_tmp).order_by("id")
# 	type_action = "show"
# 	complex_selected = []
# 	simple_text = ""
# 	suggestion = ""
# 	simplification_model_name = simplification_model
# 	last_complex_item = None
# 	form = simplification.forms.SimplificationForm()
# 	if request.POST.get("add"):
# 		type_action = "add"
# 		request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
# 	elif request.POST.get("edit"):
# 		type_action = "edit"
# 		request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
# 		sentence_pair_tmp = alignment.models.Pair.objects.get(id=request.POST.get("edit"), annotator=request.user)
# 		sentence_pair_tmp_id = sentence_pair_tmp.id
#
# 		complex_selected = data.models.Sentence.objects.filter(complex_element=sentence_pair_tmp).order_by("-id")
# 		simple_text = " ".join(data.models.Sentence.objects.filter(simple_element=sentence_pair_tmp).order_by("id").values_list("original_content", flat=True))
# 	elif request.POST.get("save-edit"):
# 		type_action = "add"
# 		form = simplification.forms.SimplificationForm(request.POST)
# 		if form.is_valid():
# 			sentence_pair_tmp = alignment.models.Pair.objects.get(id=request.POST.get("save-edit"), annotator=request.user)
# 			duration = sentence_pair_tmp.duration
# 			sentence_pair_tmp.delete()
# 			sentence_pair_tmp = alignment.models.Pair(type="translated")
# 			nlp = data.models.get_spacy_model(doc_pair_tmp.corpus.language)
# 			number_sentences = len([sent for sent in nlp(form.cleaned_data["simple_text"].strip()).sents])
# 			new_sentences = simple_doc_tmp.add_sentences(nlp(form.cleaned_data["simple_text"].strip()).sents, par_nr=-1,
# 														 language_level=simple_doc_tmp.level, selected_license=complex_doc_tmp.license,
# 														 number_sentences=number_sentences, author=request.user)
# 			simple_doc_tmp.save()
# 			simple_element = data.models.Sentence.objects.filter(id__in=new_sentences)
# 			last_simple_item, last_complex_item = sentence_pair_tmp.save_sentence_alignment_from_form(simple_element, form.cleaned_data["complex_element"], [request.user], doc_pair_tmp, request.session["start"], duration=duration)
# 	elif request.POST.get("delete"):
# 		sentence_pair_tmp = alignment.models.Pair.objects.get(id=request.POST.get("delete"), annotator=request.user)
# 		sentence_pair_tmp.delete()
# 	elif request.POST.get("save"):
# 		type_action = "add"
# 		form = simplification.forms.SimplificationForm(request.POST)
# 		if form.is_valid():
# 			nlp = data.models.get_spacy_model(doc_pair_tmp.corpus.language)
# 			number_sentences = len([sent for sent in nlp(form.cleaned_data["simple_text"].strip()).sents])
# 			new_sentences = simple_doc_tmp.add_sentences(nlp(form.cleaned_data["simple_text"].strip()).sents, par_nr=-1, language_level=simple_doc_tmp.level, selected_license=complex_doc_tmp.license, number_sentences=number_sentences, author=request.user)
# 			simple_doc_tmp.save()
# 			sentence_pair_tmp = alignment.models.Pair(type="translated")
# 			# last_simple_item, last_complex_item
# 			simple_element = data.models.Sentence.objects.filter(id__in=new_sentences)
# 			last_simple_item, last_complex_item = sentence_pair_tmp.save_sentence_alignment_from_form(simple_element, form.cleaned_data["complex_element"], [request.user], doc_pair_tmp, start_time=request.session["start"])
# 	elif request.POST.get("suggestion") and load_simplification_model:
# 		type_action = "edit"
# 		print(request.POST)
# 		if request.POST.get("complex_element"):
# 			id_list = request.POST.getlist("complex_element")
# 			simple_text = request.POST.get("simple_text")
# 			complex_selected = data.models.Sentence.objects.filter(id__in=id_list).order_by("-id")
# 			complex_selected_text = data.models.Sentence.objects.filter(id__in=id_list).values_list("original_content", flat=True)
# 			suggestion = " ".join(auto_simplify(complex_selected_text, doc_pair_tmp.corpus.language))
# 		else:
# 			suggestion = "Error: No complex sentence was selected. Please try again."
# 	aligned_pairs = alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair_id,
# 															   origin_annotator=request.user).order_by("id")
# 	complex_simplified = aligned_pairs.all().values_list("complex_elements", flat=True)
# 	return render(request, "simplification/simplification.html", {"title": "Simplification - Text Simplification Annotation Tool",
# 																  "doc_pair_id": doc_pair_id,
# 																  # "doc_simple_url": doc_pair_tmp.simple_document.url,
# 																  "doc_complex_url": complex_doc_tmp.url,
# 																  # "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
# 																  "doc_complex_access_date": complex_doc_tmp.access_date,
# 																  "complex_elements": complex_elements,
# 																  # "simple_elements": simple_elements,
# 																  "type": type_action,
# 																  "form": form,
# 																  "corpus_id": corpus_id,
# 																  "pairs": aligned_pairs,
# 																  "complex_simplified": complex_simplified,
# 																  "pair_tmp_id": sentence_pair_tmp_id,
# 																  "complex_sents": complex_selected,
# 																  "simple_text": simple_text,
# 																  "simplification_model_name": simplification_model_name,
# 																  "suggestion_simplification": suggestion,
# 																  "last_complex_item": last_complex_item,
# 																  "load_simplification_model": load_simplification_model,
# 																  })
