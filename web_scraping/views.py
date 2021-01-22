from django.shortcuts import render


def home(request):
	return render(request, 'overview.html', {"title": "Web Scraping - Text Simplification Annotation Tool"})