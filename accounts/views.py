from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
# from .views_admin import *
from django.contrib import messages

#
# def register(request):
# 	if request.method == "POST":
# 		form = RegisterForm(request.POST)
# 		if form.is_valid():
# 			form.save()
# 		username = request.POST['username']
# 		password = request.POST['password1']
# 		user = authenticate(request, username=username, password=password)
# 		if user is not None:
# 			login(request, user)
# 			return redirect("home")
# 		else:
# 			render(request, "registration/register.html", {"form": form, "error": "Something went wrong."})
# 	else:
# 		form = RegisterForm()

	# return render(request, "registration/register.html", {"form": form})


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        # print(form)
        if form.is_valid():
            print(form.cleaned_data)
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.annotator.age = form.cleaned_data.get('age')
            user.annotator.gender = form.cleaned_data.get('gender')
            user.annotator.native_language = form.cleaned_data.get('native_language')
            user.annotator.highest_education_level = form.cleaned_data.get('highest_education_level')
            user.annotator.language_level_de = form.cleaned_data.get('language_level_de')
            user.annotator.literacy_level = form.cleaned_data.get('literacy_level')
            user.annotator.training_in_linguistics = form.cleaned_data.get('training_in_linguistics')
            user.annotator.training_in_simple_language = form.cleaned_data.get('training_in_simple_language')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.add_message(request, messages.SUCCESS, "Congratulation, you're registered now.")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})