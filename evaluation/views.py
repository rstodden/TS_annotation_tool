import pandas as pd
import rating.models
import data.models
import alignment.models
from nltk import agreement
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import user_passes_test
# from django.forms.models import model_to_dict
from datetime import datetime
import io
import os
import zipfile
import numpy
import TS_annotation_tool.utils


def export_rating():  #output_path
	# using same export format as proposed in Alva-Manchego etal. (2020) https://www.aclweb.org/anthology/2020.acl-main.424.pdf
	result_frame = pd.DataFrame(
		columns=["original", "simplification", "original_sentence_id", "aspect", "worker_id", "rating"])
	i = 0
	non_aspect_fields = ['pair', 'id', 'certainty', 'comment', 'created_at', 'updated_at', 'finished_at', 'duration',
						 'rater']
	aspects = [model_field for model_field in alignment.models.Rating._meta.get_fields() if
			   model_field.name not in non_aspect_fields]
	for pair in alignment.models.Pair.objects.all():
		for pair_rating in pair.rating.all():
			original = " ".join(pair.complex_elements.values_list("original_content", flat=True))
			simplification = " ".join(pair.simple_elements.values_list("original_content", flat=True))
			original_sentence_id = pair.pair_identifier
			worker_id = pair_rating.rater.id
			for field in aspects:
				result_frame.loc[i] = [original, simplification, original_sentence_id, field.name, worker_id, field.value_from_object(pair_rating)]
				i += 1
			i += 1
		i += 1
	return result_frame


def get_automatic_transformations():
	columns = ["original", "simplification", "original_sentence_id", "transformation_level", "transformation",
			   "subtransformation", "old text", "new_text", "worker_id"]
	automatic_transformations = list()
	for doc_pair in data.models.DocumentPair.objects.all():
		simple_sentences = doc_pair.simple_document.sentences.all()  # values_list("original_content", flat=True)
		complex_sentences = doc_pair.complex_document.sentences.all()  # values_list("original_content", flat=True)
		automatic_transformations.extend(get_transformation_no_change(simple_sentences, complex_sentences, doc_pair.id))
		if doc_pair.sentence_alignment_pair.exists():
			print("# todo")  # todo: automatic insertion and deletion
			# automatic_transformations.extend(get_transformation_insertion(simple_sentences))
			# automatic_transformations.extend(get_transformation_deletion(complex_sentences, doc_pair))
	return automatic_transformations


def get_transformation_no_change(simple_sentences, complex_sentences, doc_id):
	list_no_changes = list()
	old_text, new_text = "", ""
	worker_id = "0_auto"  # automated annotated
	transformation_level = "sentence"
	transformation = "no_operation"
	sub_transformation = ""

	simple_sentences_content = [sent.original_content for sent in simple_sentences]
	for complex_sentence in complex_sentences:
		if complex_sentence.original_content in simple_sentences_content:
			original = complex_sentence.original_content
			simplification = complex_sentence.original_content
			list_no_changes.append([original, simplification, complex_sentence.id,
								   transformation_level,
								   transformation,
								   sub_transformation,
								   old_text, new_text, worker_id])
	return list_no_changes


# def get_transformation_deletion(complex_sentences, doc_pair):
# 	list_deletions = ()
# 	transformation_level = "paragraph"
# 	transformation = "deletion"
# 	sub_transformation = ""
# 	new_text = ""
# 	worker_id = "_auto"  # automated annotated
# 	# todo pay attention to user
# 	# todo: get all complex sentences ehich have no complex element and add user?
# 	anno = doc_pair.annotator
# 	print(doc_pair)
# 	for annotator_of_doc_pair in doc_pair.annotator.all():
# 		for doc_pair_of_one_annotator in doc_pair.filter(annotator=annotator_of_doc_pair):
# 			print(doc_pair_of_one_annotator)
#
# 	# for complex_sentence in complex_sentences:
# 	# 	for alignment_pair in complex_sentence.complex_element.all():
# 	# 		print("complex", complex_sentence.id, alignment_pair.annotator.all())
# 	return list_deletions
#
#
# def get_transformation_insertion(simple_sentences):
# 	list_insertions = ()
# 	transformation_level = "paragraph"
# 	transformation = "insertion"
# 	sub_transformation = ""
# 	old_text = ""
# 	worker_id = "_auto"  # automated annotated
# 	for simple_sentence in simple_sentences:
# 		if not simple_sentence.simple_element.exists():
# 			print("insert", simple_sentence.id, simple_sentence.simple_element.annotator.all())
# 	return list_insertions


def export_transformation():
	result_frame = pd.DataFrame(
		columns=["original", "simplification", "original_sentence_id", "transformation_level", "transformation",
				 "subtransformation", "old text", "new_text", "worker_id"])
	i = 0
	for pair in alignment.models.Pair.objects.all():
		for pair_transformations in pair.transformation_of_pair.all():
			original = " ".join(pair.complex_elements.values_list("original_content", flat=True))
			simplification = " ".join(pair.simple_elements.values_list("original_content", flat=True))
			original_sentence_id = pair.pair_identifier
			worker_id = pair_transformations.rater.id
			old_text = ' '.join(pair_transformations.complex_token.values_list("text", flat=True))
			new_text = ' '.join(pair_transformations.simple_token.values_list("text", flat=True))
			result_frame.loc[i] = [original, simplification, original_sentence_id,
								   pair_transformations.transformation_level,
								   pair_transformations.transformation,
								   pair_transformations.sub_transformation,
								   old_text, new_text, worker_id]
			i += 1
		i += 1
	for no_change_pair in get_automatic_transformations():
		result_frame.loc[i] = no_change_pair
		i += 1
	return result_frame


def export_alignment(user, corpus):
	"""create one simple and complex file per annotator. The simple and the complex file contains all alignments no matter their domain or corpus."""
	# todo: add sources and copyright information to texts!
	corpus_name = "DEplain"
	file_names = list()
	if user:
		for rater in set(data.models.DocumentPair.objects.values_list("annotator", flat=True)):
			rater_str = ".rater." + str(rater)
			if not corpus:
				output_text_simple = ""
				output_text_complex = ""
				file_name_complex = corpus_name + ".orig" + rater_str + ".txt"
				file_name_simple = corpus_name + ".simp" + rater_str + ".txt"
				file_names.append(file_name_simple)
				file_names.append(file_name_complex)
				for document_pair in data.models.DocumentPair.objects.filter(annotator=rater):
					for alignment in document_pair.sentence_alignment_pair.filter(annotator=rater):
						output_text_simple += " ".join(alignment.simple_elements.values_list("original_content", flat=True)) + "\n"
						output_text_complex += " ".join(alignment.complex_elements.values_list("original_content", flat=True)) + "\n"

				with open(file_name_complex, "w") as f:
					f.write(output_text_complex)
				with open(file_name_simple, "w") as f:
					f.write(output_text_simple)
			else:
				for corpus_obj in data.models.Corpus.objects.all():
					file_name_complex = corpus_obj.name + ".orig" + rater_str + ".txt"
					file_name_simple = corpus_obj.name + ".simp" + rater_str + ".txt"
					output_text_simple = ""
					output_text_complex = ""
					for document_pair in data.models.DocumentPair.objects.filter(annotator=rater, corpus=corpus_obj):
						for alignment in document_pair.sentence_alignment_pair.filter(annotator=rater):
							output_text_simple += " ".join(alignment.simple_elements.values_list("original_content", flat=True)) + "\n"
							output_text_complex += " ".join(alignment.complex_elements.values_list("original_content", flat=True)) + "\n"
					if output_text_complex != "":
						with open(file_name_complex, "w") as f:
							f.write(output_text_complex)
						file_names.append(file_name_complex)

					if output_text_simple != "":
						with open(file_name_simple, "w") as f:
							f.write(output_text_simple)
						file_names.append(file_name_simple)
	return generate_zip_file(file_names)

def gather_all_data(rater):
	transformation_level = sorted(TS_annotation_tool.utils.transformation_dict.keys())
	columns = ["original", "simplification", "original_sentence_id", "domain", "language_level_original",
			   "language_level_simple", "grammaticality_original", "grammaticality_simple",
			   "simplicity", "simplicity_original", "simplicity_simple", "structural_simplicity", "lexical_simplicity",
			   "meaning_preservation", "information_gain", "coherence_original", "coherence_simple",
			   "ambiguity_original", "ambiguity_simple",
			   *TS_annotation_tool.utils.transformation_list]
	result_frame = pd.DataFrame(columns=columns)
	i = 0
	for pair in alignment.models.Pair.objects.filter(annotator=rater):
		#for pair_transformations in pair.transformation_of_pair.all():
		original = " ".join(pair.complex_elements.values_list("original_content", flat=True))
		simplification = " ".join(pair.simple_elements.values_list("original_content", flat=True))
		original_sentence_id = pair.pair_identifier
		values = [original, simplification, original_sentence_id, pair.document_pair.complex_document.domain,
				  pair.document_pair.complex_document.level, pair.document_pair.simple_document.level]
		# add malformed info, license
		if pair.rating.filter(rater=rater):
			ratings = pair.rating.filter(rater=rater)
			values.extend([ratings[0].grammaticality_original,
								   ratings[0].grammaticality_simple,
								   ratings[0].simplicity,
								   ratings[0].simplicity_original,
								   ratings[0].simplicity_simple,
								   ratings[0].structural_simplicity,
								   ratings[0].lexical_simplicity,
								   ratings[0].meaning_preservation,
								   ratings[0].information_gain,
								   ratings[0].coherence_original,
								   ratings[0].coherence_simple,
								   ratings[0].ambiguity_original,
								   ratings[0].ambiguity_simple,
						   ])
		else:
			values.extend([numpy.nan]*13)

		if pair.transformation_of_pair.filter(rater=rater):
			for trans_level in transformation_level:
				if pair.transformation_of_pair.filter(transformation_level=trans_level, rater=rater):
					values.append(len(pair.transformation_of_pair.filter(transformation_level=trans_level, rater=rater)))
				else:
					values.append(0)
				for trans in sorted(TS_annotation_tool.utils.transformation_dict[trans_level]):
					if pair.transformation_of_pair.filter(transformation_level=trans_level, transformation=trans, rater=rater):
						values.append(len(pair.transformation_of_pair.filter(transformation=trans, rater=rater)))
					else:
						values.append(0)
					for sub_trans in sorted(TS_annotation_tool.utils.transformation_dict[trans_level][trans]):
						if pair.transformation_of_pair.filter(transformation_level=trans_level, transformation=trans, sub_transformation=sub_trans, rater=rater):
							values.append(len(pair.transformation_of_pair.filter(sub_transformation=sub_trans, rater=rater)))
						else:
							values.append(0)
		else:
			values.extend([numpy.nan]*71)
		result_frame.loc[i] = values
		i += 1
	return result_frame


def export_all(user):
	corpus_name = "DEasy"
	file_names = list()
	if user:
		for rater in set(data.models.DocumentPair.objects.values_list("annotator", flat=True)):
			rater_str = ".rater." + str(rater)
			# if not corpus:
			file_name = corpus_name + "." + rater_str + ".csv"
			file_names.append(file_name)
			output_frame = gather_all_data(rater)
			output_frame.to_csv(file_name)
	return generate_zip_file(file_names)

def generate_zip_file(filenames):
	zip_subdir = "alignments_"+str(datetime.today().strftime('%Y-%m-%d'))
	zip_filename = zip_subdir+".zip"
	buffer_zip = io.BytesIO()
	zf = zipfile.ZipFile(buffer_zip, "w")
	for fpath in filenames:
		fdir, fname = os.path.split(fpath)
		zip_path = os.path.join(zip_subdir, fname)
		zf.write(fpath, zip_path)
		os.remove(fpath)
	zf.close()
	response = HttpResponse(buffer_zip.getvalue())
	response['Content-Type'] = 'application/x-zip-compressed'
	response['Content-Disposition'] = 'attachment; filename='+zip_filename
	return response


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
		elif "export_alignment_per_user" in request.POST:
			return export_alignment(user=True, corpus=False)
		elif "export_alignment_per_corpus_and_user" in request.POST:
			return export_alignment(user=True, corpus=True)
		elif "export_transformation" in request.POST:
			output_frame = export_transformation()
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="human_ratings_ts.csv"'
			output_frame.to_csv(path_or_buf=response)
			return response
		# elif "repair_sentence" in request.POST:
		# 	data.models.repair_original_text()
		elif "export_all_in_csv_per_use" in request.POST:
			return export_all(user=True)
		elif "get_iaa" in request.POST:
			iaa_meaning = get_inter_annotator_agreement("meaning_preservation")
			iaa_simplicity = get_inter_annotator_agreement("simplicity")
			iaa_grammaticality = get_inter_annotator_agreement("grammaticality")
			return render(request, 'evaluation/iaa.html', {"iaa_meaning": iaa_meaning, "iaa_simplicity": iaa_simplicity,
														   "iaa_grammaticality": iaa_grammaticality,
														   "title": "Evaluation - Text Simplification Annotation Tool"})
	return render(request, 'evaluation/home.html', {"title": "Evaluation - Text Simplification Annotation Tool"})


# @user_passes_test(lambda u: u.is_superuser)
# def iaa(request):
# 	"""
# 	show inter annotator agreement
# 	"""
# 	return render(request, 'evaluation/iaa.html')




