from django import forms
from .models import ChangeLog


class AddChange(forms.ModelForm):
    class Meta:
        model = ChangeLog
        fields = ["headline", "topic", "comment", "priority"]

