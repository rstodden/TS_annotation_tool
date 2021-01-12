from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime
from rating.models import Rating, Transformation
from data.models import Token, Sentence, DocumentPair
from django.db.models import Q


class Pair(models.Model):
	manually_checked = models.BooleanField(default=True)
	origin_annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="origin_annotator", blank=True, null=True)
	annotator = models.ManyToManyField(User, related_name="current_annotator", blank=True)
	rating = models.ManyToManyField("rating.Rating", blank=True)
	transformation_of_pair = models.ManyToManyField("rating.Transformation", blank=True)
	# manually_added = models.BooleanField(default=False, blank=True)
	pair_identifier = models.IntegerField(default=1)
	created_at = models.DateTimeField(auto_now_add=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	finished_at = models.DateTimeField(auto_now=True, blank=True)
	duration = models.DurationField(default=datetime.timedelta(), blank=True)
	type_choices = (("parallel_online", "verified online"),
					("translated", "translated version"),
					("simplified", "manually simplified"),
					("parallel_online_uploaded", "parallel online documents manually aligned and uploaded"))
	type = models.CharField(choices=type_choices, max_length=50)
	document_pair = models.ForeignKey("data.DocumentPair", on_delete=models.CASCADE, blank=True, null=True)

	def save_sentence_alignment_from_form(self, simple_elements, complex_elements, user, document):
		self.type = "parallel_online"
		self.manually_checked = True
		self.origin_annotator = user
		self.pair_identifier = get_sentence_pair_identifier()
		self.document_pair = document
		self.save()
		self.annotator.add(user)
		for sentence_id in complex_elements:
			sentence = Sentence.objects.get(id=sentence_id)
			sentence.complex_element.add(self)
		for sentence_id in simple_elements:
			sentence = Sentence.objects.get(id=sentence_id)
			sentence.simple_element.add(self)

		return self



	# ------- unchecked -----------


	def update_or_save_rating(self, form, rater):
		rating_tmp = form.save(commit=False)
		rating_tmp.rater = rater
		self.manually_checked = True
		rating_tmp.save()
		if self.rating.filter(rater=rater):
			rating_old = self.rating.get(rater=rater)
			self.rating.remove(rating_old)
			rating_old.delete()
		self.rating.add(rating_tmp)
		self.save()
		return self


	def delete_transformation(self, transformation_id, rater):
		transformation_tmp = Transformation.objects.get(id=transformation_id, rater=rater)
		if self.transformation_of_pair.filter(id=transformation_id, rater=rater):
			self.transformation_of_pair.remove(transformation_tmp)
		transformation_tmp.delete()
		self.save()
		return self

	def save_transformation(self, form, rater):
		transformation_tmp = form.save(commit=False)
		transformation_tmp.rater = rater
		self.manually_checked = True
		transformation_tmp.save()
		for token in form.cleaned_data["complex_token"]:
			transformation_tmp.complex_token.add(token)
		for token in form.cleaned_data["simple_token"]:
			transformation_tmp.simple_token.add(token)
		transformation_tmp.save()
		self.transformation_of_pair.add(transformation_tmp)
		self.save()
		return self


	# def update_sentences(self, simple_sents, complex_sents):
	# 	self.simple_element.clear()
	# 	self.complex_element.clear()
	# 	self.simple_element.add(*simple_sents)
	# 	self.complex_element.add(*complex_sents)
	# 	self.type = "parallel_online"
	# 	self.manually_checked = 1
	# 	self.save()
	# 	return self

	def save_rating(self, form, rater):
		rating_tmp = Rating(form.save(commit=False))
		rating_tmp.rater = rater
		self.manually_checked = True
		self.rating = rating_tmp
		self.save()
		return self

	def assign_to_user(self, users):
		for user in users:
			self.annotator.add(user)
		pass

	# def __str__(self):
	# 	if self.complex_element.exists() and self.simple_element.exists() and \
	# 			None not in list(self.complex_element.all().values_list("tokens__text", flat=True)) and \
	# 			None not in list(self.simple_element.all().values_list("tokens__text", flat=True)):
	#
	# 		return " ".join(self.complex_element.all().values_list("tokens__text", flat=True)[:5]) + '... \u2194 ' +\
	# 			   " ".join(self.simple_element.all().values_list("tokens__text", flat=True)[:5]) + '...'
	# 	else:
	# 		return "Pair object (" + str(self.id) + ")"


def get_sentence_pair_identifier():
	list_ids = Pair.objects.values_list("pair_identifier")
	if list_ids:
		return max(list_ids)[0] + 1
	else:
		return 1
