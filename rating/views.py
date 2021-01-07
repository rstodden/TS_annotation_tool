from django.shortcuts import render, redirect, get_object_or_404
from .models import Rating
from django.views.generic import ListView
import alignment.models
from .forms import RatingForm, TransformationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import transformation_dict
# from django_tables2 import SingleTableView
# from .tables import PairTable
# from django_sortable.helpers import sortable_helper

# class PairsListView(SingleTableView):
# 	model = alignment.models.Pair
# 	table_class = PairTable
# 	template_name = 'rating/pairs_list.html'


# @login_required
# def pairs_list(request):
# 	pairs = alignment.models.Pair.objects.filter(annotator=request.user).order_by("pair_identifier")
# 	paginator = Paginator(pairs, 10)
#
# 	page_number = request.GET.get('page')
# 	page_obj = paginator.get_page(page_number)
# 	#sortable_pairs = sortable_helper(request, pairs)
# 	if not pairs:
# 		return render(request, 'overview.html', {"error": "There are no pairs assigned to you. Please ask the admin to get new pairs."})
#
# 	return render(request, 'overview.html', {"page_obj": page_obj})


def tokenize_dummy(alignmentpair_tmp):
	for sentence in alignmentpair_tmp.complex_element.all():
		if not sentence.tokens.exists():
			sentence.tokenize()
	for sentence in alignmentpair_tmp.simple_element.all():
		if not sentence.tokens.exists():
			sentence.tokenize()
	return 1

@login_required
def rate_pair(request, pair_id):
	alignmentpair_tmp = get_object_or_404(alignment.models.Pair, id=pair_id, annotator=request.user)
	tokenize_dummy(alignmentpair_tmp)
	if request.method == "POST":
		# redirected from rating.html. save rating of pair here.
		form = RatingForm(request.POST)
		if form.is_valid():
			# todo save rating
			alignmentpair_tmp.update_or_save_rating(form, request.user)
			if request.POST.get("transformation"):
				return redirect('rating:select_transformation', pair_id=alignmentpair_tmp.id)
			else:
				return redirect('overview')
		else:
			print("not valid", form.errors)
	if alignmentpair_tmp.rating.filter(rater=request.user).exists():
		rating_tmp = alignmentpair_tmp.rating.get(rater=request.user)
		form = RatingForm(instance=rating_tmp)
	else:
		form = RatingForm()
	return render(request, 'rating/rating.html', {'form': form, 'alignmentpair': alignmentpair_tmp})


@login_required
def select_transformation(request, pair_id):
	alignmentpair_tmp = get_object_or_404(alignment.models.Pair, id=pair_id, annotator=request.user)
	tokenize_dummy(alignmentpair_tmp)
	if request.method == "POST":
		form = TransformationForm(request.POST)
		if request.POST.get("add"):
			return render(request, 'rating/transformation.html',
						  {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "add", "transformation_dict": transformation_dict})
		# redirected from rating.html. save rating of pair here.
		elif request.POST.get("delete"):
			alignmentpair_tmp.delete_transformation(request.POST.get("delete"), request.user)
			return render(request, 'rating/transformation.html',
						  {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "show"})
		# elif request.POST.get("skip"):
		# 	return redirect('rating:rate_pair', pair_id=alignmentpair_tmp.id)
		# elif request.POST.get("reset"):
		# 	return redirect('overview')
		elif request.POST.get("save"):
			alignmentpair_tmp.save_transformation(form, request.user)
			return render(request, 'rating/transformation.html',
						  {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "show"})
		elif request.POST.get("rate"):
			return redirect('rating:rate_pair', pair_id=alignmentpair_tmp.id)
		else:
			return render(request, 'rating/transformation.html',
						  {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "show"})
	else:
		form = TransformationForm()
		return render(request, 'rating/transformation.html', {'form': form, 'alignmentpair': alignmentpair_tmp, 'type': "show"})


def home(request):
	return redirect('overview')


