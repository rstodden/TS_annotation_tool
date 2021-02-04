from django.db import models
import TS_annotation_tool.utils


# Create your models here.
class ChangeLog(models.Model):
	finished = models.BooleanField(default=False)
	topic = models.CharField(max_length=250, choices=(("General", "General"),
														("Transformations", "Transformations"),
														("Alignment", "Alignment"),
														("Ratings", "Ratings"),
														("Transformations and Ratings", "Transformations and Raings"),
														("Data", "Data"),
														("Export", "Export"),
														("Simplification", "Simplification")))
	comment = models.TextField(max_length=1000)
	headline = models.TextField(max_length=288)
	created_at = models.DateTimeField(auto_now_add=True)
	finished_at = models.DateTimeField(null=True, blank=True)
	priority = TS_annotation_tool.utils.IntegerRangeField(min_value=1, max_value=5, blank=True, null=True,
														  help_text="Select 1 for highest priority and 5 for lowest priority.")

