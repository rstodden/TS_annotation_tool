from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django_tables2 import SingleTableView
# from django_filters.views import FilterView

import data.models
import TS_annotation_tool.tables

# import django_filters
#
#
# class DocumentFilter(django_filters.FilterSet):
#     class Meta:
#         model = data.models.Document
#         fields = ['level']
#


def home(request):
	return render(request, 'home.html')


class CorpusListOverview(SingleTableView):
	model = data.models.Corpus
	table_class = TS_annotation_tool.tables.OverviewTableCorpus
	template_name = 'overview.html'


class DocumentListOverview(SingleTableView):
	model = data.models.Document
	# table_class = TS_annotation_tool.tables.OverviewTableDocument(data.models.Document.objects.filter(level__in=["a1", "a2", "b2"]))
	table_class = TS_annotation_tool.tables.OverviewTableDocument
	template_name = 'overview.html'
	# filterset_class = DocumentFilter(queryset=data.models.Document.objects.filter(level__in=["a1", "a2", "b2"]))

#
# @login_required
# def overview(request, domain=None, corpus=None):
# 	if corpus:
# 		domains = data.models.Corpus.objects.values_list("domain", flat=True).distinct()
# 		# corpus =request.POST.get("corpus")
# 		corpora = [get_object_or_404(data.models.Corpus, id=corpus)]
# 		documents = corpora[0].simple_documents.filter(annotator=request.user)
# 	elif domain:
# 		# domain = request.POST.get("domain")
# 		domains = data.models.Corpus.objects.filter(annotator=request.user).values_list("domain", flat=True).distinct()
# 		corpora = data.models.Corpus.objects.filter(domain=domain, annotator=request.user)
# 		documents = []
# 	else:
# 		domains = data.models.Corpus.objects.filter(annotator=request.user).values_list("domain", flat=True).distinct()
# 		corpora = []
# 		documents = []
# 	return render(request, 'overview.html', {"documents": documents, "corpora": corpora, "domains": domains})
#



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
		return redirect("alignment:change_alignment", doc_id=doc_tmp.id)
