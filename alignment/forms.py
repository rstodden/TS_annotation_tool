from django import forms
import data.models


class AlignmentForm(forms.ModelForm):
	simple_element = forms.ModelMultipleChoiceField(queryset=data.models.Sentence.objects.all())
	complex_element = forms.ModelMultipleChoiceField(queryset=data.models.Sentence.objects.all())
	class Meta:
		model = data.models.Sentence
		fields = ["complex_element", "simple_element"]

	def __init__(self, *args, **kwargs):
		super(AlignmentForm, self).__init__(*args, **kwargs)
		self.fields['complex_element'].required = True
		self.fields['simple_element'].required = True
