from django import forms
import data.models


# class SimplificationForm(forms.ModelForm):
# 	# simple_element = forms.ModelMultipleChoiceField(queryset=data.models.Sentence.objects.all())
# 	complex_element = forms.ModelMultipleChoiceField(queryset=data.models.Sentence.objects.all())
# 	simple_text = forms.TextInput()
# 	class Meta:
# 		model = data.models.Sentence
# 		fields = ["complex_element"] + ("simple_text",)
#
# 	def __init__(self, *args, **kwargs):
# 		super(SimplificationForm, self).__init__(*args, **kwargs)
# 		self.fields['complex_element'].required = True
# 		# self.fields['simple_text'].required = True


class SimplificationForm(forms.Form):
	# simple_element = forms.ModelMultipleChoiceField(queryset=data.models.Sentence.objects.all())
	complex_element = forms.ModelMultipleChoiceField(queryset=data.models.Sentence.objects.all(), required=True)
	simple_text = forms.CharField(required=True)

