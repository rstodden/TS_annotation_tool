from django import forms
import alignment.models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])],)
    # users = forms.ModelMultipleChoiceField(User.objects.all())
    #, label="Select users to whom the pairs will be assigned"
    #  label="Select a CSV file with manual alignemnts:"
