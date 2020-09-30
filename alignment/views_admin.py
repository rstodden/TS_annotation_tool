import pandas as pd
from .models import AlignmentPair, Assessment
import sklearn.metrics
import statsmodels.stats.inter_rater
import collections
from django.db.models import Count
from nltk import agreement

def export_rating(output_path):
	# using same export format as proposed in Alva-Manchego etal. (2020) https://www.aclweb.org/anthology/2020.acl-main.424.pdf
	result_frame = pd.DataFrame(
		columns=["original", "simplification", "original_sentence_id", "aspect", "worker_id", "rating"])
	i = 0
	for pair in AlignmentPair.objects.all():
		original = AlignmentPair.objects.get(id=pair.id).complex_element.original_content
		simplification = AlignmentPair.objects.get(id=pair.id).simple_element.original_content
		original_sentence_id = pair.pair_identifier
		worker_id = AlignmentPair.objects.get(id=pair.id).assessment.rater.id
		aspects = ["fluency", "meaning", "simplicity"]
		fluency_rating = AlignmentPair.objects.get(id=pair.id).assessment.grammaticality
		meaning_rating = AlignmentPair.objects.get(id=pair.id).assessment.meaning_preservation
		simplicity_rating = AlignmentPair.objects.get(id=pair.id).assessment.simplicity
		for aspect, rating in zip(aspects, [fluency_rating, meaning_rating, simplicity_rating]):
			result_frame.loc[i] = [original, simplification, original_sentence_id, aspect, worker_id, rating]
			i += 1


	result_frame.to_csv(output_path, sep=",", encoding="utf-8", index=False)
	return result_frame


def get_inter_annotator_agreement(aspect):
	# extract all raters
	list_rater_ids = Assessment.objects.order_by().values_list('rater_id', flat=True).distinct()
	list_pair_identifier = AlignmentPair.objects.order_by().values_list('pair_identifier', flat=True).distinct()

	output_list = [list(list_pair_identifier)]
	for id_rater in list_rater_ids:
		inner_list = list()
	# print("number ids", len(AlignmentPair.objects.order_by().values_list('pair_identifier', flat=True).distinct()))
		for pair_id in list_pair_identifier:
			relevant_object = AlignmentPair.objects.filter(annotator_id=id_rater, pair_identifier=pair_id)
			if relevant_object:
				inner_list.append(getattr(relevant_object[0].assessment, aspect))
			else:
				inner_list.append(None)
		output_list.append(inner_list)
	# outputlist: values only for meaning_preservation. first row object identifiers of pairs, row per annotator. values are ratings per record with missing values
	output = list()
	for n, coder in enumerate(output_list):
		for i in range(len(coder)):
			output.append([n + 1, i, coder[i]])
	ratingtask = agreement.AnnotationTask(data=output)
	# following the example of https://learnaitech.com/how-to-compute-inter-rater-reliablity-metrics-cohens-kappa-fleisss-kappa-cronbach-alpha-kripndorff-alpha-scotts-pi-inter-class-correlation-in-python/
	return ratingtask.alpha()

for aspect in ["meaning_preservation", "simplicity", "grammaticality"]:
	print('Krippendorff\'s alpha for', aspect, ':', get_inter_annotator_agreement(aspect))
export_rating("export_data.csv")