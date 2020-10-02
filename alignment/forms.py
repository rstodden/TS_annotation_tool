from django import forms
from .models import Pair
import rating.models
import data.models
import rating.forms

class PairForm(forms.Form):
    pair_id = forms.IntegerField(widget=forms.HiddenInput())


class AlignmentForm(forms.ModelForm):
	# align simple and complex sent. Therefore mark sentences from complex and simple data
	class Meta:
		model = Pair
		fields = ('simple_element', 'complex_element')