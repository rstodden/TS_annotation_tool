from django.db import models
from django.contrib.auth.models import User


class Simplification(models.Model):
	original_content = models.TextField()
	corrected_content = models.TextField(blank=True)
	level_list = (("a1", "Leichte Sprache"),
				   ("a2", "Einfache Sprache"),
				   ("b2", "Vereinfachte Sprache"),
				   ("c2", "Alltagssprache")
					)
	level = models.CharField(max_length=50, blank=True, choices=level_list)
	annotator = models.ManyToManyField(User)
