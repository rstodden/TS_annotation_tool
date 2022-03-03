from django.shortcuts import render, redirect, get_object_or_404
import data.models, alignment.models
from django.contrib.auth.decorators import user_passes_test

import web_scraping.models
from .forms import UploadFilesForm, UploadAnnotatedFilesForm, SentenceProblemForm, UploadWithCrawlerForm
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# @user_passes_test(lambda u: u.is_superuser)
# def home(request):
# 	return render(request, "data/home.html")


@user_passes_test(lambda u: u.is_superuser)
def insert_data(request):
	return render(request, "data/insertion.html")


@user_passes_test(lambda u: u.is_superuser)
def insert_data_by_plain_text(request):
	if request.method == 'POST':
		form_upload = UploadFilesForm(request.POST, request.FILES)
		# if not User.objects.filter(username="automatic"):
		# 	user_machine = User.objects.create_user('automatic', '', 'NoPasswordRequired!')
		# else:
		# 	user_machine = User.objects.get(username="automatic")
		if form_upload.is_valid():
			print(form_upload.cleaned_data)
			files = form_upload.cleaned_data["attachments"]
			# print(files, [dict(file) for file in files], form_upload.cleaned_data["annotator"])
			if data.models.Corpus.objects.filter(name=form_upload.cleaned_data["name"], home_page=form_upload.cleaned_data["home_page"]):
				corpus_tmp = data.models.Corpus.objects.get(name=form_upload.cleaned_data["name"], home_page=form_upload.cleaned_data["home_page"])
				corpus_tmp.add_documents_by_upload(files, form_upload.cleaned_data)
			else:
				corpus_tmp = form_upload.save()
				corpus_tmp.add_documents_by_upload(files, form_upload.cleaned_data)
			return render(request, 'data/success.html', {"number_alignments": 0})
		return render(request, "data/insertion_plain.html", {"form_upload": form_upload})
	else:
		form_upload = UploadFilesForm()
		return render(request, "data/insertion_plain.html", {"form_upload": form_upload,
													   "title": "Data Upload - Text Simplification Annotation Tool"})


@user_passes_test(lambda u: u.is_superuser)
def insert_data_by_url(request):
	if request.method == 'POST':
		form_upload = UploadWithCrawlerForm(request.POST, request.FILES)
		if form_upload.is_valid():
			print(form_upload.cleaned_data)
			file = form_upload.cleaned_data["file"]
			print(file)
			crawler = web_scraping.models.Crawler()
			crawler.crawl_data_to_db(file)
			return render(request, 'data/success.html', {"number_alignments": 0})
		return render(request, "data/insertion_web.html", {"form_upload": form_upload})
	else:
		form_upload = UploadWithCrawlerForm()
		return render(request, "data/insertion_web.html", {"form_upload": form_upload,
													   "title": "Data Upload - Text Simplification Annotation Tool"})


@user_passes_test(lambda u: u.is_superuser)
def insert_annotation(request):
	if request.method == "POST":
		form_upload = UploadFilesForm(request.POST, request.FILES)
	else:
		form_upload = UploadAnnotatedFilesForm()
	return render(request, "data/insertion.html", {"form_upload": form_upload,
												   "title": "Data Upload - Text Simplification Annotation Tool"})


@login_required
def sentence_problem(request, sentence_id):
	sentence_tmp = get_object_or_404(data.models.Sentence, id=sentence_id)
	sentence_content = sentence_tmp.original_content
	if request.method == "POST":
		form = SentenceProblemForm(request.POST, instance=sentence_tmp)
		if form.is_valid():
			sentence_tmp = form.save()
			if sentence_tmp.document.simple_document.all():
				doc_pair_id = sentence_tmp.document.simple_document.values_list("id", flat=True)[0]
			elif sentence_tmp.document.complex_document.all():
				doc_pair_id = sentence_tmp.document.complex_document.values_list("id", flat=True)[0]
			else:
				return render(request, "data/sentence_problem.html",
						  {"form": form, "sentence_content": sentence_content})
			return redirect("alignment:change_alignment", doc_pair_id=doc_pair_id)
	else:
		form = SentenceProblemForm()
	return render(request, "data/sentence_problem.html", {"form": form, "sentence_content": sentence_content})
