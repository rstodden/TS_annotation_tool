from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import change_log.forms
import change_log.models
from datetime import datetime

# Create your views here.

@login_required
def show_changelog(request):
	print(change_log.models.ChangeLog.objects.all())
	return render(request, "change_log/change_log.html", {"changes": change_log.models.ChangeLog.objects.all()})


def add_item(request):
	if request.POST:
		form = change_log.forms.AddChange(request.POST)
		if form.is_valid():
			form.save()
		return render(request, "change_log/change_log.html", {"changes": change_log.models.ChangeLog.objects.all(),
														  "form": form})
	else:
		form = change_log.forms.AddChange()
		return render(request, "change_log/add_todo.html", {"form": form})


def save_finished(request):
	if "todo_item" in request.POST:
		for item in request.POST.getlist("todo_item"):
			if change_log.models.ChangeLog.objects.filter(id=item):
				change_log_item = change_log.models.ChangeLog.objects.get(id=item)
				change_log_item.finished = True
				change_log_item.finished_at = datetime.now()
				change_log_item.save()
	return redirect("change_log:show_changelog")

