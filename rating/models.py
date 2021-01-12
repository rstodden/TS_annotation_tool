from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime
from django import forms
import TS_annotation_tool.utils


class Annotation(models.Model):
	rater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	certainty = TS_annotation_tool.utils.IntegerRangeField(min_value=1, max_value=5,
								  help_text="How certain are you regarding your annotation? 1 = uncertain, 5 = very certain", null=True, blank=True)
	comment = models.TextField(max_length=1000, blank=True, help_text="Do you have any comment regarding your annotation? Is something unclear in the sentence which influence your annotation?")
	created_at = models.DateTimeField(auto_now_add=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	finished_at = models.DateTimeField(auto_now=True, blank=True)
	duration = models.DurationField(default=datetime.timedelta(), blank=True)

	class Meta:
		abstract = True


class Transformation(Annotation):
	transformation = models.CharField(max_length=100, blank=True, choices=TS_annotation_tool.utils.tuple_list_choices_transformation)  # choices=list_transactions,
	sub_transformation = models.CharField(max_length=100, blank=True, null=True , choices=TS_annotation_tool.utils.tuple_list_choices_subtransformation)
	transformation_level = models.CharField(max_length=50, choices=TS_annotation_tool.utils.tuple_list_transformation_level)
	# models.CharField(choices=[("paragraph", "paragraph"), ("sentence", "sentence"), ("phrase", "phrase"), ("word", "word")])
	simple_token = models.ManyToManyField("data.Token", related_name="simple_token")
	complex_token = models.ManyToManyField("data.Token", related_name="complex_token")

	def __str__(self):
		if self.sub_transformation:
			subtrans = " - " + self.sub_transformation
		else:
			subtrans = ""
		if self.simple_token.exists() and self.complex_token.exists():
			return self.transformation_level + ' - ' + self.transformation + subtrans + ' (' + str(self.id) + '): ' + \
				   ' '.join(self.complex_token.values_list("text", flat=True)) + ' \u2192 ' + \
				   ' '.join(self.simple_token.values_list("text", flat=True))
		elif self.simple_token.exists() and not self.complex_token.exists():
			return self.transformation_level + ' - ' + self.transformation + subtrans + ' (' + str(self.id) + \
				   '): \u002B ' + ' '.join(self.simple_token.values_list("text", flat=True))
		if not self.simple_token.exists() and self.complex_token.exists():
			return self.transformation_level + ' - ' + self.transformation + subtrans + ' (' + str(self.id) + \
				   '): \u2212 ' + ' '.join(self.complex_token.values_list("text", flat=True))
		else:
			return self.transformation_level + ' - ' + self.transformation + ' (' + str(self.id) + ')'


class Rating(Annotation):
	rater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	help_text_grammaticality = "The {} sentence is fluent, there are no grammatical errors."
	help_text_simplicity = "The {} sentence is easy to understand."
	help_text_coherence = "The {} sentence is understandable without any preceeding or following sentence, e.g., there are no pronouns or connectives."
	help_text_ambiguity = "The {} sentence is ambiguous. It can be read in different ways."
	help_text_simpler = "The simplified sentence is easier to understand than the orginal sentence."
	help_text_meaning_preservation = "The simplified sentence adequately expresses the meaning of the original sentence, perhaps omitting the least important information."
	help_text_structural = "The structure of the simplified sentence is easier to understand than the structure of the original sentence."
	help_text_lexical = "The words of the simplified sentence are easier to understand than the words of the original sentence."
	help_text_information_gain = "In the simplified sentence, information is added or get more explicit compared to the original sentence."

	grammaticality_simple = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=help_text_grammaticality.format("simplified"))
	grammaticality_original = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=help_text_grammaticality.format("original"))
	simplicity = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=help_text_simpler)
	structural_simplicity = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=help_text_structural)
	lexical_simplicity = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=help_text_lexical)
	simplicity_original = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=help_text_simplicity.format("original"))
	simplicity_simple = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=help_text_simplicity.format("simplified"))
	meaning_preservation = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=help_text_meaning_preservation)
	information_gain = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=help_text_information_gain)
	coherence_original = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=help_text_coherence.format("original"))
	coherence_simple = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=help_text_coherence.format("simplified"))
	ambiguity_original = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=help_text_ambiguity.format("original"))
	ambiguity_simple = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=help_text_ambiguity.format("simplified"))
