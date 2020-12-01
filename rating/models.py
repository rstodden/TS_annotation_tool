from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime
from django import forms


class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)
	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value':self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)


LIKERT_CHOICES = [(1, "strongly disgree"), (2, "disagree"), (3, "neither agree nor disagree"),
           (4, "agree"), (5,  "strongly agree")]


class Rating(models.Model):
	rater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	grammaticality = models.IntegerField(max_length=1, choices=LIKERT_CHOICES, help_text="The simplified sentence is fluent, there are no grammatical errors.")
	grammaticality_original = models.IntegerField(max_length=1, choices=LIKERT_CHOICES, help_text="The original sentence is fluent, there are no grammatical errors.")
	simplicity = models.IntegerField(max_length=1, choices=LIKERT_CHOICES, help_text="The simplified sentence is easier to understand than the orginal sentence.")
	structural_simplicity = models.IntegerField(max_length=1, choices=LIKERT_CHOICES, help_text="The simplified sentence is easier to understand than the orginal sentence ignoring the complexity of the words.")
	lexical_simplicity = models.IntegerField(max_length=1, choices=LIKERT_CHOICES, help_text="The simplified sentence is easier to understand than the orginal sentence ignoring the complexity of the sentence structure.")
	simplicity_original = models.IntegerField(max_length=1, choices=LIKERT_CHOICES, help_text="The original sentence is easy to understand.")
	meaning_preservation = models.IntegerField(max_length=1, choices=LIKERT_CHOICES, help_text="The simplified sentence adequately expresses the meaning of the original sentence, perhaps omitting the least important information.")
	information_gain = models.IntegerField(max_length=1, choices=LIKERT_CHOICES, help_text="In the simplified sentence, information is added compared to the original sentence.")
	simplicity_gain = IntegerRangeField(min_value=0, max_value=100, help_text="How many sucessful lexical or syntactical transformations occured in the simplification?")

	# grammaticality = IntegerRangeField(min_value=1, max_value=5, help_text="The simplified sentence is fluent, there are no grammatical errors.")
	# grammaticality_original = IntegerRangeField(min_value=1, max_value=5, help_text="The original sentence is fluent, there are no grammatical errors.")
	# simplicity = IntegerRangeField(min_value=1, max_value=5, help_text="The simplified sentence is easier to understand than the orginal sentence.")
	# structural_simplicity = IntegerRangeField(min_value=1, max_value=5, help_text="The simplified sentence is easier to understand than the orginal sentence ignoring the complexity of the words.")
	# lexical_simplicity = IntegerRangeField(min_value=1, max_value=5, help_text="The simplified sentence is easier to understand than the orginal sentence ignoring the complexity of the sentence structure.")
	# simplicity_original = IntegerRangeField(min_value=1, max_value=5, help_text="The original sentence is easy to understand.")
	# meaning_preservation = IntegerRangeField(min_value=1, max_value=5, help_text="The simplified sentence adequately expresses the meaning of the original sentence, perhaps omitting the least important information.")
	# information_gain = IntegerRangeField(min_value=1, max_value=5, help_text="In the simplified sentence, information is added compared to the original sentence.")
	# simplicity_gain = IntegerRangeField(min_value=0, max_value=100, help_text="How many sucessful lexical or syntactical transformations occured in the simplification?")
	# grammaticality = IntegerRangeField(min_value=0, max_value=100)
	# simplicity = IntegerRangeField(min_value=0, max_value=100)
	# meaning_preservation = IntegerRangeField(min_value=0, max_value=100)

	certainty = IntegerRangeField(min_value=1, max_value=5, help_text="How certain are you regarding your rating? 1 = uncertain, 5 = very certain")
	comment = models.TextField(max_length=1000, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	finished_at = models.DateTimeField(auto_now=True, blank=True)
	duration = models.DurationField(default=datetime.timedelta(), blank=True)
	list_transactions = [("split", "Sentence Split"),
						  ("merge", "Merging Sentences"),
						  ("substitution", "Lexical substitution of a word"),
						  ("deletion", "Deletion of words or phrases"),
						  ("verbal changes", "Verbal changes"),
						  ("insert", "Add new words, phrases or clauses"),
						  ("reorder", "reorder phrases, clauses or complete sentence structure"),
						  ("no", "no operation")
						  ]
	transaction = models.CharField(max_length=100, choices=list_transactions, blank=True)

	# list_transaction_classes = ["merge", "split", "delete", "insert", "reorder", "lexical substitution", "no operation",
	# 							"verbal changes"]
	# list_transaction_subclasses = ["lexical substitution", "delete word", "split", "compound segmentation",
	# 							   "nominal to verbal style", "more frequent word", "abbreviation", "rephrasing",
	# 							   "verb to noun", "insert word", "ellipsis", "anaphora", "metaphors", "short word",
	# 							   "numbers", "synonym", "MWE", "hyponym", "hypernym", "discourse markers",
	# 							   "abbreviation", "filter word", "keep", "delete phrase or clause", "delete phrase",
	# 							   "delete clause", "reorder phase, sentence or paragraph", "replace phrase/clause",
	# 							   "insert phrase", "insert clause", "insert phrase/clause", "less adjunct phrases",
	# 							   "discontinuity resolution", "verbal changes", "voice of verb", "verb tense",
	# 							   "verb mood", "identical", "Subject-verb-reorder", "genitive to dative",
	# 							   "negative to positive", "coordinate clause", "subordinative clause",
	# 							   "appositive clause", "adverbial clause", "relative clause", "sentence order changed",
	# 							   "insert sentence", "insert explanation", "insert examplification", "delete sentence",
	# 							   "merge sentence"]
	transaction_level = models.CharField(max_length=100, choices=[("par", "paragraph"), ("sent", "sentence"),
																  ("phrase", "phrase"), ("word", "word")], blank=True)


# Create your models here.



"""transformations : {
"paragraph": {
	"reorder": {"sentence order changed", "general"},
	"insert": {"insert sentence": {"insert explanation", "insert examplification"}, "general"}, 
	"delete": {"delete sentence"}, 
	"merge": {"merge sentences"}
	}, 
"sentence": {
	"split": {"general", "coordinate clause", "subordinative clause", "appositive clause", "adverbial clause", "relative clause"}, 
	"verbal changes": {"general", "voice of verb", "verb tense", "verb mood"}, 
	"reorder": {"Subject-verb-reorder", "genitive to dative", "negative to positive"}, 
	"no operation": {"identical"}
	},
"phrase": {
	"deletion": {"delete phrase or clause": {"delete phrase", "delete clause"},  "less adjunct phrases", "replace phrase/clause", 
	"reorder": {"discontinuity resolution"}, 
	"reorder": {}, 
	"insert": {}}, 
"word"}}
 

reorder phase, sentence or paragraph	phrase/clause	reorder

insert phrase	phrase/clause	insert
insert clause	phrase/clause	insert
insert phrase/clause	phrase/clause	insert

discontinuity resolution	phrase/clause	reorder
"""