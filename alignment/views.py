from django.shortcuts import render, redirect, get_object_or_404
from .models import Pair
from django.contrib.auth.decorators import login_required


def home(request):
	return render(request, 'alignment/home.html')

def change_alignment(request, pair_identifier):
	return render(request, "alignment/change_alignment.html")

from django.views.generic import ListView

#
# class PairsListView(ListView):
#     model = Pair
#     template_name = 'alignment/overview.html'
#
# @login_required
# def pairs_list(request):
# 	pairs = Pair.objects.filter(annotator=request.user)
# 	if not pairs:
# 		return render(request, 'rating/pairs_list.html', {"error": "There are no pairs assigned to you. Please ask the admin to get new pairs."})
#
# 	return render(request, 'rating/pairs_list.html', {"pairs": pairs})
#
#
