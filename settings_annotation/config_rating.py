"""
change rating scale and delete or add rating aspects.
Make sure to save all your previous ratings before changing.
After your changes, run  `python manage.py makemigrations` and `python manage.py migrate`.
"""

LIKERT_CHOICES = [(1, "strongly disagree"), (2, "disagree"), (3, "neither agree nor disagree"),
		   (4, "agree"), (5,  "strongly agree")]
LIKERT_CHOICES_NEUTRAL = [(-2, "strongly disagree"), (-1, "disagree"), (0, "neither agree nor disagree"),
		   (1, "agree"), (2,  "strongly agree")]

# you can replace upper lines with these lines to use 7-point-scale than 5-point-scale
# LIKERT_CHOICES = [(1, "strongly disagree"), (2, "disagree"), (3, "somewhat disagree"),
# 					(4, "neither agree nor disagree"), (5, "somewhat agree"), (6, "agree"), (7,  "strongly agree")]
# LIKERT_CHOICES_NEUTRAL = [(-3, "strongly disagree"), (-2, "disagree"), (-1, "somewhat disagree"),
# 					(0, "neither agree nor disagree"), (1, "somewhat agree"), (2, "agree"), (3,  "strongly agree")]


# you can delete unwanted aspects
# add or delete items to/of `rating_aspects_neutral' for a scale ranging from -n to +n
help_text_grammaticality = "The {} sentence is fluent, there are no grammatical errors."
help_text_simplicity = "The {} sentence is easy to understand."
help_text_coherence = "The {} sentence is understandable without any preceeding or following sentence, e.g., there are no pronouns or connectives."
help_text_ambiguity = "The {} sentence is ambiguous. It can be read in different ways."
help_text_simpler = "The simplified sentence is easier to understand than the original sentence."
help_text_meaning_preservation = "The simplified sentence adequately expresses the meaning of the original sentence, perhaps omitting the least important information."
help_text_structural = "The structure of the simplified sentence is easier to understand than the structure of the original sentence."
help_text_lexical = "The words of the simplified sentence are easier to understand than the words of the original sentence."
help_text_information_gain = "In the simplified sentence, information is added or get more explicit compared to the original sentence."

rating_aspects_dict = {
	"meaning_preservation": help_text_meaning_preservation,
	"information_gain": help_text_information_gain,
	"simplicity": help_text_simpler,
	#"structural_simplicity": help_text_structural,
	#"lexical_simplicity": help_text_lexical,
	"simplicity_original": help_text_simplicity.format("original"),
	"simplicity_simple": help_text_simplicity.format("simplified"),
	"grammaticality_simple": help_text_grammaticality.format("simplified"),
	"grammaticality_original": help_text_grammaticality.format("original"),
	"coherence_original": help_text_coherence.format("original"),
	"coherence_simple": help_text_coherence.format("simplified"),
	# "ambiguity_original": help_text_ambiguity.format("original"),
	# "ambiguity_simple": help_text_ambiguity.format("simplified")
}

rating_aspects_neutral = [
	"grammaticality_simple",
	'grammaticality_original',
	'simplicity',
	'structural_simplicity',
	'lexical_simplicity',
	'information_gain'
]