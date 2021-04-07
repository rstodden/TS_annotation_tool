from django.shortcuts import render, redirect, get_object_or_404
import alignment.models
from .forms import RatingForm, TransformationForm
from django.contrib.auth.decorators import login_required
from TS_annotation_tool.utils import transformation_dict
import datetime, json
from django.core.serializers.json import DjangoJSONEncoder


@login_required
def rate_pair(request, doc_pair_id, pair_id):
	alignmentpair_tmp = get_object_or_404(alignment.models.Pair, id=pair_id, annotator=request.user, document_pair_id=doc_pair_id)
	if request.method == "POST":
		# redirected from rating.html. save rating of pair here.
		form = RatingForm(request.POST)
		if form.is_valid():
			alignmentpair_tmp.update_or_save_rating(form, request.user, request.session["start"])
			if request.POST.get("transformation"):
				return redirect('rating:select_transformation', doc_pair_id=doc_pair_id, pair_id=alignmentpair_tmp.id)

			elif request.POST.get("next"):
				next_pair = alignmentpair_tmp.next(request.user)
				if next_pair:
					return redirect('rating:rate_pair', doc_pair_id=doc_pair_id, pair_id=next_pair.id)
				else:
					return redirect('overview_per_doc', doc_pair_id=doc_pair_id)
			elif request.POST.get("prev"):
				prev_pair = alignmentpair_tmp.prev(request.user)
				if prev_pair:
					return redirect('rating:rate_pair', doc_pair_id=doc_pair_id, pair_id=prev_pair.id)
				else:
					return redirect('overview_per_doc', doc_pair_id=doc_pair_id)
			else:
				return redirect('overview_per_doc', doc_pair_id=doc_pair_id)
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
	return render(request, 'rating/rating.html', {'form': form, 'alignmentpair_id': alignmentpair_tmp.id,
												  "doc_pair_id": doc_pair_tmp.id,
												  "doc_simple_url": doc_pair_tmp.simple_document.url,
												  "doc_complex_url": doc_pair_tmp.complex_document.url,
												  "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
												  "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
												  "complex_elements": complex_elements,
												  "simple_elements": simple_elements,
												  "corpus_id": doc_pair_tmp.corpus.id,
												  "title": "Rating Annotation - Text Simplification Annotation Tool"
												  })


@login_required
def select_transformation(request, doc_pair_id, pair_id):
	alignmentpair_tmp = get_object_or_404(alignment.models.Pair, id=pair_id, annotator=request.user, document_pair_id=doc_pair_id)
	doc_pair_tmp = alignmentpair_tmp.document_pair
	complex_elements = alignmentpair_tmp.complex_elements.all().order_by("id")
	simple_elements = alignmentpair_tmp.simple_elements.all().order_by("id")
	transformation_dict_obj = None
	type_form = "show"
	if request.method == "POST":
		form = TransformationForm(request.POST)
		if request.POST.get("add"):
			transformation_dict_obj = transformation_dict
			type_form = "add"
			request.session["start"] = json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder)
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
			alignmentpair_tmp.save_transformation(form, request.user, request.session["start"])
			type_form = "show"
			# return render(request, 'rating/transformation.html',
			# 			  {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "show"})
		elif request.POST.get("next"):
			next_pair = alignmentpair_tmp.next(request.user)
			if next_pair:
				return redirect('rating:select_transformation', doc_pair_id=doc_pair_id, pair_id=next_pair.id)
			else:
				return redirect('overview_per_doc', doc_pair_id=doc_pair_id)
		elif request.POST.get("prev"):
			prev_pair = alignmentpair_tmp.prev(request.user)
			if prev_pair:
				return redirect('rating:select_transformation', doc_pair_id=doc_pair_id, pair_id=prev_pair.id)
			else:
				return redirect('overview_per_doc', doc_pair_id=doc_pair_id)
		elif request.POST.get("rate"):
			return redirect('rating:rate_pair', doc_pair_id=doc_pair_id, pair_id=alignmentpair_tmp.id)
		elif request.POST.get("document_overview"):
			return redirect('overview_per_doc', doc_pair_id=doc_pair_id)
		else:
			type_form = "show"
			# return render(request, 'rating/transformation.html',
			# 			  {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "show"})
	else:
		form = TransformationForm()
	return render(request, 'rating/transformation.html', {'form': form,
														  'alignmentpair_id': alignmentpair_tmp.id,
														  'simple_elements': simple_elements,
														 "complex_elements": complex_elements,
														  "doc_simple_url": doc_pair_tmp.simple_document.url,
														  "doc_complex_url": doc_pair_tmp.complex_document.url,
														  "doc_simple_access_date": doc_pair_tmp.simple_document.access_date,
														  "doc_complex_access_date": doc_pair_tmp.complex_document.access_date,
														  'type': type_form,
														  "doc_pair_id": doc_pair_id,
												  		  "corpus_id": doc_pair_tmp.corpus.id,
														  "transformations": alignmentpair_tmp.transformation_of_pair.all(),
														  "transformation_dict": transformation_dict_obj,
														  "title": "Transformation Annotation - Text Simplification Annotation Tool"})


# def home(request):
# 	return redirect('overview')
