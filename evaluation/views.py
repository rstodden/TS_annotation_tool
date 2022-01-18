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
from django.db.models import Q
from django.contrib.auth.models import User
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa
from .forms import ExportAlignmentForm


def export_rating():  #output_path
	# using same export format as proposed in Alva-Manchego etal. (2020) https://www.aclweb.org/anthology/2020.acl-main.424.pdf
	result_frame = pd.DataFrame(
		columns=["original", "simplification", "original_id", "simplification_id", "aspect", "rater", "rating"])
	i = 0
	non_aspect_fields = ['pair', 'id', 'certainty', 'comment', 'created_at', 'updated_at', 'finished_at', 'duration',
						 'rater']
	aspects = [model_field for model_field in alignment.models.Rating._meta.get_fields() if
			   model_field.name not in non_aspect_fields]
	for pair in alignment.models.Pair.objects.all():
		for pair_rating in pair.rating.all():
			original, original_sentence_id, simplification, simplification_sentence_id, alignment_type = get_original_data(pair)
			worker_id = pair_rating.rater.id
			for field in aspects:
				result_frame.loc[i] = [original, simplification, original_sentence_id, simplification_sentence_id, field.name, worker_id, field.value_from_object(pair_rating)]
				i += 1
			i += 1
		i += 1
	return result_frame


def get_automatic_transformations():
	columns = ["original", "simplification", "original_sentence_id", "simplification_sentence_id", "transformation_level", "transformation",
			   "subtransformation", "old text", "new_text", "worker_id"]
	automatic_transformations = list()
	for doc_pair in data.models.DocumentPair.objects.all():
		if doc_pair.simple_document and doc_pair.complex_document:
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
			list_no_changes.append([original, simplification, complex_sentence.id, "",
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
		columns=["original", "simplification", "original_id", "simplification_id", "transformation_level", "transformation",
				 "subtransformation", "old text", "new_text", "rater"])
	i = 0
	for pair in alignment.models.Pair.objects.all():
		for pair_transformations in pair.transformation_of_pair.all():
			original, original_sentence_id, simplification, simplification_sentence_id, alignment_type = get_original_data(pair)
			worker_id = pair_transformations.rater.id
			old_text = ' '.join(pair_transformations.complex_token.values_list("text", flat=True))
			new_text = ' '.join(pair_transformations.simple_token.values_list("text", flat=True))
			result_frame.loc[i] = [original, simplification, original_sentence_id, simplification_sentence_id,
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

@user_passes_test(lambda u: u.is_superuser)
def export_all_in_csv_per_use(request):
	return export_all(user=True)


@user_passes_test(lambda u: u.is_superuser)
def export_meta_data(request):
	# todo: add sources and copyright information to texts!

	return render(request, 'todo.html')


@user_passes_test(lambda u: u.is_superuser)
def export_user_data(request):
	return render(request, 'todo.html')


@user_passes_test(lambda u: u.is_superuser)
def export_iaa_transformation(request):
	return render(request, 'todo.html')


@user_passes_test(lambda u: u.is_superuser)
def export_data_sheet(request):
	return render(request, 'todo.html')


@user_passes_test(lambda u: u.is_superuser)
def export_alignment_for_crf(request):
	print("export_alignment_for_crf")
	result_frame = get_alignment_for_crf(real_user=True)
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="alignments_for_crf.csv"'
	result_frame.to_csv(path_or_buf=response)
	return response


@user_passes_test(lambda u: u.is_superuser)
def export_iaa_alignment(request):
	alignment_frame = get_alignment_for_crf(real_user=True, iaa=True)
	df_2_annotators, df_more_annotators = filter_df_by_annotator_number(alignment_frame)
	agreement_dict = get_iaa_alignment_dict(alignment_frame, df_2_annotators, df_more_annotators)
	return render(request, 'evaluation/iaa_alignment.html', {"iaa_dict": agreement_dict,
															 "title": "Inter Annotator Agreement - Text Simplification Annotation Tool"})


@user_passes_test(lambda u: u.is_superuser)
def export_iaa_rating(request):
	iaa_dict = dict()
	for aspect in TS_annotation_tool.utils.rating_aspects:
		print(aspect)
		iaa_dict[aspect] = get_inter_annotator_agreement_rating(real_user=False)
	return render(request, 'evaluation/iaa_rating.html', {"iaa_dict": iaa_dict,
														  "title": "Evaluation - Text Simplification Annotation Tool"})


@user_passes_test(lambda u: u.is_superuser)
def export_ratings_view(request):
	output_frame = export_rating()
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="human_ratings_ts.csv"'
	output_frame.to_csv(path_or_buf=response)
	return response


@user_passes_test(lambda u: u.is_superuser)
def export_transformations_view(request):
	output_frame = export_transformation()
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="human_ratings_ts.csv"'
	output_frame.to_csv(path_or_buf=response)
	return response


@user_passes_test(lambda u: u.is_superuser)
def export_alignment_view(request):
	if request.POST:
		form = ExportAlignmentForm(request.POST)
		if form.is_valid():
			return export_alignment(user=form.cleaned_data["per_user"],
									corpus=form.cleaned_data["per_corpus"],
									identical=form.cleaned_data["identical_pairs"],
									deletions=form.cleaned_data["deletions"],
									additions=form.cleaned_data["additions"],
									format=form.cleaned_data["format"]
									)
	else:
		form = ExportAlignmentForm()
	return render(request, 'evaluation/export_alignment.html', {"title": "Export Alignment - Text Simplification Annotation Tool",
																"form": form})


def export_alignment(user, corpus, identical=False, deletions=False, additions=False, format="parallel"):
	"""create one simple and complex file per annotator or per corpus or all in csv. The simple and the complex file contains all alignments no matter their domain or corpus."""
	corpus_name = "TS_anno_"
	print(identical, deletions, additions, user, corpus)
	file_names = list()
	output_df = export_csv()
	output_df_auto = export_not_aligned()
	for rater in set(data.models.DocumentPair.objects.values_list("annotator", flat=True)):
		if user:
			rater_str = ".rater." + str(rater)
			output_df = export_csv()
			output_df_auto = export_not_aligned()
		else:
			rater_str = ""
		output_text_simple_list, output_text_complex_list, output_text_meta_data = list(), list(), list()
		for corpus_obj in data.models.Corpus.objects.all():
			if corpus:
				file_name_complex = corpus_obj.name + ".orig" + rater_str + ".txt"
				file_name_simple = corpus_obj.name + ".simp" + rater_str + ".txt"
				file_name_meta_data = corpus_obj.name + ".meta" + rater_str + ".txt"
				file_name = corpus_obj.name + rater_str + ".csv"
				file_name_auto = corpus_obj.name + rater_str + "_auto.csv"
				output_text_simple_list, output_text_complex_list, output_text_meta_data = list(), list(), list()
				output_df = export_csv()
				output_df_auto = export_not_aligned()
			else:
				file_name_complex = corpus_name + ".orig" + rater_str + ".txt"
				file_name_simple = corpus_name + ".simp" + rater_str + ".txt"
				file_name_meta_data = corpus_name + ".meta" + rater_str + ".txt"
				file_name = corpus_name + rater_str + ".csv"
				file_name_auto = corpus_name + rater_str + "_auto.csv"
			for document_pair in data.models.DocumentPair.objects.filter(annotator=rater, corpus=corpus_obj):
				document_pair_id = document_pair.id
				if not document_pair.complex_document or not document_pair.simple_document:
					continue
				domain, complex_level, simple_level, license, author, url, access_date = corpus_obj.domain, document_pair.complex_document.level, document_pair.simple_document.level, corpus_obj.license, corpus_obj.author, document_pair.simple_document.url, document_pair.simple_document.access_date
				for alignment in document_pair.sentence_alignment_pair.filter(annotator=rater):
					original, original_id, simplification, simplification_id, alignment_type = get_original_data(alignment)
					if format == "parallel":
						output_text_simple_list.append(simplification)
						output_text_complex_list.append(original)
						output_text_meta_data.append("\t".join([original_id, simplification_id, str(document_pair_id), domain, complex_level, simple_level, license, author, url, str(access_date), str(rater)]))
					elif format == "csv":
						output_df = export_csv(rater, original, simplification, original_id,
									   simplification_id, document_pair_id, domain, complex_level, simple_level, license,
									   author, url, access_date, alignment=alignment_type, output_df=output_df)
			if format == "parallel" and len(output_text_simple_list) > 0 and len(output_text_complex_list) > 0:
				file_name_complex, file_name_simple, file_name_meta_data = export_txt(output_text_simple_list, output_text_complex_list, output_text_meta_data, file_name_complex, file_name_simple, file_name_meta_data)
				if file_name_simple not in file_names and file_name_complex not in file_names and file_name_meta_data not in file_names:
					file_names.extend([file_name_complex, file_name_simple, file_name_meta_data])
			elif format == "csv" and len(output_df) > 0:
				output_df.to_csv(file_name)
				if file_name not in file_names:
					file_names.append(file_name)
			if additions or deletions or identical:
				output_df_auto = export_not_aligned(rater, additions=additions, deletions=deletions, identical=identical, corpus=corpus_obj, output_df=output_df_auto)
				output_df_auto.to_csv(file_name_auto)
				if file_name_auto not in file_names:
					file_names.append(file_name_auto)
	return generate_zip_file(file_names)


def export_txt(output_text_simple_list, output_text_complex_list, output_text_meta_data, file_name_complex, file_name_simple, file_name_meta_data):
	with open(file_name_complex, "w") as f:
		for output_text_complex in output_text_complex_list:
			f.write(output_text_complex+"\n")
	with open(file_name_simple, "w") as f:
		for output_text_simple in output_text_simple_list:
			f.write(output_text_simple+"\n")
	with open(file_name_meta_data, "w") as f:
		for meta_data in output_text_meta_data:
			f.write(meta_data+"\n")
	return file_name_complex, file_name_simple, file_name_meta_data


def export_csv(rater_id=None, output_text_complex=None, output_text_simple=None, sent_id_complex=None, sent_id_simple=None, document_pair_id=None, domain=None, complex_level=None, simple_level=None, license=None, author=None, url=None, access_date=None, alignment=None, output_df=None):
	if type(output_df) != pd.DataFrame:
		output_df = pd.DataFrame(columns=["original", "simplification", "original_id", "simplification_id", "pair_id", "domain", "language_level_original",
			   "language_level_simple", "license", "author", "website", "access_date", "rater", "alignment"])
	else:
		values = [output_text_complex, output_text_simple, sent_id_complex, sent_id_simple, document_pair_id,
			  domain, complex_level, simple_level, license, author, url, access_date, rater_id, alignment]
		output_df.loc[len(output_df)] = values
	return output_df


def get_table_values(sent_id, alignment_type, doc_id, domain, complex_level, simple_level, license, author, url, access_date, simple_sent_id=None, rater=None):
	sent = data.models.Sentence.objects.get(id=sent_id)
	if alignment_type == "identical" and len(sent.tokens.all()) > 2:
		text = get_original_sent(sent, list())[0]
		# text_id = str(doc.id) + "-0-" + str(sent.paragraph_nr) + "-" + str(sent.sentence_nr)
		complex_text_id = str(doc_id) + "-1-" + str(sent.paragraph_nr) + "-" + str(sent.sentence_nr)
		simple_sent = data.models.Sentence.objects.get(id=simple_sent_id)
		simple_text_id = str(doc_id) + "-0-" + str(simple_sent.paragraph_nr) + "-" + str(simple_sent.sentence_nr)
		value_list = [text, text, complex_text_id, simple_text_id, "", domain, complex_level, simple_level, license, author, url, access_date, str(rater)+"_auto", "1:1 ("+alignment_type+")"]
		return value_list
	elif alignment_type == "deletion" and len(sent.tokens.all()) > 2:
		text = get_original_sent(sent, list())[0]
		text_id = str(doc_id) + "-1-" + str(sent.paragraph_nr) + "-" + str(sent.sentence_nr)
		text_id_simple = str(doc_id) + "-0-" + "x" + "-" + "x"
		value_list = [text, "", text_id, "", "", domain, complex_level, simple_level, license, author, url, access_date, str(rater)+"_auto", "1:0 ("+alignment_type+")"]
		return value_list
	elif alignment_type == "addition" and len(sent.tokens.all()) > 2:
		text = get_original_sent(sent, list())[0]
		text_id = str(doc_id) + "-0-" + str(sent.paragraph_nr) + "-" + str(sent.sentence_nr)
		text_id_complex = str(doc_id) + "-1-" + "x" + "-" + "x"
		value_list = ["", text, text_id_complex, text_id, "", domain, complex_level, simple_level, license, author, url, access_date, str(rater)+"_auto", "0:1 ("+alignment_type+")"]
		return value_list
	else:
		return None


def export_not_aligned(rater_id=None, identical=True, deletions=True, additions=True, corpus=None, output_df=None):
	if type(output_df) != pd.DataFrame:
		output_df = pd.DataFrame(columns=["original", "simplification", "original_id", "simplification_id", "pair_id", "domain", "language_level_original",
			   "language_level_simple", "license", "author", "website", "access_date", "rater", "alignment"])
	else:
		rater = User.objects.get(id=rater_id)
		i = 0
		for doc in data.models.DocumentPair.objects.filter(annotator=rater, complex_document__isnull=False, simple_document__isnull=False, corpus=corpus):
			simple_doc = doc.simple_document
			complex_doc = doc.complex_document
			domain, complex_level, simple_level, license, author, url, access_date = doc.corpus.domain, doc.complex_document.level, doc.simple_document.level, doc.corpus.license, doc.corpus.author, doc.simple_document.url, doc.simple_document.access_date
			identical_complex_sentences = complex_doc.sentences.filter(original_content__in=simple_doc.sentences.values_list("original_content", flat=True)).values_list("id", flat=True)
			identical_simple_sentences = simple_doc.sentences.filter(original_content__in=complex_doc.sentences.values_list("original_content", flat=True)).values_list("id", flat=True)
			if identical and identical_complex_sentences:
				for sent_id in identical_complex_sentences:
					complex_sent = data.models.Sentence.objects.get(id=sent_id)
					simple_sent_pair_id = None
					for simple_sent_id in identical_simple_sentences:
						if get_original_sent(data.models.Sentence.objects.get(id=simple_sent_id),list())[0] == get_original_sent(complex_sent, list())[0]:
							simple_sent_pair_id = simple_sent_id
					values = get_table_values(sent_id, "identical", doc.id, domain, complex_level, simple_level, license, author, url, access_date, simple_sent_pair_id, rater.id)
					if values:
						output_df.loc[i] = values
						i += 1
			not_annotated_complex = complex_doc.sentences.filter(~Q(complex_element__annotator=rater)).filter(~Q(id__in=identical_complex_sentences))  #.values_list("id", flat=True) # Q(complex_element__isnull=True) |
			not_annotated_simple = simple_doc.sentences.filter(~Q(simple_element__annotator=rater)).filter(~Q(id__in=identical_simple_sentences))  #.values_list("id", flat=True)
			if deletions and len(not_annotated_complex)/(len(complex_doc.sentences.all())-len(identical_complex_sentences)) <= 0.25:
				for sent_id in identical_complex_sentences:
					values = get_table_values(sent_id, "deletion", doc.id, domain, complex_level, simple_level, license, author, url, access_date, None, rater.id)
					if values:
						output_df.loc[i] = values
						i += 1
			if additions and (len(simple_doc.sentences.all())-len(identical_simple_sentences)) > 0 and len(not_annotated_simple)/(len(simple_doc.sentences.all())-len(identical_simple_sentences)) <= 0.25:
				for sent_id in identical_complex_sentences:
					values = get_table_values(sent_id, "addition", doc.id, domain, complex_level, simple_level, license, author, url, access_date, None, rater.id)
					if values:
						output_df.loc[i] = values
						i += 1
	# output_df.to_csv("media/not_aligned_sentences_"+corpus_name+"_"+str(rater_id)+".csv", encoding="utf-8")
	# response = HttpResponse(content_type='text/csv')
	# response['Content-Disposition'] = 'attachment; filename="not_aligned_sentences.csv"'
	# output_df.to_csv(path_or_buf=response)
	# return "media/not_aligned_sentences_"+str(rater_id)+".csv"
	return output_df


def get_original_sent(sent, output):
	if len(sent.original_content_repaired) >= 1:
		output.append(sent.original_content_repaired)
	else:
		output.append(sent.original_content)
	return output


def get_original_data(pair):
	original = list()
	simplification = list()
	original_id = ""
	simplification_id = ""
	n_simple, n_complex = len(pair.simple_elements.all()), len(pair.complex_elements.all())
	for complex_sent in pair.complex_elements.all():
		original = get_original_sent(complex_sent, original)
		if original_id:
			if not complex_sent.given_id:
				original_id += "|"+str(pair.document_pair.id) + "-1-" + str(complex_sent.paragraph_nr) + "-" + str(complex_sent.sentence_nr)
			else:
				original_id += "|"+complex_sent.given_id
		else:
			if not complex_sent.given_id:
				original_id = str(pair.document_pair.id) + "-1-" + str(complex_sent.paragraph_nr) + "-" + str(complex_sent.sentence_nr)
			else:
				original_id = complex_sent.given_id
	for simple_sent in pair.simple_elements.all():
		simplification = get_original_sent(simple_sent, simplification)
		if simplification_id:
			if not simple_sent.given_id:
				simplification_id += "|" + str(pair.document_pair.id) + "-0-" + str(simple_sent.paragraph_nr) + "-" + str(simple_sent.sentence_nr)
			else:
				simplification_id += "|" + simple_sent.given_id
		else:
			if not simple_sent.given_id:
				simplification_id = str(pair.document_pair.id) + "-0-" + str(simple_sent.paragraph_nr) + "-" + str(simple_sent.sentence_nr)
			else:
				simplification_id = simple_sent.given_id
	original = " ".join(original)
	simplification = " ".join(simplification)
	return original, original_id, simplification, simplification_id, str(n_complex)+":"+str(n_simple)


def gather_all_data(rater):
	transformation_level = sorted(TS_annotation_tool.utils.transformation_dict.keys())
	columns = ["original", "simplification", "original_id", "simplification_id", "pair_id", "domain", "language_level_original",
			   "language_level_simple", "license", "author", "website", "access_date", "rater", "alignment",
			   "malformed_complex", "malformed_simple",
			   "duration_rating",
			   *TS_annotation_tool.utils.rating_aspects,
			   # "duration_transformation",
			   *TS_annotation_tool.utils.transformation_list]
	print(len(columns), len(TS_annotation_tool.utils.rating_aspects), len(TS_annotation_tool.utils.transformation_list))
	result_frame = pd.DataFrame(columns=columns)
	i = 0
	for pair in alignment.models.Pair.objects.filter(annotator=rater):
		#for pair_transformations in pair.transformation_of_pair.all():
		original, original_id, simplification, simplification_id, alignment_type = get_original_data(pair)
		original_sentence_id = pair.pair_identifier
		malformed_original = 1 if len(pair.complex_elements.filter(malformed=True)) >= 1 else 0
		malformed_simple = 1 if len(pair.simple_elements.filter(malformed=True)) >= 1 else 0
		values = [original, simplification, original_id, simplification_id, original_sentence_id, pair.document_pair.complex_document.domain,
				  pair.document_pair.complex_document.level, pair.document_pair.simple_document.level,
				  pair.document_pair.corpus.license, pair.document_pair.corpus.author, pair.document_pair.corpus.home_page,
				  pair.document_pair.complex_document.access_date, rater, alignment_type, malformed_original, malformed_simple
				  ]
		if pair.rating.filter(rater=rater):
			ratings = pair.rating.filter(rater=rater)
			values.extend([ratings[0].duration])
			for aspect in TS_annotation_tool.utils.rating_aspects:
				values.append(ratings[0].__dict__[aspect])
		else:
			len_x = len(TS_annotation_tool.utils.rating_aspects)+1  # +1 for duration  # 15
			values.extend([numpy.nan]*len_x)
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
			# todo automatically generate this number
			len_subtrans = len(TS_annotation_tool.utils.transformation_list)  # 71
			values.extend([numpy.nan]*len_subtrans)
		result_frame.loc[i] = values
		i += 1
	# if rater == 2:
	# 	not_aligned_frame = export_not_aligned()
	return result_frame


def export_all(user):
	corpus_name = "TS_anno_"
	file_names = list()
	if user:
		for rater in set(data.models.DocumentPair.objects.values_list("annotator", flat=True)):
			rater_str = ".rater." + str(rater)
			file_name = corpus_name + rater_str + ".csv"
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


def get_inter_annotator_agreement_rating(real_user=False):
	dataframe = get_alignment_for_crf(real_user=True, iaa=False, iaa_rating=True)
	# pick dublicates in docpair simple_id and complex_id
	# check columns regarding aspect
	for docpair in data.models.DocumentPair.objects.all().order_by("id"):
		annotator_set = set(docpair.sentence_alignment_pair.all().values_list("annotator__id", flat=True))
		if len(annotator_set) < 2:
			continue
		# todo export rating
		# check if same aligned, if same alignment than calculate iaa of rating
		# for sentence_alignment in docpair.sentence_alignment_pair.all():
		# 	if sentence_alignment.objects.filter(simple)
		# for alignment_pair in docpair.sentence_alignment_pair.all():
		# 	if alignment_pair.complex_elements.filter(user_id)
		# for user_nr, user in enumerate(annotator_set):
		# 	if len(docpair.sentence_alignment_pair.filter(annotator=user)) == 0:
		# 		continue
		# 	if real_user and user.username == "test":
		# 		continue
		# 	complex_doc = docpair.complex_document
		# 	simple_doc = docpair.simple_document
		# 	domain = docpair.corpus.domain
		# 	title = docpair.simple_document.title
		# 	for par_nr_simple in sorted(list(set(simple_doc.sentences.all().values_list("paragraph_nr", flat=True)))):

	return 0
	# extract all raters
	# list_rater_ids = rating.models.Rating.objects.order_by().values_list('rater_id', flat=True).distinct()
	# list_pair_identifier = alignment.models.Pair.objects.order_by().values_list('pair_identifier', flat=True).distinct()
	#
	# output_list = [list(list_pair_identifier)]
	# for id_rater in list_rater_ids:
	# 	inner_list = list()
	# # print("number ids", len(Pair.objects.order_by().values_list('pair_identifier', flat=True).distinct()))
	# 	for pair_id in list_pair_identifier:
	# 		relevant_object = alignment.models.Pair.objects.filter(annotator=id_rater, pair_identifier=pair_id)
	# 		if relevant_object and relevant_object[0].rating.all():
	# 			# print(relevant_object[0])
	# 			# print(relevant_object[0].rating.all())
	# 			# print(relevant_object[0].rating.all()[0])
	# 			inner_list.append(getattr(relevant_object[0].rating.all()[0], aspect))
	# 		else:
	# 			inner_list.append(None)
	# 	output_list.append(inner_list)
	# # outputlist: values only for meaning_preservation. first row object identifiers of pairs, row per annotator. values are ratings per record with missing values
	# output = list()
	# for n, coder in enumerate(output_list):
	# 	for i in range(len(coder)):
	# 		output.append([n + 1, i, coder[i]])
	# ratingtask = agreement.AnnotationTask(data=output)
	# # following the example of https://learnaitech.com/how-to-compute-inter-rater-reliablity-metrics-cohens-kappa-fleisss-kappa-cronbach-alpha-kripndorff-alpha-scotts-pi-inter-class-correlation-in-python/
	# return ratingtask.alpha()


def export_sentences():
	for corpus in data.models.Corpus.objects.filter(name="Einfache Bücher"):
		if not os.path.exists("output_data/"+corpus.name):
			os.makedirs("output_data/"+corpus.name)
		for doc_par in corpus.document_pairs.all():
			simp_doc = doc_par.simple_document
			simple_text = ""
			for sent in simp_doc.sentences.all().order_by("id"):
				if sent.original_content.strip() != "":
					if corpus.name in ["bible_verified", "Einfache Bücher"]:
						simple_text += sent.original_content_repaired.strip() + "SEPL|||sent|||SEPR"
					else:
						simple_text += sent.original_content.strip()+"SEPL|||sent|||SEPR"
			with open("output_data/"+corpus.name+"/simple_"+simp_doc.title+".txt", "w") as f:
				f.write(simple_text[:-18])
			complex_doc = doc_par.complex_document
			complex_text = ""
			for sent in complex_doc.sentences.all().order_by("id"):
				if sent.original_content != "":
					if corpus.name in ["bible_verified", "Einfache Bücher"]:
						complex_text += sent.original_content_repaired.strip()+"SEPL|||sent|||SEPR"
					else:
						complex_text += sent.original_content.strip() + "SEPL|||sent|||SEPR"
			with open("output_data/"+corpus.name+"/complex_"+complex_doc.title+".txt", "w") as f:
				f.write(complex_text[:-18])
	return 1


def get_alignment_for_crf(real_user=True, iaa=False, iaa_rating=False):
	# if only one annotator annotated a document, use their annotation. If two use Mayas. Also include alignSame
	columns = ["tag", "docpair", "simple_sent_id", "complex_sent_id", "simplification", "original", "GLEU", "domain", "annotator", "title"]
	if iaa_rating:
		columns.extend(TS_annotation_tool.utils.rating_aspects)
	result_frame = pd.DataFrame(columns=columns)
	i = 0
	print(data.models.DocumentPair.objects.filter(sentence_alignment_pair__manually_checked=True).distinct().order_by("id"))
	for docpair in data.models.DocumentPair.objects.filter(sentence_alignment_pair__manually_checked=True).distinct().order_by("id"):  # .values_list("id", flat=True):  # .filter(~Q(corpus_id__in=[20, 21, 10])).order_by("id"):  # (~Q(complex_document__url__contains="bibel")).order_by("id"):  # filter(complex_document__url__contains="alumni"):  # filter(~Q(complex_document__url__contains="bibel")):
		annotator_set = set(docpair.sentence_alignment_pair.all().values_list("annotator__id", flat=True))
		if iaa and len(annotator_set) < 2:
			continue
		for user_nr, user in enumerate(docpair.annotator.all()):
			if len(docpair.sentence_alignment_pair.filter(annotator=user)) == 0:
				continue
			if real_user and user.username == "test":
					continue
			complex_doc = docpair.complex_document
			simple_doc = docpair.simple_document
			domain = docpair.corpus.domain
			title = docpair.simple_document.title
			for par_nr_simple in sorted(list(set(simple_doc.sentences.all().values_list("paragraph_nr", flat=True)))):
				for sent_simple in simple_doc.sentences.filter(paragraph_nr=par_nr_simple).order_by("id"):
					simple_sent_id = str(docpair.id) + "-0-" + str(sent_simple.paragraph_nr) + "-" + str(sent_simple.sentence_nr)
					if len(sent_simple.original_content_repaired) >= 1:
						sent_simple_content = sent_simple.original_content_repaired
					else:
						sent_simple_content = sent_simple.original_content
					for par_nr_complex in sorted(list(set(complex_doc.sentences.all().values_list("paragraph_nr", flat=True)))):
						for sent_complex in complex_doc.sentences.filter(paragraph_nr=par_nr_complex).order_by("id"):
							complex_sent_id = str(docpair.id) + "-1-" + str(sent_complex.paragraph_nr) + "-" + str(sent_complex.sentence_nr)
							if len(sent_complex.original_content_repaired) >= 1:
								sent_complex_content = sent_complex.original_content_repaired
							else:
								sent_complex_content = sent_complex.original_content
							if sent_complex.original_content == sent_simple.original_content:
								if real_user:
									continue
								else:
									if iaa_rating:
										result_frame.loc[i] = ["aligned", docpair.id, simple_sent_id, complex_sent_id,
															   sent_simple_content, sent_complex_content, 0,
															   domain, -1, title] + [pd.nan]*len(TS_annotation_tool.utils.rating_aspects)
									else:
										result_frame.loc[i] = ["aligned", docpair.id, simple_sent_id, complex_sent_id,
														   sent_simple_content, sent_complex_content, 0,
														   domain, -1, title]
									i += 1
							elif len(sent_complex.complex_element.filter(annotator=user)) == 0 or len(sent_simple.simple_element.filter(annotator=user)) == 0:
								if iaa_rating:
									result_frame.loc[i] = ["notAligned", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,
													   domain, user.id, title] + [pd.nan]*len(TS_annotation_tool.utils.rating_aspects)
								else:
									result_frame.loc[i] = ["notAligned", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,
													   domain, user.id, title]
								i += 1
							elif len(sent_simple.simple_element.get(annotator=user).simple_elements.all()) == 1 and len(sent_complex.complex_element.get(annotator=user).complex_elements.all()) == 1 and sent_complex.complex_element.get(annotator=user).id == sent_simple.simple_element.get(annotator=user).id:
								if iaa_rating:
									# todo add rating here, but keep track on the ratings checked in utils
									result_frame.loc[i] = ["aligned", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,
													   domain, user.id, title] + [pd.nan] * len(TS_annotation_tool.utils.rating_aspects)
								else:
									result_frame.loc[i] = ["aligned", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,
													   domain, user.id, title]
								i += 1
							elif (len(sent_simple.simple_element.get(annotator=user).simple_elements.all()) > 1  and sent_complex in sent_simple.simple_element.get(annotator=user).complex_elements.all()) or (len(sent_complex.complex_element.get(annotator=user).complex_elements.all()) > 1 and sent_simple in sent_complex.complex_element.get(annotator=user).simple_elements.all()):
								if iaa_rating:
									# todo check if only this one annotated and not also fully aligned
									result_frame.loc[i] = ["partialAligned", docpair.id, simple_sent_id,
														   complex_sent_id,
														   sent_simple_content, sent_complex_content, 0,
														   domain, user.id, title] + [pd.nan] * len(TS_annotation_tool.utils.rating_aspects)
								else:
									result_frame.loc[i] = ["partialAligned", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,
													   domain, user.id, title]
								i += 1
							elif sent_complex.complex_element.get(annotator=user).id != sent_simple.simple_element.get(annotator=user).id:
								if iaa_rating:
									result_frame.loc[i] = ["notAligned", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,  domain, user.id, title] + [pd.nan] * len(TS_annotation_tool.utils.rating_aspects)
								else:
									result_frame.loc[i] = ["notAligned", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,  domain, user.id, title]
								i += 1
							else:
								if iaa_rating:
									result_frame.loc[i] = ["unclear", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,
													   domain, user.id, title] + [pd.nan] * len(TS_annotation_tool.utils.rating_aspects)
								else:
									result_frame.loc[i] = ["unclear", docpair.id, simple_sent_id, complex_sent_id,
													   sent_simple_content, sent_complex_content, 0,
													   domain, user.id, title]
								i += 1
		print(docpair)
		# result_frame.to_csv("media/result_frame_maya.csv")
	return result_frame


def get_inter_annotator_agreement_alignment(dataframe):
	annotators = list(set(dataframe["annotator"]))
	categories = [0, 1, 2]
	dataframe["tag"] = dataframe["tag"].replace("aligned", 1)
	dataframe["tag"] = dataframe["tag"].replace("partialAligned", 2)
	dataframe["tag"] = dataframe["tag"].replace("notAligned", 0)
	if len(annotators) <= 1:
		n_ratings = len(dataframe)
		name = ""
		iaa = None
	else:
		rating_of_all_annotator = dataframe.drop_duplicates(["simple_sent_id", "complex_sent_id"])
		rating_of_all_annotator.rename(columns={'tag': 'label'}, inplace=True)
		n_ratings = len(rating_of_all_annotator)
		for i,annotator in enumerate(annotators):
			rating_of_one_annotator = dataframe[dataframe["annotator"] == annotator][["tag", "simple_sent_id", "complex_sent_id"]]
			rating_of_all_annotator = pd.merge(rating_of_all_annotator, rating_of_one_annotator, on=['simple_sent_id', "complex_sent_id"], how='left')
			rating_of_all_annotator.rename(columns={'tag': 'rating_'+str(i)}, inplace=True)
		if len(annotators) == 2:
			iaa = round(cohen_kappa_score(rating_of_all_annotator["rating_0"], rating_of_all_annotator["rating_1"], weights="quadratic"),4)
			name = "Cohens Kappa"
		else:
			rating_of_all_annotator = rating_of_all_annotator.loc[:, rating_of_all_annotator.columns.str.contains('rating')]
			category_df = pd.DataFrame(columns=categories)
			for i, row in rating_of_all_annotator.iterrows():
				for cat in categories:
					category_df.loc[i, cat] = (row == cat).sum()
			iaa = round(fleiss_kappa(category_df),4)
			name = "Fleiss Kappa"
	return {"n": n_ratings, "name": name, "iaa": iaa}


def filter_df_by_annotator_number(dataframe):
	docpairs_2_annotators = list()
	docpairs_more_annotators = list()
	n_anno = 0
	for docpair in set(dataframe["docpair"]):
		n_anno = len(set(dataframe[dataframe["docpair"] == docpair]["annotator"]))
		if n_anno < 2:
			continue
		elif n_anno == 2:
			docpairs_2_annotators.append(docpair)
		else:
			docpairs_more_annotators.append(docpair)
	dataframe_2_annotators = dataframe[dataframe["docpair"].isin(docpairs_2_annotators)]
	dataframe_more_annotators = dataframe[dataframe["docpair"].isin(docpairs_more_annotators)]
	return dataframe_2_annotators, dataframe_more_annotators


def get_iaa_alignment_dict(alignment_frame, df_2_annotators, df_more_annotators):
	agreement_dict = dict()
	agreement_dict["Per Title"] = dict()
	agreement_dict["Per Domain"] = dict()
	agreement_dict["All Documents"] = {"all": dict()}
	if len(df_2_annotators) > 0:
		iaa_two_annotators = get_inter_annotator_agreement_alignment(df_2_annotators)
		agreement_dict["All Documents"]["all"]["2 Annotators"] = iaa_two_annotators
		for domain in set(alignment_frame["domain"]):
			if domain not in agreement_dict["Per Domain"].keys():
				agreement_dict["Per Domain"][domain] = dict()
			if len(df_2_annotators[df_2_annotators["domain"] == domain]) > 0:
				iaa_two_annotators = get_inter_annotator_agreement_alignment(
					df_2_annotators[df_2_annotators["domain"] == domain])
				agreement_dict["Per Domain"][domain]["2 Annotators"] = iaa_two_annotators
		for title in set(alignment_frame["title"]):
			if title not in agreement_dict["Per Title"].keys():
				agreement_dict["Per Title"][title] = dict()
			if len(df_2_annotators[df_2_annotators["title"] == title]) > 0:
				iaa_two_annotators = get_inter_annotator_agreement_alignment(
					df_2_annotators[df_2_annotators["title"] == title])
				agreement_dict["Per Title"][title]["2 Annotators"] = iaa_two_annotators
	if len(df_more_annotators) > 0:
		iaa_more_annotators = get_inter_annotator_agreement_alignment(df_more_annotators)
		agreement_dict["All Documents"]["all"]["More Annotators"] = iaa_more_annotators
		for domain in set(alignment_frame["domain"]):
			if domain not in agreement_dict["Per Domain"].keys():
				agreement_dict["Per Domain"][domain] = dict()
			if len(df_more_annotators[df_more_annotators["domain"] == domain]) > 0:
				iaa_more_annotators = get_inter_annotator_agreement_alignment(
					df_more_annotators[df_more_annotators["domain"] == domain])
				agreement_dict["Per Domain"][domain]["More Annotators"] = iaa_more_annotators
		for title in set(alignment_frame["title"]):
			if title not in agreement_dict["Per Title"].keys():
				agreement_dict["Per Title"][title] = dict()
			if len(df_more_annotators[df_more_annotators["title"] == title]) > 0:
				iaa_more_annotators = get_inter_annotator_agreement_alignment(
					df_more_annotators[df_more_annotators["title"] == title])
				agreement_dict["Per Title"][title]["More Annotators"] = iaa_more_annotators
	# for domain in set(alignment_frame["domain"]):
	# 	agreement_dict["Per Domain"][domain] = dict()
	# 	if len(df_2_annotators[df_2_annotators["domain"] == domain]) > 0:
	# 		iaa_two_annotators = get_inter_annotator_agreement_alignment(
	# 			df_2_annotators[df_2_annotators["domain"] == domain])
	# 		agreement_dict["Per Domain"][domain]["2 Annotators"] = iaa_two_annotators
	# 	if len(df_more_annotators[df_more_annotators["domain"] == domain]) > 0:
	# 		iaa_more_annotators = get_inter_annotator_agreement_alignment(
	# 			df_more_annotators[df_more_annotators["domain"] == domain])
	# 		agreement_dict["Per Domain"][domain]["More Annotators"] = iaa_more_annotators
	# get_inter_annotator_agreement_alignment(alignment_frame[alignment_frame["domain"] == domain])
	# for title in set(alignment_frame["title"]):
	# 	agreement_dict["Per Title"][title] = dict()
	# 	if len(df_2_annotators[df_2_annotators["title"] == title]) > 0:
	# 		iaa_two_annotators = get_inter_annotator_agreement_alignment(
	# 			df_2_annotators[df_2_annotators["title"] == title])
	# 		agreement_dict["Per Title"][title]["2 Annotators"] = iaa_two_annotators
	# 	if len(df_more_annotators[df_more_annotators["title"] == title]) > 0:
	# 		iaa_more_annotators = get_inter_annotator_agreement_alignment(
	# 			df_more_annotators[df_more_annotators["title"] == title])
	# 		agreement_dict["Per Title"][title]["More Annotators"] = iaa_more_annotators
	return agreement_dict


@user_passes_test(lambda u: u.is_superuser)
def export(request):
	# todo export meta data, e.g. data of annotators
	return render(request, 'evaluation/home.html', {"title": "Evaluation - Text Simplification Annotation Tool"})


@user_passes_test(lambda u: u.is_superuser)
def full_document_export(request):
	file_names = list()
	simple_text, complex_text, meta_data = "", "", "\t".join(["language", "domain", "complex_level", "simple_level", "license", "author", "url", "access_date"])
	for document_pair in data.models.DocumentPair.objects.filter(corpus__continuous_text=True):
		if not document_pair.simple_document or not document_pair.complex_document:
			continue
		simple_text_tmp = document_pair.simple_document.plain_data
		simple_text += simple_text_tmp.replace("SEPL|||SEPR", " ")+"\n"
		complex_text_tmp = document_pair.complex_document.plain_data
		complex_text += complex_text_tmp.replace("SEPL|||SEPR", " ")+"\n"
		language, domain, complex_level, simple_level, license, author, url, access_date = document_pair.corpus.language, document_pair.corpus.domain, document_pair.complex_document.level, document_pair.simple_document.level, document_pair.corpus.license, document_pair.corpus.author, document_pair.simple_document.url, document_pair.simple_document.access_date
		meta_data += "\t".join([language, domain, complex_level, simple_level, license, author, url, str(access_date)])+"\n"
	with open("document_level_simple.txt", "w") as f:
		f.write(simple_text)
	with open("document_level_original.txt", "w") as f:
		f.write(complex_text)
	with open("document_level_meta.tsv", "w") as f:
		f.write(meta_data)
	return generate_zip_file(["document_level_simple.txt", "document_level_original.txt", "document_level_meta.tsv"])

def get_ids(doc_pair, sent, level):
	if len(sent) == 1:
		sent_id = str(doc_pair.id) + "-"+level+"-" + str(sent[0].paragraph_nr) + "-" + str(sent[0].sentence_nr)
		text = sent[0].original_content
	else:
		sent_id_list, text_list = list(), list()
		for s in sent:
			sent_id_list.append(str(doc_pair.id) + "-"+level+"-" + str(s.paragraph_nr) + "-" + str(s.sentence_nr))
			text_list.append(s.original_content)
		sent_id = "|".join(sent_id_list)
		text = " ".join(text_list)
	return sent_id, text


@user_passes_test(lambda u: u.is_superuser)
def full_aligned_document_export(request):
	file_names = list()
	columns = ["original", "simplification", "original_id", "simplification_id", "pair_id", "domain", "language_level_original",
			   "language_level_simple", "license", "author", "website", "access_date", "rater", "alignment"]
	for corpus in data.models.Corpus.objects.filter(continuous_text=True):
		domain, language, complex_level, simple_level, license, author = corpus.domain, corpus.language, corpus.complex_level, corpus.simple_level, corpus.license, corpus.author
		for rater in set(data.models.DocumentPair.objects.filter(corpus=corpus).values_list("annotator", flat=True)):
			output_df = pd.DataFrame(columns=columns)
			for doc_pair in corpus.document_pairs.filter(annotator=rater, complex_document__isnull=False, simple_document__isnull=False):
				pair_id, website, access_date = str(doc_pair.id), doc_pair.complex_document.url, doc_pair.complex_document.access_date
				simple_doc = doc_pair.simple_document
				complex_doc = doc_pair.complex_document
				simple_elements = doc_pair.sentence_alignment_pair.filter(annotator=rater).all().values_list("simple_elements", flat=True)
				complex_elements = doc_pair.sentence_alignment_pair.filter(annotator=rater).values_list("complex_elements", flat=True)
				simple_elements_added = list()
				complex_elements_added = list()
				for complex_sent in complex_doc.sentences.all():
					original = complex_sent.original_content
					complex_sent_id = str(doc_pair.id) + "-1-" + str(complex_sent.paragraph_nr) + "-" + str(complex_sent.sentence_nr)
					if complex_sent.original_content in simple_doc.sentences.values_list("original_content",flat=True):
						alignment_type = "identical"
						simple_sent = simple_doc.sentences.filter(original_content=complex_sent.original_content)
						simple_sent_id, simplification = get_ids(doc_pair, simple_sent,"0")
						simple_elements_added.extend(simple_sent)
					elif complex_sent.id in complex_elements and complex_sent not in complex_elements_added:
						alignment_type = "aligned"
						alignment_pair = complex_sent.complex_element.get(annotator=rater)
						complex_sent_id, original = get_ids(doc_pair, alignment_pair.complex_elements.all(), "1")
						simple_sent_id, simplification = get_ids(doc_pair, alignment_pair.simple_elements.all(), "0")
						simple_elements_added.extend(alignment_pair.simple_elements.all())
						complex_elements_added.extend(alignment_pair.complex_elements.all())
					else:
						alignment_type = "deletion"
						simple_sent_id, simplification = str(doc_pair.id) + "-0-x-x", ""
					output_df.loc[len(output_df)] = [original, simplification, complex_sent_id, simple_sent_id, pair_id, domain, complex_level,
													 simple_level, license, author, website, access_date, rater, alignment_type]
				for simple_sent in simple_doc.sentences.all():
					# simple_sent = data.models.Sentence.objects.get(id=simple_sent)
					if simple_sent not in simple_elements_added:
						alignment_type = "addition"
						simple_sent_id = str(doc_pair.id) + "-0-" + str(simple_sent.paragraph_nr) + "-" + str(simple_sent.sentence_nr)
						simplification = simple_sent.original_content
						complex_sent_id, original = str(doc_pair.id) + "-1-x-x", ""
						output_df.loc[len(output_df)] = [original, simplification, complex_sent_id, simple_sent_id,
														 pair_id, domain, complex_level,
														 simple_level, license, author, website, access_date, rater,
														 alignment_type]
			output_df = output_df.sort_values(["original_id", "simplification_id"])
			output_df.to_csv(corpus.name+"_"+str(rater)+"_doc_alignment.csv", index=False)
			file_names.append(corpus.name+"_"+str(rater)+"_doc_alignment.csv")
	return generate_zip_file(file_names)

# @user_passes_test(lambda u: u.is_superuser)
# def iaa(request):
# 	"""
# 	show inter annotator agreement
# 	"""
# 	return render(request, 'evaluation/iaa.html')
