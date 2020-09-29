from django.shortcuts import render, redirect, get_object_or_404
from .models import AlignmentPair, Assessment
from .forms import RatingForm, RegisterForm, PairForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .views_admin import *


def update_rating(alignmentpair_tmp, form, rater):
	alignmentpair_tmp.assessment.simplicity = form.cleaned_data["simplicity"]
	alignmentpair_tmp.assessment.grammaticality = form.cleaned_data["grammaticality"]
	alignmentpair_tmp.assessment.meaning_preservation = form.cleaned_data["meaning_preservation"]
	alignmentpair_tmp.assessment.comment = form.cleaned_data["comment"]
	alignmentpair_tmp.assessment.transaction = form.cleaned_data["transaction"]
	alignmentpair_tmp.assessment.certainty = form.cleaned_data["certainty"]
	alignmentpair_tmp.manually_checked = True
	alignmentpair_tmp.assessment.rater_id = rater.id
	alignmentpair_tmp.assessment.save()
	alignmentpair_tmp.save()
	return alignmentpair_tmp

def save_rating(alignmentpair_tmp, form, rater):
	alignmentpair_tmp.assessment = form.save(commit=False)
	alignmentpair_tmp.assessment.rater_id = rater.id
	alignmentpair_tmp.manually_checked = True
	alignmentpair_tmp.assessment.save()
	alignmentpair_tmp.save()
	return alignmentpair_tmp


@login_required
def pairs_list(request):
	pairs = AlignmentPair.objects.filter(annotator_id=request.user)
	if request.method == "POST":
		# redirected from rating.html. save rating of pair here.
		form = RatingForm(request.POST)
		if form.is_valid():
			alignmentpair_tmp = AlignmentPair.objects.get(id=form.cleaned_data["pair_id"], annotator_id=request.user)
			if alignmentpair_tmp.assessment:
				# update rating values
				alignmentpair_tmp = update_rating(alignmentpair_tmp, form, request.user)
			else:
				# create rating values
				alignmentpair_tmp = save_rating(alignmentpair_tmp, form, request.user)
			return render(request, 'alignment/pairs_list.html', {"success": "Rating successfully saved.", "pairs": pairs})
		else:
			print("not valid", form.errors)
	if not pairs:
		return render(request, 'alignment/pairs_list.html', {"error": "There are no pairs assigned to you. Please ask the admin to get new pairs."})

	return render(request, 'alignment/pairs_list.html', {"pairs": pairs})


@login_required
def rate_pair(request):
	if request.method == "POST":
		# redirected from pairs_list.html call pair to rate here.
		form = PairForm(request.POST)
		if form.is_valid():
			pair_id = form.cleaned_data["pair_id"]
			alignmentpair_tmp = AlignmentPair.objects.get(id=pair_id, annotator_id=request.user)
			if alignmentpair_tmp.assessment:
				form = RatingForm(initial={'grammaticality': alignmentpair_tmp.assessment.grammaticality,
									   'meaning_preservation': alignmentpair_tmp.assessment.meaning_preservation,
									   'simplicity': alignmentpair_tmp.assessment.simplicity,
									   'transaction': alignmentpair_tmp.assessment.transaction,
									   'certainty': alignmentpair_tmp.assessment.certainty,
									   'comment': alignmentpair_tmp.assessment.comment})
			else:
				form = RatingForm()
			return render(request, 'alignment/rating.html', {'form': form, 'alignmentpair': alignmentpair_tmp})
		else:
			print("redirect with wrong pair")
			return redirect('pairs_list')

	else:
		print("redirect without pair, e.g., after refreshing rate_pair site")
		return redirect('pairs_list')



def register(request):
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
		username = request.POST['username']
		password = request.POST['password1']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect("/home", {})
		else:
			render(request, "registration/register.html", {"form": form, "error": "Something went wrong."})
	else:
		form = RegisterForm()

	return render(request, "registration/register.html", {"form": form})


def home(request):
	return render(request, 'alignment/home.html')


