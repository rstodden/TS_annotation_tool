from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime
from rating.models import Rating, Transformation
from data.models import Token

class Pair(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, unique=True, primary_key=True)
	simple_element = models.ManyToManyField("data.Sentence", related_name="simple_sentence")
	complex_element = models.ManyToManyField("data.Sentence", related_name="complex_sentence")
	manually_checked = models.BooleanField(default=True)
	origin_annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="origin_annotator", blank=True, null=True)
	annotator = models.ManyToManyField(User, related_name="current_annotator", blank=True)
	rating = models.ManyToManyField("rating.Rating", blank=True)
	transformation_of_pair = models.ManyToManyField("rating.Transformation", blank=True)
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

		# if self.rating.objects.filter(rater=rater):
		# 	rating_tmp = self.rating.objects.get(rater=rater)
		# else:
		# 	rating_tmp = Rating()
		# rating_tmp.simplicity = form.cleaned_data["simplicity"]
		# rating_tmp.grammaticality = form.cleaned_data["grammaticality"]
		# rating_tmp.meaning_preservation = form.cleaned_data["meaning_preservation"]
		# rating_tmp.comment = form.cleaned_data["comment"]
		# rating_tmp.certainty = form.cleaned_data["certainty"]
		# self.manually_checked = True
		# rating_tmp.rater_id = rater.id
		# rating_tmp.save()
		# if not self.rating.filter(rater=rater):
		# 	print(rating_tmp)
		# 	self.rating.add(rating_tmp)
		# self.save()
		# return self

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
		# transformation_tmp = Transformation(rater=rater)
		# transformation_tmp.comment = form_dict.get("comment")
		# transformation_tmp.certainty = form_dict.get("certainty")
		# transformation_tmp.transformation = form_dict.get("transformation")
		# transformation_tmp.transformation_level = form_dict.get("transformation_level")
		# if form_dict.get("subtransformation") and [element for element in form_dict.getlist("other_text") if element]:
		# 	transformation_tmp.sub_transformation = form_dict.get("sub_transformation") + ":" + " ".join([element for element in form_dict.getlist("other_text") if element])
		# else:
		# 	transformation_tmp.sub_transformation = form_dict.get("sub_transformation")
		# transformation_tmp.save()
		# for token_id in form_dict.getlist("complex_token"):
		# 	transformation_tmp.complex_token.add(Token.objects.get(id=token_id))
		# for token_id in form_dict.getlist("simple_token"):
		# 	transformation_tmp.simple_token.add(Token.objects.get(id=token_id))
		# # transformation_tmp.simple_token = form.cleaned_data["meaning_preservation"]
		# # transformation_tmp.complex_token = form.cleaned_data["meaning_preservation"]
		# self.manually_checked = True
		# transformation_tmp.save()
		# # if not self.transformation_of_pair.filter(rater=rater):
		# # 	print(transformation_tmp)
		# self.transformation_of_pair.add(transformation_tmp)
		# self.save()
		# return self

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

