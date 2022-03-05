from django import forms
import alignment.models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from multiupload.fields import MultiFileField
from django.core.exceptions import FieldDoesNotExist
import data.models
import TS_annotation_tool.utils
# from crispy_forms.helper import FormHelper

class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])],)
    # users = forms.ModelMultipleChoiceField(User.objects.all())
    #, label="Select users to whom the pairs will be assigned"
    #  label="Select a CSV file with manual alignemnts:"


class UploadFilesForm(forms.ModelForm):
    class Meta:
        model = data.models.Corpus
        fields = ["name", "home_page", "author", "license", "license_file", "parallel",  "pre_aligned",
                  "manually_aligned", "pre_split", "to_simplify", "domain", "language", "continuous_text"]

        # help_texts = {
        #     'add_par_nr': data.models.popover_html("Do you want to add paragraph and sentence numbers?"),
        #     'language_level_simple': 'On which language level (following CEFR) ist the simple text? E.g., A1 for easy-to-read language, A2 or B1 for plain language.',
        #     'language_level_complex': 'On which language level (following CEFR) ist the complex text? E.g., C" for everyday language.',
        #     'annotator': 'Which annotator(s) should align, rate or annotate the texts?',
        #     'name': "How should the corpus be called in the annotation tool?",
        #     'home_page': "What is the source of the (web) data)? Please provide at least a author name or homepage.",
        #     'author': 'Who is/are the author(s) of the data? Please provide at least a author name or homepage.',
        #     'license': 'Is the data published under a specific license?',
        #     'license_file': "If a license file is provided, please upload it.",
        #     'domain': 'How can the domain of the data be described?',
        #     'language': "In which language is the data?",
        #     'pre_aligned': "Are the documents already sentence-wise aligned?",
        #     'pre_split': "Are the sentences already split?",
        #     'manually_aligned': "If the texta are already aligned, were they manually or automatically aligned?",
        #     'parallel': "Do comparable or parallel documents exist? If not you can select the to_simplify option.",
        #     'to_simplify': "If no simplified version of a text exists so far you can upload the complex version with this option and simplify the texts yourself.",
        # }
    # corpus_name = forms.CharField(max_length=50)
    # url = forms.URLField()
    # languages = forms.ChoiceField(choices=TS_annotation_tool.utils.LANGUAGE_CHOICES)
    # license = forms.ChoiceField(choices=data.models.list_licenses)
    # domain = forms.CharField(max_length=50)
    find_most_similiar = forms.BooleanField(required=False, help_text=data.models.popover_html('Would you like to calculate similarity between the sentences to get alignment hints?'))
    language_level_simple = forms.ChoiceField(required=False, choices=TS_annotation_tool.utils.language_level_list, help_text=data.models.popover_html('On which language level (following CEFR) ist the simple text? E.g., A1 for easy-to-read language, A2 or B1 for plain language.)'))
    language_level_complex = forms.ChoiceField(choices=TS_annotation_tool.utils.language_level_list, help_text=data.models.popover_html('On which language level (following CEFR) ist the complex text? E.g., C" for everyday language.'))
    professionally_simplified = forms.BooleanField(required=False, help_text=data.models.popover_html("Were the simplified texts professionally simplified?"))
    annotator = forms.ModelMultipleChoiceField(User.objects.all(), help_text=data.models.popover_html('Which annotator(s) should align, rate or annotate the texts?'))
    attachments = MultiFileField(min_num=2)

    def __init__(self, *args, **kwargs):
        super(UploadFilesForm, self).__init__(*args, **kwargs)
        self.fields['annotator'].required = False
        self.fields['license_file'].required = False
        self.fields['home_page'].required = False
        self.fields['author'].required = False
        # self.helper = FormHelper()


class UploadAnnotatedFilesForm(forms.ModelForm):
    class Meta:
        model = data.models.Corpus
        fields = ["name", "home_page", "language", "license", "domain", "parallel"]


class SentenceProblemForm(forms.ModelForm):
    class Meta:
        model = data.models.Sentence
        fields = ["malformed", "malformed_comment"]


class UploadWithCrawlerForm(forms.Form):
    file = forms.FileField()


class UploadRatingForm(forms.Form):
    annotator = forms.ModelChoiceField(User.objects.all())
    file = forms.FileField()