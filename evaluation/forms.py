from django import forms
from evaluation.models import MetaData
import data.models
from data.models import popover_html
from django.contrib.auth.models import User


class ExportAlignmentForm(forms.Form):
	identical_pairs = forms.BooleanField(required=False, help_text=popover_html("Do you want to export identical (no-change) pairs? (automatically aligned)"))
	additions = forms.BooleanField(required=False, help_text=popover_html("Do you want to export sentences only occurring in the simplified text? (automatically aligned)"))
	deletions = forms.BooleanField(required=False, help_text=popover_html("Do you want to export sentences only occurring in the original text? (automatically aligned)"))
	# include_text = forms.BooleanField()
	per_user = forms.BooleanField(required=False, help_text=popover_html("Do you want to separate the data per user?"))
	per_corpus = forms.BooleanField(required=False, help_text=popover_html("Do you want to separate the data per corpus?"))
	format = forms.ChoiceField(choices=[("parallel", "parallel"), ("csv", "csv")], help_text=popover_html("CSV: All data in a comma-separated file. Parallel: Export in two files, where each row is aligned with each other."))


class MetaDataForm(forms.ModelForm):
	"""
	based on HuggingFace Data Sheets https://github.com/huggingface/datasets/blob/master/templates/README_guide.md
	"""
	class Meta:
		model = MetaData
		exclude = ["id"]
	# # # text_included = forms.MultipleChoiceField(choices=data.models.Corpus.objects.all(), help_text=popover_html("Which texts are included? (Curation Rationale)"))
	# # text_selection = forms.CharField(widget=forms.Textarea, help_text=popover_html("Why and with which motivate are the texts selected? (Curation Rationale)"))
	# # # language = forms.MultipleChoiceField(choices=data.models.Corpus.objects.all().values_list("language", flat=True))
	# # # annotator = forms.MultipleChoiceField(choices=User.objects.all().values_list("username"))
	# # domain = forms.ModelMultipleChoiceField(queryset=data.models.Corpus.objects.all().values_list("domain", flat=True).distinct())
	# # # language_levels = forms.MultipleChoiceField(choices=data.models.Corpus.objects.all().values_list("simple_level", flat=True))
	# # # licenses = forms.MultipleChoiceField(choices=data.models.Corpus.objects.all().values_list("license"))
	# # annoation_process = forms.CharField(widget=forms.Textarea, help_text=popover_html("Please describe the annotation process."))
	# # annotation_guidelines = forms.URLField(help_text=popover_html("Please add the link to the annotation guidelines or annotation schema used for building the data set."))
	# # dataset_authors = forms.CharField(widget=forms.Textarea, help_text=popover_html("Who are the responsible authors of the data set?"))
	# # rating = forms.BooleanField(help_text=popover_html("Are ratings of the sentence pairs annotated?"))
	# # transformations = forms.BooleanField(help_text=popover_html("Are rewriting transformations of the sentence pairs annotated?"))
	# # distribution_of_data = forms.CharField(widget=forms.Textarea, help_text=popover_html("How will the data be distributed? Add a link to the save location."))
	# # personal_sensitive_info = forms.CharField(widget=forms.Textarea, help_text=popover_html("Does the data contain sensitive or personal information?"))
	# summary = forms.CharField(widget=forms.Textarea, help_text=popover_html("Please summarize your data set briefly. "))
	# dataset_creation = forms.CharField(widget=forms.Textarea, help_text=popover_html("Please summarize your data set briefly. "))
	# language_description = forms.CharField(widget=forms.Textarea, help_text=popover_html("Which texts are included? Why and with which motivate are the texts selected?"))
	# domain_decription = forms.CharField(widget=forms.Textarea, help_text=popover_html("Which domains are included?"))
	# annotation_process_description = forms.CharField(widget=forms.Textarea, help_text=popover_html("Describe the annotation process."))
	# annotator_description = forms.CharField(widget=forms.Textarea, help_text=popover_html("Describe the annotators."))
	# sensitive_data_description = forms.CharField(widget=forms.Textarea)
	# bias_description = forms.CharField(widget=forms.Textarea)
	# social_impact_description = forms.CharField(widget=forms.Textarea)
	# limitations_description = forms.CharField(widget=forms.Textarea)
	# license_description = forms.CharField(widget=forms.Textarea)
	# curator_description = forms.CharField(widget=forms.Textarea)
	# citation_description = forms.CharField(widget=forms.Textarea)
	# contribution_description = forms.CharField(widget=forms.Textarea)
	# task_description = forms.CharField(widget=forms.Textarea)
	# homepage = forms.CharField()
	# repository = forms.CharField()
	# paper = forms.CharField()
	# leaderboard = forms.CharField()
	# point_of_contact = forms.CharField()
	# data_fields_description = forms.CharField(widget=forms.Textarea)

