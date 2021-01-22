from django import forms
import alignment.models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from multiupload.fields import MultiFileField
from languages.languages import LANGUAGES
import data.models
import TS_annotation_tool.utils


class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])],)
    # users = forms.ModelMultipleChoiceField(User.objects.all())
    #, label="Select users to whom the pairs will be assigned"
    #  label="Select a CSV file with manual alignemnts:"


class UploadFilesForm(forms.ModelForm):
    class Meta:
        model = data.models.Corpus
        fields = ["name", "home_page", "language", "license", "domain", "parallel"]
    # corpus_name = forms.CharField(max_length=50)
    # url = forms.URLField()
    # language = forms.ChoiceField(choices=LANGUAGES)
    # license = forms.ChoiceField(choices=data.models.list_licenses)
    # domain = forms.CharField(max_length=50)
    language_level_simple = forms.ChoiceField(choices=TS_annotation_tool.utils.language_level_list)
    language_level_complex = forms.ChoiceField(choices=TS_annotation_tool.utils.language_level_list)
    annotator = forms.ModelMultipleChoiceField(User.objects.all())
    attachments = MultiFileField(min_num=2)

    def __init__(self, *args, **kwargs):
        super(UploadFilesForm, self).__init__(*args, **kwargs)
        self.fields['annotator'].required = False


class UploadAnnotatedFilesForm(forms.ModelForm):
    class Meta:
        model = data.models.Corpus
        fields = ["name", "home_page", "language", "license", "domain", "parallel"]