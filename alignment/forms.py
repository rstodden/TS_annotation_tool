from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .models import AlignmentPair, Sentence, Assessment

class RatingForm(forms.ModelForm):
    pair_id = forms.IntegerField(widget=forms.HiddenInput())
    # def __init__(self, alignment_id):
    #     self.alignment_id = alignment_id

    class Meta:
        model = Assessment #AlignmentPair
        fields = ['grammaticality', 'simplicity', 'meaning_preservation', 'transaction', 'certainty', "comment"]
        help_texts = {
            "meaning_preservation": "The simplified sentence adequately expresses the meaning of the original, perhaps omitting the least important information. 1 = very bad, 5 = very good.",
            "grammaticality": "The simplified sentence is fluent, there are no grammatical errors. 1 = very bad, 5 = very good.",
            "simplicity": "The simplified sentence is easier to understand than the original sentence. 1 = very bad, 5 = very good.",
            "certainty": "How certain are you regarding your rating? 1 = uncertain, 5 = very certain",
            "comment": "Leave a comment to note your thouts regarding the rating.",
            "transaction": "Choose one of the listed transactions which describe best the process during simplification."
        }



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class PairForm(forms.Form):
    pair_id = forms.IntegerField(widget=forms.HiddenInput())


# # class CorrectionForm(forms.ModelForm):
# #
# #     class Meta:
# #         model = Sentence
# #         fields = ('corrected_content')
#
#
# class AlignmentForm(forms.ModelForm):
# 	# align simple and complex sent. Therefore mark sentences from complex and simple data
#     class Meta:
#         model = AlignmentPair
#         fields = ('simple_element', 'complex_element')