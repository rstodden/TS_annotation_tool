from django.shortcuts import render, redirect, get_object_or_404
from .models import Rating
import alignment.models
from .forms import RatingForm, PairForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
# from .views_admin import *
import datetime


@login_required
def pairs_list(request):
	pairs = alignment.models.Pair.objects.filter(annotator=request.user)
	if request.method == "POST":
		# redirected from rating.html. save rating of pair here.
		form = RatingForm(request.POST)
		if form.is_valid():
			alignmentpair_tmp = alignment.models.Pair.objects.get(id=form.cleaned_data["pair_id"], annotator=request.user)
			alignmentpair_tmp.update_or_save_rating(form, request.user)
			#
			# if alignmentpair_tmp.rating.filter(rater=request.user):
			# 	# update rating values
			# 	# alignmentpair_tmp.rating.updated_at
			# 	alignmentpair_tmp.update_or_save_rating(form, request.user)
			# else:
			# 	# create rating values
			# 	alignmentpair_tmp.save_rating(form, request.user)
			return render(request, 'rating/pairs_list.html', {"success": "Rating successfully saved.", "pairs": pairs})
		else:
			print("not valid", form.errors)
	if not pairs:
		return render(request, 'rating/pairs_list.html', {"error": "There are no pairs assigned to you. Please ask the admin to get new pairs."})

	return render(request, 'rating/pairs_list.html', {"pairs": pairs})


@login_required
def rate_pair(request):
	if request.method == "POST":
		# redirected from pairs_list.html call pair to rate here.
		form = PairForm(request.POST)
		if form.is_valid():
			pair_id = form.cleaned_data["pair_id"]
			alignmentpair_tmp = alignment.models.Pair.objects.get(id=pair_id, annotator=request.user)
			# print(alignmentpair_tmp, alignmentpair_tmp.simple_element, alignmentpair_tmp.simple_element.all().values_list("original_content", flat=True))
			rating_tmp = alignmentpair_tmp.rating.filter(rater=request.user)
			print(rating_tmp)
			if rating_tmp.exists():
				form = RatingForm(initial={'grammaticality': rating_tmp[0].grammaticality,
										   'meaning_preservation': rating_tmp[0].meaning_preservation,
										   'simplicity': rating_tmp[0].simplicity,
										   'transaction': rating_tmp[0].transaction,
										   'certainty': rating_tmp[0].certainty,
										   'comment': rating_tmp[0].comment})
			else:
				form = RatingForm()

			return render(request, 'rating/rating.html', {'form': form, 'alignmentpair': alignmentpair_tmp})
		else:
			print("redirect with wrong pair")
			return redirect('pairs_list')

	else:
		print("redirect without pair, e.g., after refreshing rate_pair site")
		return redirect('pairs_list')



def home(request):
	return render(request, 'rating/home.html')


