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
	corpora_to_simplify  = data.models.Corpus.objects.filter(to_simplify=True , document_pairs__annotator=request.user).distinct()
	return render(request, 'overview_corpora.html', {"corpora": corpora, "corpora_to_simplify": corpora_to_simplify,
											 "title": "Corpora Overview - Text Simplification Annotation Tool"})


@login_required
def overview_per_corpus(request, corpus_id):
	#corpora = data.models.Corpus.objects.all()
	corpus = get_object_or_404(data.models.Corpus, id=corpus_id)
	documents_dict = dict()
	# corpus_dict[corpus.name] = documents_dict
	document_pairs = data.models.DocumentPair.objects.all().filter(corpus=corpus, annotator=request.user).order_by("id")
	if document_pairs.exists():
		paginator = Paginator(document_pairs, 10)
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)

		for doc_pair in page_obj.object_list:
			alignments_tmp = alignment.models.Pair.objects.all().filter(document_pair__id=doc_pair.id,
																		origin_annotator=request.user)
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
				transformations = round((transformations / num_alignments) * 100, 2)
				rating = round((rating / num_alignments) * 100, 2)
			else:
				aligned = False
			documents_dict[doc_pair.id] = {"aligned": aligned, "rating": rating,
										   "transformations": transformations}
	else:
		page_obj = None
	return render(request, 'overview_per_corpus.html', {"corpus_name": corpus.name, "corpus_id": corpus_id,
														"corpus_domain": corpus.domain, "document_pairs": page_obj,
														"documents_dict": documents_dict,
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
