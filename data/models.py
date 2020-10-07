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
	access_date = models.DateField(blank=True, null=True)
	author = models.TextField(max_length=100, blank=True)
	html_data = models.TextField(blank=True)
	plain_data = models.TextField(blank=True)
	level_list = (("a1", "Leichte Sprache"),
				   ("a2", "Einfache Sprache"),
				   ("b2", "Vereinfachte Sprache"),
				   ("c2", "Alltagssprache")
					)
	level = models.CharField(max_length=50, blank=True, choices=level_list)
	parallel_document = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
	annotator = models.ManyToManyField(User, blank=True)
	alignments = models.ManyToManyField(alignment.models.Pair, blank=True)
	path = models.FileField(upload_to='media/uploads/', blank=True, null=True)
	domain = models.CharField(max_length=50, blank=True, null=True)
	sentences = models.ManyToManyField("data.Sentence", blank=True)

	def scraping_content(self):
		# extracting the content of the html tree
		pass

	def split_sentences(self):
		# read plain data and create sentence objects which will be linked to this document
		pass

	def align_sentences(self, simple_sentences, complex_sentences, user, type_alignment):
		# alignment_tmp, alignment_tmp_created = alignment.models.Pair.objects.get_or_create(url=row["simplesource"])
		# todo: change or create new?
		list_ids = alignment.models.Pair.objects.values_list("pair_identifier")
		if list_ids:
			pair_identifier = max(list_ids)[0]+1
		else:
			pair_identifier = 0
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

	def add_plain_text_manually(self, url, plain_text, level, author=None):
		self.plain_data = plain_text
		self.access_date = datetime.datetime.now()
		self.url = url
		self.level = level
		self.author = author
		return self

	def set_values(self, level, user, file_path, domain):
		self.level = level
		self.annotator.add(user)
		self.path = file_path
		self.domain = domain
		self.save()
		return self



class Sentence(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, primary_key=True, unique=True)
	# grammaticality = IntegerRangeField(min_value=1, max_value=5, default=0)
	# translation_quality = IntegerRangeField(min_value=1, max_value=5, default=0)

	# many to one
	# document = models.ForeignKey(Document, on_delete=models.CASCADE)
	original_content = models.TextField()
	corrected_content = models.TextField(blank=True)
	translation = models.TextField(blank=True)
	level_list = (("a1", "Leichte Sprache"),
				   ("a2", "Einfache Sprache"),
				   ("b2", "Vereinfachte Sprache"),
				   ("c2", "Alltagssprache")
					)
	level = models.CharField(max_length=50, blank=True, choices=level_list)
	simplification = models.ForeignKey("simplification.Simplification", blank=True, on_delete=models.CASCADE, null=True)


class Corpus(models.Model):
	name = models.CharField(max_length=100, blank=True)
	home_page = models.URLField(max_length=500)
	list_licenses = (("prohibition", "prohibition"),("save_use", "save_use"),
					 ("save_use_share_with_password", "save_use_share_with_password"),
					 ("CC_BY_NC_DE_3", "CC_BY_NC_DE_3"),
					 ("CC_BY_NC_SA_DE_3", "CC_BY_NC_SA_DE_3"),
					 ("CC_BY_NC_ND_DE_3", "CC_BY_NC_ND_DE_3"),
					 ("to_add", "to_add"),
					 )
	license = models.CharField(max_length=250, choices=list_licenses)
	parallel = models.BooleanField(default=False)
	simple_documents = models.ManyToManyField(Document, related_name="simple_documents")
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

		dataframe_content = pd.read_csv(ContentFile(uploaded_file.read()), encoding="utf-8")
		file_path = save_uploaded_file(uploaded_file)

		self.name = "manually_added_at"+str(datetime.datetime.now())
		self.license = "to_add"
		self.home_page = ""
		self.parallel = True
		self.language = settings.LANGUAGE_CORPORA
		self.domain = "mixed"
		self.path = file_path
		self.save()


		for index, row in dataframe_content.iterrows():
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
												 file_path, row["domain"])
				self.complex_documents.add(complex_doc)
			if simple_doc_created:
				simple_doc = simple_doc.set_values(row["simplelevel"], User.objects.get(username="admin"), file_path, row["domain"])
				self.simple_documents.add(simple_doc)
			simple_doc.parallel_document = complex_doc
			complex_doc.parallel_document = simple_doc


			# todo split sentence here
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
		self.save()
		return self




# url = models.URLField(max_length=500)
# access_date = models.DateField(blank=True, null=True)
# author = models.TextField(max_length=100, blank=True)
# html_data = models.TextField(blank=True)
# plain_data = models.TextField(blank=True)
# level_list = (("a1", "Leichte Sprache"),
# 			   ("a2", "Einfache Sprache"),
# 			   ("b2", "Vereinfachte Sprache"),
# 			   ("c2", "Alltagssprache")
# 				)
# level = models.CharField(max_length=50, blank=True, choices=level_list)
# parallel_document = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
# annotator = models.ManyToManyField(User, blank=True)
# alignments = models.ManyToManyField(Pair, blank=True)
# path = models.FileField(upload_to='media/uploads/')

# file_url = save_uploaded_file(uploaded_file)
# create dummy corpus and dummy document but add urls and add file_url to doc.path
# add sentences to doc and corpus
# align sentences 8create alignemnt.pair
# aligned_pairs = alignment.models.Pair.assign_to_user()
# return aligned pairs


def save_uploaded_file(f):
	fs = FileSystemStorage()
	filename = fs.save(f.name, f)
	uploaded_file_url = fs.url(filename)
	return uploaded_file_url

