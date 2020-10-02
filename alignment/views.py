from django.shortcuts import render, redirect, get_object_or_404
from .models import Pair
import data.models
import alignment.forms
from django.contrib.auth.decorators import login_required


def home(request):
	return render(request, 'alignment/home.html')


@login_required
def overview(request):
	documents = data.models.Document.objects.filter(annotator=request.user)
	if not documents:
		return render(request, 'alignment/overview.html', {"error": "There are no documents assigned to you. Please ask the admin to get new documents."})
	return render(request, 'alignment/overview.html', {"documents": documents})


@login_required
def change_alignment(request, doc_id):
	doc_tmp = get_object_or_404(data.models.Document, id=doc_id, annotator=request.user)
	if request.method == "POST":
		form = alignment.forms.AlignmentForm(request.POST)
		if form.is_valid():
			list_alignments = doc_tmp.align_sentences(form.cleaned_data["simple_element"], form.cleaned_data["complex_element"], request.user)
			# todo: rate the newly generated pairs ?
			return redirect('rating:pairs_list')
		else:
			print("form not ok")
	if doc_tmp.alignments.filter(origin_annotator=request.user).exists():
		alignment_tmp = doc_tmp.alignments.filter(origin_annotator=request.user)[0]
		form = alignment.forms.AlignmentForm(initial={'simple_element': alignment_tmp.alignments.simple_element.all(),
													   'complex_element': alignment_tmp.alignments.complex_element.all()
													   })
	else:
		form = alignment.forms.AlignmentForm()
	return render(request, "alignment/change_alignment.html", {"form": form, "doc": doc_tmp})

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
