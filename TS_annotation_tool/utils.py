from django.db import models

list_licenses = (
					("to_add", "to_add"),
					("not_allowed", "not_allowed"),
					("save_use", "save_use"),
					("save_use_share", "save_use_share"),
					("save_use_share_with_password", "save_use_share_with_password"),
					("CC_BY_NC_SA_DE_2", "CC_BY_NC_SA_DE_2"),
					("CC_BY_NC_DE_3", "CC_BY_NC_DE_3"),
					("CC_BY_NC_SA_DE_3", "CC_BY_NC_SA_DE_3"),
					("CC_BY_NC_ND_DE_3", "CC_BY_NC_ND_DE_3"),
					("CC_BY_ND_DE_3", "CC_BY_ND_DE_3"),
					("CC_BY_SA_DE_3", "CC_BY_SA_DE_3"),
					("CC_BY_SA_3", "CC_BY_SA_3"),
					("CC_BY_4", "CC_BY_4"),
					("CC_BY_NC_ND_4", "CC_BY_NC_ND_4"),
					("CC_BY_NC_4", "CC_BY_NC_4"),
					("CC_BY_NC_SA_4", "CC_BY_NC_SA_4"),
					 )

language_level_list = (("a1", "Leichte Sprache"),
				   ("a2", "Einfache Sprache"),
				   ("b2", "Vereinfachte Sprache"),
				   ("c2", "Alltagssprache")
					)


class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)

	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value': self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)


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
						    "no_operation": [],
					   		},
					   "paragraph": {
						   "reorder": ["sentence-order-changed", "other"],
						   "merge": [],
						   "deletion": [],
						   "insert": ["explanation", "examplification", "other"]
					   }
				   }

keys_list_transformation = sorted([list(trans.keys()) for level, trans in transformation_dict.items()])
list_choices_transformation = sorted(list(set([item for sublist in keys_list_transformation for item in sublist])))
values_list_subtransformations = sorted([list(transformation_dict[trans].values()) for trans in transformation_dict.keys()])
nested_list_choices_subtransformation = sorted([item for sublist in values_list_subtransformations for item in sublist])
list_choices_subtransformation = sorted(list(set([item for sublist in nested_list_choices_subtransformation for item in sublist])))
tuple_list_choices_transformation = [(trans, trans) for trans in list_choices_transformation]
tuple_list_choices_subtransformation = [(subtrans, subtrans) for subtrans in list_choices_subtransformation]
tuple_list_transformation_level = [(item, item) for item in transformation_dict.keys()]


LIKERT_CHOICES = [(1, "strongly diasgree"), (2, "disagree"), (3, "neither agree nor disagree"),
		   (4, "agree"), (5,  "strongly agree")]
LIKERT_CHOICES_NEUTRAL = [(-2, "strongly diasgree"), (-1, "disagree"), (0, "neither agree nor disagree"),
		   (1, "agree"), (2,  "strongly agree")]

