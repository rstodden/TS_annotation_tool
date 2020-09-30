from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
# from .views_admin import *


def register(request):
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
		username = request.POST['username']
		password = request.POST['password1']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect("home")
		else:
			render(request, "registration/register.html", {"form": form, "error": "Something went wrong."})
	else:
		form = RegisterForm()

	return render(request, "registration/register.html", {"form": form})
