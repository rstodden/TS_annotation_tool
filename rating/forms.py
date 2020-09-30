from django import forms
from .models import Rating
from django.utils import timezone


class RatingForm(forms.ModelForm):
    pair_id = forms.IntegerField(widget=forms.HiddenInput())
    # def __init__(self, alignment_id):
    #     self.alignment_id = alignment_id

    class Meta:
        model = Rating
        fields = ['grammaticality', 'simplicity', 'meaning_preservation', 'transaction', 'certainty', "comment"]
        help_texts = {
            "meaning_preservation": "The simplified sentence adequately expresses the meaning of the original, perhaps omitting the least important information. 1 = very bad, 5 = very good.",
            "grammaticality": "The simplified sentence is fluent, there are no grammatical errors. 1 = very bad, 5 = very good.",
            "simplicity": "The simplified sentence is easier to understand than the original sentence. 1 = very bad, 5 = very good.",
            "certainty": "How certain are you regarding your rating? 1 = uncertain, 5 = very certain",
            "comment": "Leave a comment to note your thouts regarding the rating.",
            "transaction": "Choose one of the listed transactions which describe best the process during simplification."
        }



class PairForm(forms.Form):
    pair_id = forms.IntegerField(widget=forms.HiddenInput())
