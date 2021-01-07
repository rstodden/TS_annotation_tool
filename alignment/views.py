from django.shortcuts import render, redirect, get_object_or_404
from .models import Pair
import data.models
import alignment.forms
import rating.models
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def home(request):
	return render(request, 'overview.html')


# @login_required
# def change_alignment(request, alignment_id):
# 	alignment_tmp = get_object_or_404(Pair, id=alignment_id, annotator=request.user)
# 	doc_tmp = data.models.Document.objects.get(alignments=alignment_id, annotator=request.user)
# 	if request.method == "POST":
# 		simple_sents = request.POST.getlist("simple_selected")
# 		complex_sents = request.POST.getlist("complex_selected")
# 		alignment_tmp.update_sentences(simple_sents, complex_sents)
# 		if request.POST["submit"] == "rate":
# 			return redirect('rating:rate_pair', pair_id=alignment_tmp.id)
# 		else:
# 			return redirect('overview_per_doc', doc_id=doc_tmp.id)
#
# 	if doc_tmp.parallel_document:
# 		simple_elements = doc_tmp.sentences.all()
# 		parallel_doc = doc_tmp.parallel_document
# 		complex_elements = parallel_doc.sentences.all()
# 		return render(request, "alignment/change_alignment.html", {"simple_elements": simple_elements,
# 																   "complex_elements": complex_elements,
# 																   "complex_sents": alignment_tmp.complex_element.all(),
# 																   "simple_sents": alignment_tmp.simple_element.all(),
# 																   "alignment_id": alignment_id})
# 	else:
# 		return redirect('simplification:home', doc_id=doc_tmp.id)


@login_required
def change_alignment(request, doc_id):
	doc_tmp = get_object_or_404(data.models.Document, id=doc_id, annotator=request.user)
	simple_elements = doc_tmp.sentences.all()
	parallel_doc = doc_tmp.parallel_document
	complex_elements = parallel_doc.sentences.all()
	complex_selected = []
	simple_selected = []
	type_action = "show"
	form = alignment.forms.AlignmentForm()
	if request.method == "POST":
		if request.POST.get("add"):
			type_action = "add"
		elif request.POST.get("edit"):
			type_action = "add"
			pair_tmp = Pair.objects.get(id=request.POST.get("edit"))
			complex_selected = pair_tmp.complex_element.all()
			simple_selected = pair_tmp.simple_element.all()
		elif request.POST.get("delete"):
			doc_tmp.delete_pair(request.POST.get("delete"), request.user)
		elif request.POST.get("rate"):
			return redirect("rating:rate_pair", pair_id=request.POST.get("rate"))
		elif request.POST.get("transformation"):
			return redirect("rating:select_transformation", pair_id=request.POST.get("transformation"))
		elif request.POST.get("save"):
			form = alignment.forms.AlignmentForm(request.POST)
			if form.is_valid():
				print(form.cleaned_data)
				doc_tmp.save_alignment_form_form(form, request.user)
			else:
				print(form.errors)
	return render(request, "alignment/change_alignment.html", {"simple_elements": simple_elements,
															   "complex_elements": complex_elements,
															   "pairs": doc_tmp.alignments.all(),
															   "complex_sents": complex_selected,
															   "simple_sents": simple_selected,
															   "type": type_action,
															   "doc_id": doc_tmp.id, "form":form,
															   })
