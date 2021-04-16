from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import data.models
import alignment.models


def home(request):
	return render(request, 'home.html')

@login_required
def overview_all_corpora(request):
	corpora = list(set(data.models.Corpus.objects.filter(document_pairs__annotator=request.user)))
	corpora_to_simplify  = data.models.Corpus.objects.filter(to_simplify=True)
	return render(request, 'overview_corpora.html', {"corpora": corpora, "corpora_to_simplify": corpora_to_simplify,
											 "title": "Corpora Overview - Text Simplification Annotation Tool"})


@login_required
def overview_per_corpus(request, corpus_id):
	#corpora = data.models.Corpus.objects.all()
	corpus = get_object_or_404(data.models.Corpus, id=corpus_id)
	corpus_dict = dict()
	title = ""
	#for corpus in corpora:
	documents_dict = dict()
	for doc_pair in data.models.DocumentPair.objects.all().filter(corpus=corpus, annotator=request.user):
		alignments_tmp = alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair.id, origin_annotator=request.user)
		rating = 0
		transformations = 0
		if alignments_tmp.exists():
			aligned = True
			num_alignments = len(alignments_tmp.all())
			for pair in alignments_tmp.all():
				if pair.rating.exists():
					rating += 1
				if pair.transformation_of_pair.exists():
					transformations += 1
			transformations = round((transformations/num_alignments)*100, 2)
			rating = round((rating/num_alignments)*100, 2)
		else:
			aligned = False

		if doc_pair.complex_document:
			complex_level = doc_pair.complex_document.level
			title = doc_pair.complex_document.title
		else:
			complex_level = None
		if doc_pair.simple_document:
			simple_level = doc_pair.simple_document.level
			title = doc_pair.simple_document.title
		else:
			simple_level = None
		documents_dict[doc_pair.id] = {"domain": corpus.domain, "simple_level": simple_level,
									   "complex_level": complex_level, "aligned": aligned, "rating": rating,
									   "transformations": transformations, "title": title,
									   "last_change": doc_pair.last_changes, "no_alignment_possible": doc_pair.no_alignment_possible}
	corpus_dict[corpus.name] = documents_dict
	return render(request, 'overview_per_corpus.html', {"corpora": corpus_dict, "corpus_id": corpus_id,
											 "title": "Corpus Overview - Text Simplification Annotation Tool"})


@login_required
def overview_per_doc(request, doc_pair_id):
	doc_pair_tmp = get_object_or_404(data.models.DocumentPair, id=doc_pair_id, annotator=request.user)
	alignments_tmp = alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair_tmp.id, origin_annotator=request.user).order_by("id")
	if doc_pair_tmp.corpus.to_simplify:
		return redirect("simplification:simplify", doc_pair_id=doc_pair_tmp.id)
	if alignments_tmp.exists():
		paginator = Paginator(alignments_tmp, 10)
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)
		return render(request, 'overview_per_doc.html', {
			"alignments": page_obj,
			"domain": doc_pair_tmp.simple_document.domain,
			"doc_simple_url": doc_pair_tmp.simple_document.url,
			"doc_complex_url": doc_pair_tmp.complex_document.url,
			"doc_pair_id": doc_pair_tmp.id,
			"doc_title": doc_pair_tmp.simple_document.title,
			"corpus_id": doc_pair_tmp.corpus.id,
			"title": "Document Overview - Text Simplification Annotation Tool"})
	else:
		return redirect("alignment:change_alignment", doc_pair_id=doc_pair_tmp.id)
