"""
add or remove transformations. After your changes, run  `python manage.py makemigrations` and `python manage.py migrate`
"""

transformation_dict = {"word": {
							"deletion": ["discourse_markers", "abbreviations", "filter_words", "other"],
							"lexical_substitution": ["compound_segmentation", "more_frequent_word", "abbreviation",
													 "anaphora", "shorter_word", "synonym", "hyponym", "hypernym",
													 "nominalization", "metaphor_resolution", "number", "date", "other"],
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

transformation_list = list()
for transformation_level in sorted(transformation_dict.keys()):
	transformation_list.append(transformation_level+"#")
	for transformation in sorted(transformation_dict[transformation_level]):
		transformation_list.append(transformation_level+"#"+transformation+"*")
		for sub_transformation in sorted(transformation_dict[transformation_level][transformation]):
			transformation_list.append(transformation_level+"#"+transformation+"*"+sub_transformation+"+")
