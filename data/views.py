from django.shortcuts import render, redirect
import data.models
from django.contrib.auth.decorators import user_passes_test
from .forms import UploadFilesForm, UploadAnnotatedFilesForm
from django.contrib.auth.models import User


# @user_passes_test(lambda u: u.is_superuser)
# def home(request):
# 	return render(request, "data/home.html")


@user_passes_test(lambda u: u.is_superuser)
def insert_data(request):
	if request.method == 'POST':
		form_upload = UploadFilesForm(request.POST, request.FILES)
		# if not User.objects.filter(username="automatic"):
		# 	user_machine = User.objects.create_user('automatic', '', 'NoPasswordRequired!')
		# else:
		# 	user_machine = User.objects.get(username="automatic")
		if form_upload.is_valid():
			files = form_upload.cleaned_data["attachments"]
			if data.models.Corpus.objects.filter(name=form_upload.cleaned_data["name"], home_page=form_upload.cleaned_data["home_page"]):
				corpus_tmp = data.models.Corpus.objects.get(name=form_upload.cleaned_data["name"], home_page=form_upload.cleaned_data["home_page"])
				corpus_tmp.add_documents_by_upload(files, form_upload)
			else:
				corpus_tmp = form_upload.save()
				corpus_tmp.add_documents_by_upload(files, form_upload)
			return render(request, 'data/success.html', {"number_alignments": 0})
		return render(request, "data/insertion.html", {"form_upload": form_upload})
	else:
		form_upload = UploadFilesForm()
		return render(request, "data/insertion.html", {"form_upload": form_upload,
													   "title": "Data Upload - Text Simplification Annotation Tool"})


@user_passes_test(lambda u: u.is_superuser)
def insert_annotation(request):
	if request.method == "POST":
		form_upload = UploadFilesForm(request.POST, request.FILES)
	else:
		form_upload = UploadAnnotatedFilesForm()
	return render(request, "data/insertion.html", {"form_upload": form_upload,
												   "title": "Data Upload - Text Simplification Annotation Tool"})
