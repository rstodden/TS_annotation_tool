# from django import forms
# from .models import Pair
# import rating.models
# import data.models
# import rating.forms
#
# class PairForm(forms.Form):
# 	pair_id = forms.IntegerField(widget=forms.HiddenInput())
#
#
# class AlignmentForm(forms.ModelForm):
# 	def __init__(self, *args, **kwargs):
# 		self._parallel_doc_id = kwargs.pop('parallel_doc_id', None)
# 		self._doc_id = kwargs.pop('doc_id', None)
# 		super().__init__(*args, **kwargs)
#
# 	# align simple and complex sent. Therefore mark sentences from complex and simple data
# 	class Meta:
# 		model = Pair
# 		# simple_elements = forms.ModelMultipleChoiceField(data.models.Document.objects.get(id=AlignmentForm._doc_id).alignments.all())
# 		# complex_elements = forms.ModelMultipleChoiceField(data.models.Document.objects.get(id=self._parallel_doc_id).alignments.all())
