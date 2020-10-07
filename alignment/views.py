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
def overview_per_doc(request, doc_id):
	doc_tmp = get_object_or_404(data.models.Document, id=doc_id, annotator=request.user)
	print(doc_tmp.alignments.all())
	if doc_tmp.alignments.filter(origin_annotator=request.user).exists():
		return render(request, 'alignment/overview_per_doc.html', {
			"alignments": doc_tmp.alignments.filter(origin_annotator=request.user),
			"doc_url": doc_tmp.url, "doc_id": doc_tmp.id})
	else:
		# todo link to create alignment
		return render(request, 'alignment/overview_per_doc.html', {
		"error": "There are no alignments assigned to the doc. Please start aligning."})


@login_required
def change_alignment(request, alignment_id):
	print(alignment_id)
	alignment_tmp = get_object_or_404(Pair, id=alignment_id, annotator=request.user)
	doc_tmp = data.models.Document.objects.get(alignments=alignment_id, annotator=request.user)
	if request.method == "POST":
		simple_sents = request.POST.getlist("simple_selected")
		complex_sents = request.POST.getlist("complex_selected")
		alignment_tmp.update_sentences(simple_sents, complex_sents)
		if request.POST["submit"] == "rate":
			return redirect('rating:rate_pair', pair_id=alignment_tmp.id)
		else:
			return redirect('alignment:overview_per_doc', doc_id=doc_tmp.id)

	if doc_tmp.parallel_document:
		simple_elements = doc_tmp.sentences.all()
		parallel_doc = doc_tmp.parallel_document
		complex_elements = parallel_doc.sentences.all()
		return render(request, "alignment/change_alignment.html", {"simple_elements": simple_elements,
																   "complex_elements": complex_elements,
																   "complex_sents": alignment_tmp.complex_element.all(),
																   "simple_sents": alignment_tmp.simple_element.all(),
																   "alignment_id": alignment_id})
	else:
		return redirect('simplification:home', doc_id=doc_tmp.id)


@login_required
def create_alignment(request, doc_id):
	# todo: problem to get doc_id and pair_id

	doc_tmp = get_object_or_404(data.models.Document, id=doc_id, annotator=request.user)
	simple_elements = doc_tmp.sentences.all()
	parallel_doc = doc_tmp.parallel_document
	complex_elements = parallel_doc.sentences.all()
	return render(request, "alignment/change_alignment.html", {"simple_elements": simple_elements,
															   "complex_elements": complex_elements,
															   "complex_sents": [],
															   "simple_sents": [],})



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
