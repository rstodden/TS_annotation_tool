from django.shortcuts import render


def home(request):
	return render(request, 'overview_per_corpus.html', {"title": "Web Scraping - Text Simplification Annotation Tool"})