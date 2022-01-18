from django.db import models
from data.models import popover_html

# Create your models here.
class MetaData(models.Model):
	"""
	based on HuggingFace Data Sheets https://github.com/huggingface/datasets/blob/master/templates/README_guide.md
	"""
	summary = models.TextField(help_text=popover_html("Please summarize your data set briefly. "))
	dataset_creation = models.TextField(help_text=popover_html("Please summarize your data set briefly. "))
	language_description = models.TextField(help_text=popover_html(
		"Which texts are included? Why and with which motivate are the texts selected?"))
	domain_decription = models.TextField(help_text=popover_html("Which domains are included?"))
	annotation_process_description = models.TextField(help_text=popover_html("Describe the annotation process."))
	annotator_description = models.TextField(help_text=popover_html("Describe the annotators."))
	sensitive_data_description = models.TextField()
	bias_description = models.TextField()
	social_impact_description = models.TextField()
	limitations_description = models.TextField()
	license_description = models.TextField()
	curator_description = models.TextField()
	citation_description = models.TextField()
	contribution_description = models.TextField()
	task_description = models.TextField()
	homepage = models.CharField(max_length=1)
	repository = models.CharField(max_length=1)
	paper = models.CharField(max_length=1)
	leaderboard = models.CharField(max_length=1)
	point_of_contact = models.CharField(max_length=1)
	data_fields_description = models.TextField()
	language_producers_description = models.TextField()
	collection_description = models.TextField()