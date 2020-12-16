from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

import data.models


def home(request):
	return render(request, 'home.html')


@login_required
def overview(request, domain=None, corpus=None):
	if corpus:
		domains = data.models.Corpus.objects.values_list("domain", flat=True).distinct()
		# corpus =request.POST.get("corpus")
		corpora = [get_object_or_404(data.models.Corpus, id=corpus)]
		documents = corpora[0].simple_documents.all()
	elif domain:
		# domain = request.POST.get("domain")
		domains = data.models.Corpus.objects.values_list("domain", flat=True).distinct()
		corpora = data.models.Corpus.objects.filter(domain=domain)
		documents = []
	else:
		domains = data.models.Corpus.objects.values_list("domain", flat=True).distinct()
		corpora = []
		documents = []
	return render(request, 'overview.html', {"documents": documents, "corpora": corpora, "domains": domains})




@login_required
def overview_per_doc(request, doc_id):
	doc_tmp = get_object_or_404(data.models.Document, id=doc_id, annotator=request.user)
	alignments_tmp = doc_tmp.alignments.filter(origin_annotator=request.user)
	if alignments_tmp.exists():
		paginator = Paginator(alignments_tmp, 10)
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)
		return render(request, 'overview_per_doc.html', {
			"alignments": page_obj,
			"doc_url": doc_tmp.url, "doc_id": doc_tmp.id})
	else:
		# todo link to create alignment
		return render(request, 'overview_per_doc.html', {
		"error": "There are no alignments assigned to the doc. Please start aligning."})
