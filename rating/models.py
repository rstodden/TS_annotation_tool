from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime

class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)
	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value':self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)


class Rating(models.Model):
	rater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	grammaticality = IntegerRangeField(min_value=1, max_value=5)
	simplicity = IntegerRangeField(min_value=1, max_value=5)
	meaning_preservation = IntegerRangeField(min_value=1, max_value=5)
	# grammaticality = IntegerRangeField(min_value=0, max_value=100)
	# simplicity = IntegerRangeField(min_value=0, max_value=100)
	# meaning_preservation = IntegerRangeField(min_value=0, max_value=100)
	certainty = IntegerRangeField(min_value=1, max_value=5)
	comment = models.TextField(max_length=1000, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	finished_at = models.DateTimeField(auto_now=True, blank=True)
	duration = models.DurationField(default=datetime.timedelta(), blank=True)
	list_transactions = (("split", "Sentence Split"),
						  ("join", "Joining Sentences"),
						  ("replace", "Word or Phrase Replacement"),
						  ("rephrase", "Rephrasing a part"),
						  ("addition", "Information Addition"),
						  ("anaphora", "Anaphora Resolution")
						  )
	transaction = models.CharField(max_length=100, choices=list_transactions, blank=True)



# Create your models here.



