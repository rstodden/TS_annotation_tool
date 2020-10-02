from django.shortcuts import render, redirect, get_object_or_404
from .models import Rating
from django.views.generic import ListView
import alignment.models
from .forms import RatingForm
from django.contrib.auth.decorators import login_required
# from django_tables2 import SingleTableView
# from .tables import PairTable
# from django_sortable.helpers import sortable_helper

# class PairsListView(SingleTableView):
# 	model = alignment.models.Pair
# 	table_class = PairTable
# 	template_name = 'rating/pairs_list.html'


@login_required
def pairs_list(request):
	pairs = alignment.models.Pair.objects.filter(annotator=request.user)
	#sortable_pairs = sortable_helper(request, pairs)
	if not pairs:
		return render(request, 'rating/pairs_list.html', {"error": "There are no pairs assigned to you. Please ask the admin to get new pairs."})

	return render(request, 'rating/pairs_list.html', {"pairs": pairs})


@login_required
def rate_pair(request, pair_identifier):
	alignmentpair_tmp = alignment.models.Pair.objects.get(pair_identifier=pair_identifier, annotator=request.user)
	print(pair_identifier)
	if request.method == "POST":
		# redirected from rating.html. save rating of pair here.
		form = RatingForm(request.POST)
		if form.is_valid():
			alignmentpair_tmp = alignment.models.Pair.objects.get(pair_identifier=pair_identifier,
																  annotator=request.user)
			alignmentpair_tmp.update_or_save_rating(form, request.user)

			return redirect('rating:pairs_list')
		else:
			print("not valid", form.errors)
	if alignmentpair_tmp.rating.filter(rater=request.user).exists():
		rating_tmp = alignmentpair_tmp.rating.filter(rater=request.user)[0]
		form = RatingForm(initial={'grammaticality': rating_tmp.grammaticality,
								   'meaning_preservation': rating_tmp.meaning_preservation,
								   'simplicity': rating_tmp.simplicity,
								   'transaction': rating_tmp.transaction,
								   'certainty': rating_tmp.certainty,
								   'comment': rating_tmp.comment})
	else:
		form = RatingForm()
	return render(request, 'rating/rating.html', {'form': form, 'alignmentpair': alignmentpair_tmp})


def home(request):
	return render(request, 'rating/home.html')


