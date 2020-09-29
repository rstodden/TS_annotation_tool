from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)
	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value':self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)

class Document(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, primary_key=True, unique=True)
	source = models.CharField(max_length=500, blank=True)
	access_date = models.DateTimeField(blank=True, null=True)
	license = models.CharField(max_length=250, blank=True)
	domain = models.CharField(max_length=100, blank=True)
	simple_data = models.CharField(max_length=100, blank=True) # list of sentences
	complex_data = models.CharField(max_length=100, blank=True) # list of sentences
	plain_data = models.TextField(blank=True)

class Sentence(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, primary_key=True, unique=True)
	# translation = models.TextField(blank=True)
	# grammaticality = IntegerRangeField(min_value=1, max_value=5, default=0)
	# translation_quality = IntegerRangeField(min_value=1, max_value=5, default=0)
	domain = models.CharField(max_length=100, blank=True)
	source = models.CharField(max_length=500, blank=True)
	# many to one
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	original_content = models.TextField(blank=True)
	corrected_content = models.TextField(blank=True)
	level_list = (("a1", "Leichte Sprache"),
				   ("a2", "Einfache Sprache"),
				   ("c2", "Alltagssprache")
					)
	level = models.CharField(max_length=50, blank=True, choices=level_list)



class Assessment(models.Model):
	rater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	grammaticality = IntegerRangeField(min_value=1, max_value=5, blank=True)
	simplicity = IntegerRangeField(min_value=1, max_value=5, blank=True)
	meaning_preservation = IntegerRangeField(min_value=1, max_value=5, blank=True)
	# grammaticality = IntegerRangeField(min_value=0, max_value=100, blank=True)
	# simplicity = IntegerRangeField(min_value=0, max_value=100, blank=True)
	# meaning_preservation = IntegerRangeField(min_value=0, max_value=100, blank=True)
	certainty = IntegerRangeField(min_value=1, max_value=5, blank=True)
	comment = models.TextField(max_length=1000, blank=True)
	list_transactions = (("split", "Sentence Split"),
						  ("join", "Joining Sentences"),
						  ("replace", "Word or Phrase Replacement"),
						  ("rephrase", "Rephrasing a part"),
						  ("addition", "Information Addition"),
						  ("anaphora", "Anaphora Resolution")
						  )
	transaction = models.CharField(max_length=100, choices= list_transactions, blank=True)


# Create your models here.
class AlignmentPair(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, unique=True, primary_key=True)
	domain = models.CharField(max_length=100, blank=True)
	source = models.CharField(max_length=500, blank=True)
	# sentence element
	simple_element = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name="simple_sentence")
	# sentence element
	complex_element = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name="complex_sentence")
	manually_checked = models.BooleanField(default=False, blank=True)
	origin_annotator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="origin_annotator")
	annotator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="current_annotator")
	assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, blank=True, null=True)
	added = models.BooleanField(default=False, blank=True)
	pair_identifier = models.IntegerField(default=0, blank=True)




# class AlignmentPairSentence(AlignmentPair):
# 	# partially based on http://www.winlp.org/wp-content/uploads/2019/final_papers/211_Paper.pdf
# 	list_transactions = (("split", "Sentence Split"),
# 						  ("join", "Joining Sentences"),
# 						  ("replace", "Word or Phrase Replacement"),
# 						  ("rephrase", "Rephrasing a part"),
# 						  ("addition", "Information Addition"),
# 						  ("anaphora", "Anaphora Resolution")
# 						  )
# 	transaction = models.CharField(max_length=100, choices= list_transactions)
#
# class AlignmentPairDiscourse(AlignmentPair):
# 	# partially based on http://www.winlp.org/wp-content/uploads/2019/final_papers/211_Paper.pdf
# 	list_transactions = (("split", "Sentence Split"),
# 						  ("join", "Joining Sentences"),
# 						  ("replace", "Word or Phrase Replacement"),
# 						  ("rephrase", "Rephrasing a part"),
# 						  ("reordered", "Sentence Reordering"),
# 						  ("drop", "Sentence Removal"),
# 						  ("addition", "Sentence or Information Addition"),
# 						  ("anaphora", "Anaphora Resolution")
# 						  )
# 	transaction = models.CharField(max_length=100, choices= list_transactions)

