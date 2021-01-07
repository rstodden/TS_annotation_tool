from django import forms
from .models import Pair
# import rating.models
import data.models
# import rating.forms
#
# class PairForm(forms.Form):
# 	pair_id = forms.IntegerField(widget=forms.HiddenInput())
#


class AlignmentForm(forms.ModelForm):
	class Meta:
		model = Pair
		fields = ["complex_element", "simple_element"]
