from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Annotator
import TS_annotation_tool.utils
import data.models

class RegisterForm(UserCreationForm):
    # email = forms.EmailField(required=False, help_text=data.models.popover_html("Add your email address."))
    age = forms.IntegerField(required=False, help_text=data.models.popover_html("Add your age, it helps us to understand your annotations better."))
    # gender = forms.ChoiceField(required=False, choices=TS_annotation_tool.utils.gender)
    native_language = forms.ChoiceField(required=False, choices=TS_annotation_tool.utils.LANGUAGE_CHOICES, help_text=data.models.popover_html("Add your native language, it helps us to understand your annotations better."))
    highest_education_level = forms.ChoiceField(required=False, choices=TS_annotation_tool.utils.education_level, help_text=data.models.popover_html("Add your highest education level, it helps us to understand your annotations better."))
    language_level_de = forms.ChoiceField(required=False, choices=TS_annotation_tool.utils.personal_language_level, help_text=data.models.popover_html("Add your language level of the target language, it helps us to understand your annotations better."))
    literacy_level = forms.ChoiceField(required=False, choices=TS_annotation_tool.utils.literacy_levels, initial={"": ""}, help_text=data.models.popover_html("Add your literacy level, it helps us to understand your annotations better. The categories are based on OECD literacy levels"))
    training_in_linguistics = forms.BooleanField(required=False, help_text=data.models.popover_html("Are you trained in linguistics? The information helps us to understand your annotations better."))
    training_in_simple_language = forms.BooleanField(required=False, help_text=data.models.popover_html("Are you trained in simplified languages? The information helps us to understand your annotations better."))

    class Meta:
        model = User
        # exclude = ["email"]
        fields = ["username", "age", "native_language",
                   "highest_education_level", "language_level_de", "literacy_level", "training_in_linguistics",
                   "training_in_simple_language", "password1", "password2"]


# age = models.IntegerField()
# gender = models.CharField(max_length=10, choices=TS_annotation_tool.utils.gender)
# native_language = models.CharField(max_length=8, choices=TS_annotation_tool.utils.LANGUAGE_CHOICES)
# highest_education_level = models.CharField(choices=TS_annotation_tool.utils.education_level)
# language_level_de = models.CharField(max_length=250, choices=TS_annotation_tool.utils.personal_language_level)
# literacy_level = models.CharField(max_length=250, choices=TS_annotation_tool.utils.literacy_levels, blank=True)
# training_in_linguistics = models.BooleanField()
# training_in_simple_language = models.BooleanField()