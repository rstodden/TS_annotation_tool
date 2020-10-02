from django.shortcuts import render

# Create your views here.
# simplification of complex texts, such as user generated texts
# add simplification to data model od data app


def home(request):
	return render(request, "simplification/home.html")
