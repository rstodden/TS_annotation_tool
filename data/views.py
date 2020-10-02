from django.shortcuts import render, redirect
import data.models
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from .forms import UploadFileForm
import csv, io
import pandas as pd
import alignment.models
from django.core.files.base import ContentFile


def home(request):
	return render(request, "data/home.html")


@user_passes_test(lambda u: u.is_superuser)
def insert_data(request):
	if request.method == 'POST':
		form_upload = UploadFileForm(request.POST, request.FILES)
		if form_upload.is_valid():
			# selected_users = form_upload.cleaned_data["users"]
			uploaded_file = request.FILES['file']
			new_corpus = data.models.Corpus()
			new_corpus.fill_with_manually_aligned(uploaded_file)
			file_url = new_corpus.path
			# alignments assinment to users missing
			new_corpus.save()
			return render(request, 'data/success.html', {'file_url': file_url, "number_alignments": 0})
		return render(request, "data/insertion.html", {"form_upload": form_upload })
	else:
		form_upload = UploadFileForm()
		return render(request, "data/insertion.html", {"form_upload": form_upload })


