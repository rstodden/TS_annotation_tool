from django.shortcuts import render, redirect, get_object_or_404
import alignment.models
import data.models
from .forms import RatingForm, TransformationForm
from django.contrib.auth.decorators import login_required
from TS_annotation_tool.utils import transformation_dict
import datetime, json
from django.core.serializers.json import DjangoJSONEncoder
import difflib
from data.views import check_url_or_404


@login_required
def rate_pair(request, corpus_id, doc_pair_id, pair_id):
	corpus_tmp, doc_pair_tmp, alignmentpair_tmp = check_url_or_404(user=request.user, corpus_id=corpus_id, doc_pair_id=doc_pair_id, sentence_id=None, pair_id=pair_id)
	if request.method == "POST":
		# redirected from rating.html. save rating of pair here.
		form = RatingForm(request.POST)
		if form.is_valid():
			alignmentpair_tmp.update_or_save_rating(form, request.user, request.session["start"])
			if request.POST.get("transformation"):
				return redirect('rating:select_transformation', corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=alignmentpair_tmp.id)

			elif request.POST.get("next"):
				next_pair = alignmentpair_tmp.next(request.user)
				if next_pair:
					return redirect('rating:rate_pair', corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=next_pair.id)
				else:
					return redirect('overview_per_doc', corpus_id=corpus_id, doc_pair_id=doc_pair_id)
			elif request.POST.get("prev"):
				prev_pair = alignmentpair_tmp.prev(request.user)
				if prev_pair:
					return redirect('rating:rate_pair', corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=prev_pair.id)
				else:
					return redirect('overview_per_doc', corpus_id=corpus_id, doc_pair_id=doc_pair_id)
			else:
				return redirect('overview_per_doc', corpus_id=corpus_id, doc_pair_id=doc_pair_id)
		else:
			print("not valid", form.errors)
	if alignmentpair_tmp.rating.filter(rater=request.user).exists():
		rating_tmp = alignmentpair_tmp.rating.get(rater=request.user)
		form = RatingForm(instance=rating_tmp)
	else:
		form = RatingForm()
	doc_pair_tmp = alignmentpair_tmp.document_pair
	complex_elements = " ".join(alignmentpair_tmp.complex_elements.values_list("original_content", flat=True).order_by("id"))
	simple_elements = " ".join(alignmentpair_tmp.simple_elements.values_list("original_content", flat=True).order_by("id"))
	request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
	return render(request, 'rating/rating.html', {'form': form, 'pair_id': alignmentpair_tmp.id,
												  "doc_pair_id": doc_pair_tmp.id,
												  "doc_simple_url": doc_pair_tmp.simple_document.url,
												  "doc_complex_url": doc_pair_tmp.complex_document.url,
												  "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
												  "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
												  "complex_elements": complex_elements,
												  "simple_elements": simple_elements,
												  "corpus_id": corpus_id,
												  "title": "Rating Annotation - Text Simplification Annotation Tool"
												  })


def get_edit_label(alignmentpair):
	transformation_information = {"simple": dict(), "complex": dict()}
	complex_text_and_ids = alignmentpair.complex_elements.all().order_by("id").values_list("tokens__text", "tokens__id").order_by("tokens__id")
	simple_text_and_ids = alignmentpair.simple_elements.all().order_by("id").values_list("tokens__text", "tokens__id").order_by("tokens__id")

	complex_text = [item[0] for item in complex_text_and_ids]
	complex_ids = [item[1] for item in complex_text_and_ids]
	simple_text = [item[0] for item in simple_text_and_ids]
	simple_ids = [item[1] for item in simple_text_and_ids]
	for edit_type, o_start, o_end, s_start, s_end in difflib.SequenceMatcher(None, complex_text, simple_text).get_opcodes():
		if edit_type == "equal":
			for token_id in complex_ids[o_start:o_end]:
				transformation_information["complex"][token_id] = "copy-label"
			for token_id in simple_ids[s_start:s_end]:
				transformation_information["simple"][token_id] = "copy-label"
		elif edit_type == "replace":
			for token_id in complex_ids[o_start:o_end]:
				transformation_information["complex"][token_id] = "replace-label"
			for token_id in simple_ids[s_start:s_end]:
				transformation_information["simple"][token_id] = "replace-label"
		elif edit_type == "delete":
			for token_id in complex_ids[o_start:o_end]:
				transformation_information["complex"][token_id] = "delete-label"
		elif edit_type == "insert":
			for token_id in simple_ids[s_start:s_end]:
				transformation_information["simple"][token_id] = "add-label"
		else:
			print(edit_type)
	return transformation_information

@login_required
def select_transformations(request, corpus_id, doc_pair_id, pair_id):
	corpus_tmp, doc_pair_tmp, alignmentpair_tmp = check_url_or_404(user=request.user, corpus_id=corpus_id, doc_pair_id=doc_pair_id, sentence_id=None, pair_id=pair_id)
	complex_elements = alignmentpair_tmp.complex_elements.all().order_by("id")
	simple_elements = alignmentpair_tmp.simple_elements.all().order_by("id")
	transformation_dict_obj = None
	complex_token_selected = []
	simple_token_selected = []
	transformation_tmp_id = None
	transformation_selected = None
	transformation_level_selected = None
	transformation_subtransformation_selected = None
	transformation_slot_start = None
	transformation_start_at_beginning = False
	transformation_own_subtransformation_selected = None
	transformation_information = None
	type_form = "show"
	if request.method == "POST":
		form = TransformationForm(request.POST)
		if request.POST.get("add"):
			transformation_dict_obj = transformation_dict
			type_form = "add"
			transformation_information = get_edit_label(alignmentpair_tmp)
			request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
		elif request.POST.get("edit"):
			type_form = "edit"
			transformation_information = get_edit_label(alignmentpair_tmp)
			request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
			transformation_tmp = alignmentpair_tmp.transformation_of_pair.get(id=request.POST.get("edit"), rater=request.user)
			form = TransformationForm(instance=transformation_tmp)
			transformation_dict_obj = transformation_dict
			complex_token_selected = transformation_tmp.complex_token.all()
			simple_token_selected = transformation_tmp.simple_token.all()
			transformation_selected = transformation_tmp.transformation
			transformation_level_selected = transformation_tmp.transformation_level
			transformation_subtransformation_selected = transformation_tmp.sub_transformation
			transformation_start_at_beginning = transformation_tmp.insert_at_beginning
			transformation_slot_start = transformation_tmp.insert_slot_start
			# transformation_own_subtransformation_selected = transformation_tmp.own_subtransformation
			transformation_tmp_id = transformation_tmp.id
		elif request.POST.get("delete"):
			alignmentpair_tmp.delete_transformation(request.POST.get("delete"), request.user)
			type_form = "show"
			# return render(request, 'rating/transformation.html',
			# 			  {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "show"})
		# elif request.POST.get("skip"):
		# 	return redirect('rating:rate_pair', pair_id=alignmentpair_tmp.id)
		# elif request.POST.get("reset"):
		# 	return redirect('overview')
		elif request.POST.get("save"):
			if form.is_valid():
				# own_subtransformation = [value for value in request.POST.getlist('own_subtransformation') if value != ""]
				alignmentpair_tmp.save_transformation(form, request.user, request.session["start"])  # , own_subtransformation)
				type_form = "show"
		elif request.POST.get("save-edit"):
			if form.is_valid():
				# own_subtransformation = [value for value in request.POST.getlist('own_subtransformation') if value != ""]
				transformation_tmp = alignmentpair_tmp.transformation_of_pair.get(id=request.POST.get("save-edit"),
																				  rater=request.user)
				transformation_tmp.edit(form, request.user, request.session["start"])  # , own_subtransformation)
				type_form = "show"
		elif request.POST.get("next"):
			next_pair = alignmentpair_tmp.next(request.user)
			if next_pair:
				return redirect('rating:select_transformation', corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=next_pair.id)
			else:
				return redirect('overview_per_doc', corpus_id=corpus_id, doc_pair_id=doc_pair_id)
		elif request.POST.get("prev"):
			prev_pair = alignmentpair_tmp.prev(request.user)
			if prev_pair:
				return redirect('rating:select_transformation', corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=prev_pair.id)
			else:
				return redirect('overview_per_doc', corpus_id=corpus_id, doc_pair_id=doc_pair_id)
		elif request.POST.get("rate"):
			return redirect('rating:rate_pair', corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=alignmentpair_tmp.id)
		elif request.POST.get("document_overview"):
			return redirect('overview_per_doc', corpus_id=corpus_id, doc_pair_id=doc_pair_id)
		else:
			type_form = "show"
			# return render(request, 'rating/transformation.html',
			# 			  {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "show"})
	else:
		form = TransformationForm()
	return render(request, 'rating/transformation.html', {'form': form,
														  'pair_id': alignmentpair_tmp.id,
														  'simple_elements': simple_elements,
														 "complex_elements": complex_elements,
														  "doc_simple_url": doc_pair_tmp.simple_document.url,
														  "doc_complex_url": doc_pair_tmp.complex_document.url,
														  "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
														  "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
														  'type': type_form,
														  "doc_pair_id": doc_pair_id,
												  		  "corpus_id": corpus_id,
														  "transformations": alignmentpair_tmp.transformation_of_pair.all(),
														  "transformation_dict": transformation_dict_obj,
														  "complex_token_selected": complex_token_selected,
														  "simple_token_selected": simple_token_selected,
														  "transformation_selected": transformation_selected,
														  "transformation_level_selected": transformation_level_selected,
														  "transformation_subtransformation_selected": transformation_subtransformation_selected,
														  # "transformation_own_subtransformation_selected": transformation_own_subtransformation_selected,
														  "transformation_id": transformation_tmp_id,
														  "transformation_slot_start": transformation_slot_start,
														  "transformation_start_at_beginning": transformation_start_at_beginning,
														  "transformation_information": transformation_information,
														  "title": "Transformation Annotation - Text Simplification Annotation Tool"})


# def home(request):
# 	return redirect('overview')



@login_required
def transformations(request, corpus_id, doc_pair_id):
	corpus_tmp, doc_pair_tmp, x = check_url_or_404(user=request.user, corpus_id=corpus_id, doc_pair_id=doc_pair_id, sentence_id=None, pair_id=None)
	first_alignment_pair = doc_pair_tmp.sentence_alignment_pair.filter(annotator=request.user).first()
	if first_alignment_pair:
		return redirect("rating:select_transformation", corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=first_alignment_pair.id)
	else:
		return render(request, 'rating/home.html', {"corpus_id": corpus_id, "doc_pair_id": doc_pair_tmp.id,
													"title": "Annotation - Text Simplification Annotation Tool"
													})


@login_required
def rating(request, corpus_id, doc_pair_id):
	corpus_tmp, doc_pair_tmp, x = check_url_or_404(user=request.user, corpus_id=corpus_id, doc_pair_id=doc_pair_id)
	first_alignment_pair = doc_pair_tmp.sentence_alignment_pair.filter(annotator=request.user).first()
	if first_alignment_pair:
		return redirect("rating:rate_pair", corpus_id=corpus_id, doc_pair_id=doc_pair_id, pair_id=first_alignment_pair.id)
	else:
		return render(request, 'rating/home.html', {"corpus_id": corpus_id, "doc_pair_id": doc_pair_tmp.id,
													"title": "Annotation - Text Simplification Annotation Tool"
													})