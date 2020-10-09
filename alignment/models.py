from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import rating.models
import datetime


class Pair(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, unique=True, primary_key=True)
	simple_element = models.ManyToManyField("data.Sentence", related_name="simple_sentence")
	complex_element = models.ManyToManyField("data.Sentence", related_name="complex_sentence")
	manually_checked = models.BooleanField(default=True)
	origin_annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="origin_annotator", blank=True, null=True)
	annotator = models.ManyToManyField(User, related_name="current_annotator", blank=True, null=True)
	rating = models.ManyToManyField(rating.models.Rating, blank=True)
	# manually_added = models.BooleanField(default=False, blank=True)
	pair_identifier = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	finished_at = models.DateTimeField(auto_now=True, blank=True)
	duration = models.DurationField(default=datetime.timedelta(), blank=True)
	type_choices = (("parallel_online", "verified online"),
					("translated", "translated version"),
					("simplified", "manually simplified"),
					("parallel_online_uploaded", "parallel online documents manually aligned and uploaded"))
	type = models.CharField(choices=type_choices, max_length=50)

	def update_or_save_rating(self, form, rater):
		if self.rating.filter(rater=rater):
			rating_tmp = self.rating.get(rater=rater)
		else:
			rating_tmp = rating.models.Rating()
		rating_tmp.simplicity = form.cleaned_data["simplicity"]
		rating_tmp.grammaticality = form.cleaned_data["grammaticality"]
		rating_tmp.meaning_preservation = form.cleaned_data["meaning_preservation"]
		rating_tmp.comment = form.cleaned_data["comment"]
		rating_tmp.transaction = form.cleaned_data["transaction"]
		rating_tmp.certainty = form.cleaned_data["certainty"]
		self.manually_checked = True
		rating_tmp.rater_id = rater.id
		rating_tmp.save()
		if not self.rating.filter(rater=rater):
			print(rating_tmp)
			self.rating.add(rating_tmp)
		self.save()
		return self

	def update_sentences(self, simple_sents, complex_sents):
		self.simple_element.clear()
		self.complex_element.clear()
		self.simple_element.add(*simple_sents)
		self.complex_element.add(*complex_sents)
		self.type = "parallel_online"
		self.manually_checked = 1
		self.save()
		return self

	def save_rating(self, form, rater):
		rating_tmp = rating.models.Rating(form.save(commit=False))
		rating_tmp.rater = rater
		self.manually_checked = True
		self.rating = rating_tmp
		self.save()
		return self

	def assign_to_user(self, users):
		for user in users:
			self.annotator.add(user)
		pass

