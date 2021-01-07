from django import forms
from .models import Rating, Transformation, LIKERT_CHOICES_NEUTRAL, LIKERT_CHOICES
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
                  "simple_token", "complex_token"]
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
        # self.fields['transformation'].required = False
        # self.fields['transformation_level'].required = False
        self.fields['sub_transformation'].required = False


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['grammaticality_simple', 'meaning_preservation', 'ambiguity_original', 'ambiguity_simple',
                  'grammaticality_original', 'structural_simplicity', 'lexical_simplicity', 'coherence_simple',
                  'simplicity_original', 'simplicity_simple', 'information_gain', 'coherence_original', 'simplicity',
                  'certainty', "comment"]
        widgets = {
            'meaning_preservation': forms.RadioSelect(choices=LIKERT_CHOICES),
            'grammaticality_simple': forms.RadioSelect(choices=LIKERT_CHOICES_NEUTRAL),
            'grammaticality_original': forms.RadioSelect(choices=LIKERT_CHOICES_NEUTRAL),
            'simplicity': forms.RadioSelect(choices=LIKERT_CHOICES_NEUTRAL),
            'simplicity_original': forms.RadioSelect(choices=LIKERT_CHOICES),
            'simplicity_simple': forms.RadioSelect(choices=LIKERT_CHOICES),
            'structural_simplicity': forms.RadioSelect(choices=LIKERT_CHOICES_NEUTRAL),
            'lexical_simplicity': forms.RadioSelect(choices=LIKERT_CHOICES_NEUTRAL),
            'information_gain': forms.RadioSelect(choices=LIKERT_CHOICES_NEUTRAL),
            'coherence_original': forms.RadioSelect(choices=LIKERT_CHOICES),
            'coherence_simple': forms.RadioSelect(choices=LIKERT_CHOICES),
            'ambiguity_original': forms.RadioSelect(choices=LIKERT_CHOICES),
            'ambiguity_simple': forms.RadioSelect(choices=LIKERT_CHOICES),
        }

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
