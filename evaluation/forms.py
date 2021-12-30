from django import forms
from data.models import popover_html


class ExportAlignmentForm(forms.Form):
	identical_pairs = forms.BooleanField(required=False, help_text=popover_html("Do you want to export identical (no-change) pairs? (automatically aligned)"))
	additions = forms.BooleanField(required=False, help_text=popover_html("Do you want to export sentences only occurring in the simplified text? (automatically aligned)"))
	deletions = forms.BooleanField(required=False, help_text=popover_html("Do you want to export sentences only occurring in the original text? (automatically aligned)"))
	# include_text = forms.BooleanField()
	per_user = forms.BooleanField(required=False, help_text=popover_html("Do you want to separate the data per user?"))
	per_corpus = forms.BooleanField(required=False, help_text=popover_html("Do you want to separate the data per corpus?"))
	format = forms.ChoiceField(choices=[("parallel", "parallel"), ("csv", "csv")], help_text=popover_html("CSV: All data in a comma-separated file. Parallel: Export in two files, where each row is aligned with each other."))