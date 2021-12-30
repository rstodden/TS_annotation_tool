from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime
from django import forms
import TS_annotation_tool.utils
import json


class Annotation(models.Model):
	rater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	certainty = TS_annotation_tool.utils.IntegerRangeField(min_value=1, max_value=5,
								  help_text="How certain are you regarding your annotation? 1 = uncertain, 5 = very certain", null=True, blank=True)
	comment = models.TextField(max_length=1000, blank=True, help_text="Do you have any comment regarding your annotation? Is something unclear in the sentence which influence your annotation?")
	created_at = models.DateTimeField(null=True, blank=True)
	updated_at = models.DateTimeField(null=True, blank=True)
	finished_at = models.DateTimeField(null=True, blank=True)
	duration = models.DurationField(null=True, blank=True)

	class Meta:
		abstract = True


class Transformation(Annotation):
	transformation = models.CharField(max_length=100, blank=True, choices=TS_annotation_tool.utils.tuple_list_choices_transformation)
	sub_transformation = models.CharField(max_length=100, blank=True, null=True, choices=TS_annotation_tool.utils.tuple_list_choices_subtransformation)
	# own_subtransformation = models.CharField(max_length=100, blank=True, null=True)
	transformation_level = models.CharField(max_length=50, choices=TS_annotation_tool.utils.tuple_list_transformation_level, blank=True, null=True)
	simple_token = models.ManyToManyField("data.Token", related_name="simple_token")
	complex_token = models.ManyToManyField("data.Token", related_name="complex_token")

	def edit(self, form, rater, start_time):  # , own_subtransformation):
		print(form.cleaned_data)
		self.rater = rater
		self.finished_at = datetime.datetime.now()
		self.duration = self.duration + (self.finished_at - datetime.datetime.strptime(json.loads(start_time), "%Y-%m-%dT%H:%M:%S.%f"))
		self.manually_checked = True
		self.sub_transformation = form.cleaned_data["sub_transformation"]
		# if self.sub_transformation == "other" and len(own_subtransformation) >= 1:
		# 	self.own_subtransformation = own_subtransformation
		self.transformation = form.cleaned_data["transformation"]
		self.transformation_level = form.cleaned_data["transformation_level"]
		self.comment = form.cleaned_data["comment"]
		self.certainty = form.cleaned_data["certainty"]
		self.save()
		for token in form.cleaned_data["complex_token"]:
			if token not in self.complex_token.all():
				self.complex_token.add(token)
		for token in form.cleaned_data["simple_token"]:
			if token not in self.simple_token.all():
				self.simple_token.add(token)
		for token in self.complex_token.all():
			if token not in form.cleaned_data["complex_token"]:
				self.complex_token.remove(token)
		for token in self.simple_token.all():
			if token not in form.cleaned_data["simple_token"]:
				self.simple_token.remove(token)
		self.save()
		return self

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

	if "grammaticality_simple" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		grammaticality_simple = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=TS_annotation_tool.utils.rating_aspects_dict["grammaticality_simple"], null=True, blank=True)
	if "grammaticality_original" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		grammaticality_original = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=TS_annotation_tool.utils.rating_aspects_dict["grammaticality_original"], null=True, blank=True)
	if "simplicity" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		simplicity = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=TS_annotation_tool.utils.rating_aspects_dict["simplicity"], null=True, blank=True)
	if "structural_simplicity" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		structural_simplicity = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=TS_annotation_tool.utils.rating_aspects_dict["structural_simplicity"], null=True, blank=True)
	if "lexical_simplicity" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		lexical_simplicity = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=TS_annotation_tool.utils.rating_aspects_dict["lexical_simplicity"], null=True, blank=True)
	if "simplicity_original" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		simplicity_original = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=TS_annotation_tool.utils.rating_aspects_dict["simplicity_original"], null=True, blank=True)
	if "simplicity_simple" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		simplicity_simple = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=TS_annotation_tool.utils.rating_aspects_dict["simplicity_simple"], null=True, blank=True)
	if "meaning_preservation" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		meaning_preservation = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=TS_annotation_tool.utils.rating_aspects_dict["meaning_preservation"], null=True, blank=True)
	if "information_gain" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		information_gain = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES_NEUTRAL, help_text=TS_annotation_tool.utils.rating_aspects_dict["information_gain"], null=True, blank=True)
	if "coherence_original" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		coherence_original = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=TS_annotation_tool.utils.rating_aspects_dict["coherence_original"], null=True, blank=True)
	if "coherence_simple" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		coherence_simple = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=TS_annotation_tool.utils.rating_aspects_dict["coherence_simple"], null=True, blank=True)
	if "ambiguity_original" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		ambiguity_original = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=TS_annotation_tool.utils.rating_aspects_dict["ambiguity_original"], null=True, blank=True)
	if "ambiguity_simple" in TS_annotation_tool.utils.rating_aspects_dict.keys():
		ambiguity_simple = models.IntegerField(choices=TS_annotation_tool.utils.LIKERT_CHOICES, help_text=TS_annotation_tool.utils.rating_aspects_dict["ambiguity_simple"], null=True, blank=True)

	def check_field_names(self):
		field_names = self._meta.get_fields()
		for aspect in TS_annotation_tool.utils.rating_aspects_dict.keys():
			if aspect not in field_names:
				raise "Please add "+aspect+" to the model fields in rating.models.py"

