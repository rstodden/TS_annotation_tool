from django.db import models
from languages.fields import LanguageField
import datetime
from django.contrib.auth.models import User
import alignment.models
from django.core.files.storage import FileSystemStorage
import pandas as pd
import io, csv
from django.core.files.base import ContentFile
import numpy as np
from django.conf import settings
import spacy

list_licenses = (
					("to_add", "to_add"),
					("not_allowed", "not_allowed"),
					("save_use", "save_use"),
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
					 )

language_level_list = (("a1", "Leichte Sprache"),
				   ("a2", "Einfache Sprache"),
				   ("b2", "Vereinfachte Sprache"),
				   ("c2", "Alltagssprache")
					)
class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)
	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value':self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)


class Document(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, primary_key=True, unique=True)
	url = models.URLField(max_length=500)
	title = models.TextField(max_length=500, blank=True)
	access_date = models.DateField(blank=True, null=True)
	author = models.TextField(max_length=100, blank=True)
	html_data = models.TextField(blank=True)
	plain_data = models.TextField(blank=True)
	level = models.CharField(max_length=50, blank=True, choices=language_level_list)
	license = models.CharField(max_length=250, choices=list_licenses, blank=True)
	parallel_document = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
	annotator = models.ManyToManyField(User, blank=True)
	alignments = models.ManyToManyField("alignment.Pair", blank=True)
	path = models.FileField(upload_to='media/uploads/', blank=True, null=True)
	domain = models.CharField(max_length=50, blank=True, null=True)
	sentences = models.ManyToManyField("data.Sentence", blank=True)

	def scraping_content(self):
		# extracting the content of the html tree
		pass

	def split_sentences(self):
		# read plain data and create sentence objects which will be linked to this document
		pass

	def get_pair_identifier(self):
		list_ids = alignment.models.Pair.objects.values_list("pair_identifier")
		if list_ids:
			return max(list_ids)[0] + 1
		else:
			return 1

	def align_sentences(self, simple_sentences, complex_sentences, user, type_alignment):
		# alignment_tmp, alignment_tmp_created = alignment.models.Pair.objects.get_or_create(url=row["simplesource"])
		# todo: change or create new?
		list_ids = alignment.models.Pair.objects.values_list("pair_identifier")
		pair_identifier = self.get_pair_identifier()
		alignment_tmp = alignment.models.Pair()  #.objects.create(manually_checked=True, pair_identifier=pair_identifier)
		alignment_tmp.manually_checked = True
		alignment_tmp.pair_identifier = pair_identifier
		alignment_tmp.save()
		for simple_s in simple_sentences:
			alignment_tmp.simple_element.add(simple_s)
		for complex_s in complex_sentences:
			alignment_tmp.complex_element.add(complex_s)
		alignment_tmp.annotator.add(user)
		alignment_tmp.origin_annotator = user
		alignment_tmp.type = type_alignment
		alignment_tmp.save()
		self.alignments.add(alignment_tmp)
		self.save()
		return self.alignments

	def __str__(self):
		return self.url

	def add_plain_text_manually(self, url, plain_text, level, author=None):
		self.plain_data = plain_text
		self.access_date = datetime.datetime.now()
		self.url = url
		self.level = level
		self.author = author
		return self

	def set_values(self, level, user, file_path, domain=None, title=None, access_date=None, license=None):
		self.level = level
		self.annotator.add(user)
		self.path = file_path
		self.domain = domain
		self.title = title
		self.access_date = datetime.datetime.strptime(access_date, '%d.%m.%y').strftime('%Y-%m-%d')
		self.license = license
		self.save()
		return self

	def delete_pair(self, pair_id, user):
		pair_tmp = alignment.models.Pair.objects.get(id=pair_id, annotator=user)
		if self.alignments.filter(id=pair_id, annotator=user):
			self.alignments.remove(pair_tmp)
		pair_tmp.delete()
		self.save()
		return self

	def save_alignment_form_form(self, form, user):
		alignment_tmp = form.save(commit=False)
		alignment_tmp.type = "parallel_online"
		alignment_tmp.manually_checked = True
		alignment_tmp.origin_annotator = user
		alignment_tmp.pair_identifier = self.get_pair_identifier()
		alignment_tmp.save()
		alignment_tmp.annotator.add(user)
		for sentence in form.cleaned_data["complex_element"]:
			alignment_tmp.complex_element.add(sentence)
		for sentence in form.cleaned_data["simple_element"]:
			alignment_tmp.simple_element.add(sentence)
		alignment_tmp.save()
		self.alignments.add(alignment_tmp)
		self.save()
		return self


class Token(models.Model):
	text = models.CharField(max_length=200)
	lemma = models.CharField(max_length=200)
	tag = models.CharField(max_length=10)

	def __str__(self):
		return self.text


class Sentence(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, primary_key=True, unique=True)
	# grammaticality = IntegerRangeField(min_value=1, max_value=5, default=0)
	# translation_quality = IntegerRangeField(min_value=1, max_value=5, default=0)

	# many to one
	# document = models.ForeignKey(Document, on_delete=models.CASCADE)
	original_content = models.TextField()
	corrected_content = models.TextField(blank=True)
	translation = models.TextField(blank=True)
	level = models.CharField(max_length=50, blank=True, choices=language_level_list)
	simplification = models.ForeignKey("simplification.Simplification", blank=True, on_delete=models.CASCADE, null=True)
	tokens = models.ManyToManyField(Token, related_name="tokens", blank=True)

	def tokenize(self, doc):
		for token in doc:
			token_tmp = Token(text=token.text, lemma=token.lemma_, tag=token.tag_)
			token_tmp.save()
			self.tokens.add(token_tmp)
		self.save()


class Corpus(models.Model):
	name = models.CharField(max_length=100, blank=True)
	home_page = models.URLField(max_length=500)
	license = models.CharField(max_length=250, choices=list_licenses)
	parallel = models.BooleanField(default=False)
	simple_documents = models.ManyToManyField(Document, blank=True, related_name="simple_documents")
	complex_documents = models.ManyToManyField(Document, blank=True, related_name="complex_documents")
	domain = models.CharField(max_length=100)
	language = LanguageField(blank=True, max_length=8)
	path = models.CharField(max_length=500, blank=True, null=True)

	def fill_corpus(self):
		# read urls and save plain text
		# create document instances and assign to corpus
		# also add parallel link between documents, if exist
		pass

	def fill_with_manually_aligned(self, uploaded_file):

		dataframe_content = pd.read_csv(ContentFile(uploaded_file.read()), encoding="utf-8", sep=",")
		file_path = save_uploaded_file(uploaded_file)

		self.name = "manually_added_at"+str(datetime.datetime.now())
		self.license = "to_add"
		self.home_page = ""
		self.parallel = True
		self.language = settings.LANGUAGE_CORPORA
		self.domain = "mixed"
		self.path = file_path
		self.save()

		domains = set()
		for index, row in dataframe_content.iterrows():
			domains.add(row["domain"])
			# lower levels to match level choice list
			if not pd.isna(row["complexlevel"]):
				row["complexlevel"] = row["complexlevel"].lower()
			if not pd.isna(row["simplelevel"]):
				row["simplelevel"] = row["simplelevel"].lower()

			# create or get document and set as parallel
			simple_doc, simple_doc_created = Document.objects.get_or_create(url=row["simplesource"])
			complex_doc, complex_doc_created = Document.objects.get_or_create(url=row["complexsource"])
			if complex_doc_created:
				complex_doc = complex_doc.set_values(row["complexlevel"], User.objects.get(username="admin"),
												 	file_path, domain=row["domain"], title=row["title_complex"],
													 access_date=row["access_date_complex"], license=row["license_complex"])
				self.complex_documents.add(complex_doc)
			if simple_doc_created:
				simple_doc = simple_doc.set_values(row["simplelevel"], User.objects.get(username="admin"), file_path,
												   domain=row["domain"], title=row["title_simple"],
												   access_date=row["access_date_simple"], license=row["license_simple"])
				self.simple_documents.add(simple_doc)
			simple_doc.parallel_document = complex_doc
			complex_doc.parallel_document = simple_doc


			# create and add sentences
			simple_sent = Sentence(original_content=row["simple"], level=row["simplelevel"])
			complex_sent = Sentence(original_content=row["complex"], level=row["complexlevel"])
			simple_sent.save()
			complex_sent.save()

			simple_doc.sentences.add(simple_sent)
			complex_doc.sentences.add(complex_sent)

			# add alignment
			simple_doc.align_sentences([simple_sent], [complex_sent], User.objects.get(username="admin"), "parallel_online_uploaded")

			simple_doc.save()
			complex_doc.save()
		if len(domains) == 1:
			self.domain = list(domains)[0]
		self.save()
		return self

	def __str__(self):
		return self.name

	def add_documents_by_upload(self, files, form_upload):
		simple_files = [file for file in files if "simple" in file.name]
		nlp = get_spacy_model(form_upload.cleaned_data["language"])
		for file in simple_files:
			file_name, file_ending = file.name.split(".")
			file_id = file_name.split("_")[-1]
			simple_document = create_document_by_upload(document=file,
														language_level=form_upload.cleaned_data["language_level_simple"],
														domain=form_upload.cleaned_data["domain"], nlp=nlp,
														annotators=form_upload.cleaned_data["annotator"])
			self.simple_documents.add(simple_document)
			complex_file_obj = [file for file in files if "complex" in file.name and "_" + file_id + "." in file.name]
			if complex_file_obj:
				complex_document = create_document_by_upload(complex_file_obj[0], form_upload.cleaned_data[
					"language_level_complex"], form_upload.cleaned_data["domain"], nlp,
														annotators=form_upload.cleaned_data["annotator"])
				complex_document.parallel_document = simple_document
				complex_document.save()
				simple_document.parallel_document = complex_document
				simple_document.save()
				self.complex_documents.add(complex_document)

		self.save()
		return self


def save_uploaded_file(f):
	fs = FileSystemStorage()
	filename = fs.save(f.name, f)
	uploaded_file_url = fs.url(filename)
	return uploaded_file_url


def get_spacy_model(language):
	if language == "de":
		nlp = spacy.load("de_core_news_sm")
	elif language == "en":
		nlp = spacy.load("en_core_web_sm")
	else:
		nlp = spacy.load("en_core_web_sm")
	return nlp


def create_document_by_upload(document, language_level, domain, nlp, annotators=None):
	document_content = document.readlines()
	copyright_line = document_content[0].decode("utf-8").strip().split(" ")
	date = copyright_line[-1][:-1]
	url = copyright_line[3]
	title = url.split("/")[-1]

	if Document.objects.filter(title=title, url=url):
		document_tmp = Document.objects.get(title=title, url=url)
	else:
		document_tmp = Document(url=url, title=title, access_date=date, plain_data=document_content[1].decode("utf-8"),
											level=language_level, domain=domain)
		document_tmp.save()
		if annotators:
			for user in annotators:
				document_tmp.annotator.add(user)
		for sent in nlp(document_content[1].decode("utf-8")).sents:
			sent_tmp = Sentence(original_content=sent, level=language_level)
			sent_tmp.save()
			sent_tmp.tokenize(sent)
			document_tmp.sentences.add(sent_tmp)
		document_tmp.save()
	return document_tmp
