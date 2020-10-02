import pandas as pd
import rating.models
import alignment.models
from nltk import agreement
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import user_passes_test


def export_rating():  #output_path
	# using same export format as proposed in Alva-Manchego etal. (2020) https://www.aclweb.org/anthology/2020.acl-main.424.pdf
	result_frame = pd.DataFrame(
		columns=["original", "simplification", "original_sentence_id", "aspect", "worker_id", "rating"])
	i = 0
	for pair in alignment.models.Pair.objects.all():
		for pair_rating in pair.rating.all():
			original = " ".join(pair.complex_element.all().values_list("original_content", flat=True))
			simplification = " ".join(pair.simple_element.all().values_list("original_content", flat=True))
			original_sentence_id = pair.pair_identifier
			worker_id = pair_rating.rater.id
			aspects = ["fluency", "meaning", "simplicity"]
			fluency_rating = pair_rating.grammaticality
			meaning_rating = pair_rating.meaning_preservation
			simplicity_rating = pair_rating.simplicity
			for aspect, rating in zip(aspects, [fluency_rating, meaning_rating, simplicity_rating]):
				result_frame.loc[i] = [original, simplification, original_sentence_id, aspect, worker_id, rating]
				i += 1
			i += 1
		i += 1
	return result_frame


def get_inter_annotator_agreement(aspect):
	# extract all raters
	list_rater_ids = rating.models.Rating.objects.order_by().values_list('rater_id', flat=True).distinct()
	list_pair_identifier = alignment.models.Pair.objects.order_by().values_list('pair_identifier', flat=True).distinct()

	output_list = [list(list_pair_identifier)]
	for id_rater in list_rater_ids:
		inner_list = list()
	# print("number ids", len(Pair.objects.order_by().values_list('pair_identifier', flat=True).distinct()))
		for pair_id in list_pair_identifier:
			relevant_object = alignment.models.Pair.objects.filter(annotator_id=id_rater, pair_identifier=pair_id)
			if relevant_object:
				inner_list.append(getattr(relevant_object[0].rating, aspect))
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


@user_passes_test(lambda u: u.is_superuser)
def export(request):
	if request.method == "POST":
		if "export_rating" in request.POST:
			output_frame = export_rating()
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="human_ratings_ts.csv"'
			output_frame.to_csv(path_or_buf=response)
			return response
		elif "get_iaa" in request.POST:
			iaa_meaning = get_inter_annotator_agreement("meaning_preservation")
			iaa_simplicity = get_inter_annotator_agreement("simplicity")
			iaa_grammaticality = get_inter_annotator_agreement("grammaticality")
			return render(request, 'evaluation/iaa.html', {"iaa_meaning": iaa_meaning, "iaa_simplicity": iaa_simplicity,
														   "iaa_grammaticality": iaa_grammaticality})
	return render(request, 'evaluation/home.html', {})


# @user_passes_test(lambda u: u.is_superuser)
# def iaa(request):
# 	"""
# 	show inter annotator agreement
# 	"""
# 	return render(request, 'evaluation/iaa.html')




