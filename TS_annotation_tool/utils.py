from django.db import models
from settings_annotation.config_languages import LANGUAGE_CHOICES
from settings_annotation.config_rating import LIKERT_CHOICES, LIKERT_CHOICES_NEUTRAL, rating_aspects_dict, rating_aspects_neutral
from settings_annotation.config_transformation import transformation_dict, transformation_list, tuple_list_choices_transformation, tuple_list_choices_subtransformation, tuple_list_transformation_level

rating_aspects = sorted(list(rating_aspects_dict.keys()))

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
					("MIT", "MIT")
					 )

language_level_list = (
				   ("---", "---"),
				   ("a1", "Easy-to-read Language (A1, Leichte Sprache)"),
				   ("a2", "Plain Language (A2-B1, Einfache Sprache)"),
				   ("b2", "Simplified Language (B2)"),
   				   ("c1", "(C1)"),
				   ("c2", "Everyday Language (C2)")
					)
license_limits = {"not_allowed": {"save_use": 0.75, "save_use_share_with_password": 0.15}}

gender = (("---", "---"), ("male","male"), ("female", "female"), ("divers", "divers"))


# based on https://www.cmu.edu/common-cold-project/measures-by-study/psychological-and-social-constructs/objective-socioeconomic-status-measures/pcs3_ses.pdf

education_level = (
	("---", "---"),
	("no", "Didn’t Finish High School"),
	("high_school", "High School Graduate or General Education Diploma"),
	("high_school_program", "Completed High School and a technical/vocational program"),
	("bachelor", "College graduate (BA or BS)"),
	("master", "Master’s degree (or other post-graduate training)"),
	("doctoral", "Doctoral degree (PhD., MD, EdD, DVM, DDS, JD, etc)")
)

personal_language_level = (
	("---", "---"),
	("a1", "A1, Beginner"),
	("a2", "A2, Elementary"),
	("b1", "B1, Intermediate"),
	("b2", "B2, Upper Intermediate"),
	("c1", "C1, Advanced"),
	("c2", "C2, Proficiency"),
	("native", "Native Language"),
)

literacy_levels = (
	("---", "---"),
	('level_0', 'Below Level 1'),
	('level_1', 'Level 1'),
	('level_2', 'Level 2'),
	('level_3', 'Level 2'),
	("level_4", "Level 4"),
	("level_5", "Level 5")
)

class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)

	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value': self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)

