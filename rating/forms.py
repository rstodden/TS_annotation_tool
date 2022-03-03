from django import forms

import TS_annotation_tool.utils
from .models import Rating, Transformation
from TS_annotation_tool.utils import LIKERT_CHOICES_NEUTRAL, LIKERT_CHOICES
from django.utils import timezone


# list_transactions = [("split", "Sentence Split"),
#                      ("merge", "Merging Sentences"),
#                      ("substitution", "Lexical substitution of a word"),
#                      ("deletion", "Deletion of words or phrases"),
#                      ("verbal changes", "Verbal changes"),
#                      ("insert", "Add new words, phrases or clauses"),
#                      ("reorder", "reorder phrases, clauses or complete sentence structure"),
#                      ("no", "no operation")
#                      ]
#
# transaction_level = [("par", "paragraph"), ("sent", "sentence"), ("phrase", "phrase"), ("word", "word")]


class TransformationForm(forms.ModelForm):
    class Meta:
        model = Transformation
        fields = ['certainty', "comment",
                  "transformation", "transformation_level", "sub_transformation",
                  # "own_subtransformation",
                  "simple_token", "complex_token", "insert_slot_start", "insert_at_beginning"]
        # , "insert_slot_end"]
        # , 'complex_tokens', 'simple_tokens', 'transaction', 'transaction_level',
    #     widgets = {
    #     'transaction': forms.CheckboxSelectMultiple(choices=list_transactions),
    #     'transaction_level': forms.CheckboxSelectMultiple(choices=transaction_level)
    # }

    def __init__(self, *args, **kwargs):
        super(TransformationForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = False
        # self.fields['certainty'].required = False
        self.fields['complex_token'].required = False
        self.fields['simple_token'].required = False
        # self.fields['transformation'].required = True
        self.fields['transformation_level'].required = True
        self.fields['sub_transformation'].required = False
        self.fields["insert_slot_start"].required = False
        # self.fields["insert_slot_end"].required = False
        self.fields["insert_at_beginning"].required = False

        # self.fields['own_subtransformation'].required = False


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = [*TS_annotation_tool.utils.rating_aspects,
                  'certainty', "comment"]
        widgets = {aspect: (forms.RadioSelect(choices=LIKERT_CHOICES) if aspect not in TS_annotation_tool.utils.rating_aspects_neutral else forms.RadioSelect(choices=LIKERT_CHOICES_NEUTRAL)) for aspect in TS_annotation_tool.utils.rating_aspects}

    def __init__(self, *args, **kwargs):
        super(RatingForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = False
        self.fields['certainty'].required = False

        # fields = ['grammaticality', 'meaning_preservation', 'simplicity',
        #           'grammaticality_original', 'structural_simplicity', 'lexical_simplicity',
        #           'simplicity_original', 'information_gain', 'simplicity_gain',
        #           'transaction', 'certainty', "comment"]
        #
        # help_texts = {
        #     'grammaticality': "The simplified sentence is fluent, there are no grammatical errors.",
        #     'grammaticality_original': "The original sentence is fluent, there are no grammatical errors.",
        #     'simplicity': "The simplified sentence is easier to understand than the orginal sentence.",
        #     'structural_simplicity': "The simplified sentence is easier to understand than the orginal sentence ignoring the complexity of the words.",
        #     'lexical_simplicity': "The simplified sentence is easier to understand than the orginal sentence ignoring the complexity of the sentence structure.",
        #     'simplicity_original': "The original sentence is easy to understand.",
        #     'meaning_preservation': "The simplified sentence adequately expresses the meaning of the original sentence, perhaps omitting the least important information.",
        #     'information_gain': "In the simplified sentence, information is added compared to the original sentence.",
        #     'simplicity_gain': "How many sucessful lexical or syntactical transformations occured in the simplification?",
        #     "comment": "Leave a comment to note your thoughts regarding the rating.",
        #     "transaction": "Choose one of the listed transactions which describe best the process during simplification.",
        #     "certainty": "How certain are you regarding your rating and alignment? 1 = uncertain, 5 = very certain"
        # }
