from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime
from django import forms

transformation_dict = {"word": {
							"deletion": ["discourse_markers", "abbreviations", "filter_words", "other"],
							"lexical_substitution": ["compound_segmentation", "more_frequent_word", "abbreviation",
													 "anaphora", "shorter_word", "synonym", "hyponym", "hypernym",
													 "nominalization", "metaphor_resolution", "number", "other"],
							"insert": ["ellipsis_filled", "other"],
							# "no_operation": [],
							},
					   "phrase": {
						   "reorder": ["discontinuity_resolution", "other"],
						   "deletion": ["phrase", "clause", "replace", "less_adjunct_phrase", "other"],
						   "rephrase": [],
					   		"insert": ["clause", "phrase", "other"]
					   		},
					   "sentence": {
						   "split": ["coordinate_clause", "subordinate_clause", "appositive_phrase", "adverbial_clause",
									 "relative_clause", "other"],
						   "verbal_changes": ["voice_of_verb", "verb_tense", "verb_mood", "other"],
						   "lexical_substitution": ["verbalization", "other"],
						   "reorder": ["subject-verb-reorder", "genitive to dative", "negative to positive", "other"],
						   "rephrase": [],
						   # "no_operation: []",
					   		},
					   # "paragraph": {
						#    "reorder": {"sentence-order-changed"},
						#    "merge": {},
						#    "deletion": {},
						#    "insert": {"explanation", "examplification"}
					   # }
				   }

class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)
	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value': self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)


LIKERT_CHOICES = [(1, "strongly disgree"), (2, "disagree"), (3, "neither agree nor disagree"),
		   (4, "agree"), (5,  "strongly agree")]


class Annotation(models.Model):
	rater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	certainty = IntegerRangeField(min_value=1, max_value=5,
								  help_text="How certain are you regarding your annotation? 1 = uncertain, 5 = very certain")
	comment = models.TextField(max_length=1000, blank=True, help_text="Do you have any comment regarding your annotation? Is something unclear in the sentence which influence your annotation?")
	created_at = models.DateTimeField(auto_now_add=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	finished_at = models.DateTimeField(auto_now=True, blank=True)
	duration = models.DurationField(default=datetime.timedelta(), blank=True)

	class Meta:
		abstract = True


class Transformation(Annotation):
	# todo: connect to sentence and tokens of data model which are affected by transformation
	list_transactions = [("split", "Sentence Split"),
						 ("merge", "Merging Sentences"),
						 ("substitution", "Lexical substitution of a word"),
						 ("deletion", "Deletion of words or phrases"),
						 ("verbal changes", "Verbal changes"),
						 ("insert", "Add new words, phrases or clauses"),
						 ("reorder", "reorder phrases, clauses or complete sentence structure"),
						 ("no", "no operation")
						 ]
	transformation = models.CharField(max_length=100, blank=True)  # choices=list_transactions,
	sub_transformation = models.CharField(max_length=100, blank=True)

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
	transformation_level = models.CharField(max_length=100, blank=True)  # choices=[("par", "paragraph"), ("sent", "sentence"), ("phrase", "phrase"), ("word", "word")],
	simple_tokens = models.ManyToManyField("data.Token", related_name="simple_tokens")
	complex_tokens = models.ManyToManyField("data.Token", related_name="complex_tokens")

	def __str__(self):
		return self.transformation_level + '_' + self.transformation + '_' + str(self.id)


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

	grammaticality_simple = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_grammaticality.format("simplified"))
	grammaticality_original = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_grammaticality.format("original"))
	simplicity = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_simpler)
	structural_simplicity = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_structural)
	lexical_simplicity = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_lexical)
	simplicity_original = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_simplicity.format("original"))
	simplicity_simple = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_simplicity.format("simplified"))
	meaning_preservation = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_meaning_preservation)
	information_gain = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_information_gain)
	coherence_original = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_coherence.format("original"))
	coherence_simple = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_coherence.format("simplified"))
	ambiguity_original = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_ambiguity.format("original"))
	ambiguity_simple = models.IntegerField(choices=LIKERT_CHOICES, help_text=help_text_ambiguity.format("simplified"))
	# simplicity_gain = IntegerRangeField(min_value=0, max_value=100, help_text="How many sucessful lexical or syntactical transformations occured in the simplification?")

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
