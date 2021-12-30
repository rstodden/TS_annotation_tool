from django.db import models
import TS_annotation_tool.utils
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Annotator(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	age = models.IntegerField(blank=True, null=True)
	gender = models.CharField(max_length=10, choices=TS_annotation_tool.utils.gender, blank=True, null=True)
	native_language = models.CharField(max_length=8, choices=TS_annotation_tool.utils.LANGUAGE_CHOICES,blank=True, null=True)
	highest_education_level = models.CharField(max_length=250, choices=TS_annotation_tool.utils.education_level,blank=True, null=True)
	language_level_de = models.CharField(max_length=250, choices=TS_annotation_tool.utils.personal_language_level,blank=True, null=True)
	literacy_level = models.CharField(max_length=250, choices=TS_annotation_tool.utils.literacy_levels, blank=True, null=True)
	training_in_linguistics = models.BooleanField(null=True)
	training_in_simple_language = models.BooleanField(null=True)
	# ethnic_origin = models.CharField(choices={"white":"white", "black":"black", "oriental/asian": "oriental/asian", "asian_pacific_islander": "Asian Pacific Islander"})


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
	if created:
		Annotator.objects.create(user=instance)
	instance.annotator.save()
