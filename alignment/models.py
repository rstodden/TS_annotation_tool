from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from rating.models import Rating, Transformation
from data.models import Token, Sentence, DocumentPair


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
	document_pair = models.ForeignKey("data.DocumentPair", on_delete=models.CASCADE, blank=True, null=True, related_name="sentence_alignment_pair")

	def save_sentence_alignment_from_form(self, simple_elements, complex_elements, user, document):
		self.type = "parallel_online"
		self.manually_checked = True
		self.origin_annotator = user
		self.pair_identifier = get_sentence_pair_identifier()
		self.document_pair = document
		self.save()
		self.annotator.add(user)
		for sentence in complex_elements:
			sentence.complex_element.add(self)
		for sentence in simple_elements:
			sentence.simple_element.add(self)
		return simple_elements.order_by("-id")[0], complex_elements.order_by("-id")[0]

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
		transformation_tmp.delete()
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

	def next(self, user):
		doc_pair_tmp = self.document_pair
		all_pairs = list(doc_pair_tmp.sentence_alignment_pair.filter(annotator=user).order_by("id"))
		index_self = all_pairs.index(self)
		if index_self+1 < len(all_pairs):
			return all_pairs[index_self+1]
		else:
			return None

	def prev(self, user):
		doc_pair_tmp = self.document_pair
		all_pairs = list(doc_pair_tmp.sentence_alignment_pair.filter(annotator=user).order_by("id"))
		index_self = all_pairs.index(self)
		if index_self != 0:
			return all_pairs[index_self-1]
		else:
			return None


def get_sentence_pair_identifier():
	list_ids = Pair.objects.values_list("pair_identifier")
	if list_ids:
		return max(list_ids)[0] + 1
	else:
		return 1
