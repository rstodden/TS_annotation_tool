from django.db import models
from languages.fields import LanguageField
import datetime


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
				   ("c2", "Alltagssprache")
					)
	level = models.CharField(max_length=50, blank=True, choices=level_list)
	parallel_document = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

	def scraping_content(self):
		# extracting the content of the html tree
		pass

	def split_sentences(self):
		# read plain data and create sentence objects which will be linked to this document
		pass

	def align_sentences(self):
		# call alignment app
		pass

	def add_plain_text_manually(self, url, plain_text, level, author=None):
		self.plain_data = plain_text
		self.access_date = datetime.datetime.now()
		self.url = url
		self.level = level
		self.author = author
		return self


class Sentence(models.Model):
	# id = models.ForeignKey(on_delete=models.CASCADE, primary_key=True, unique=True)
	# grammaticality = IntegerRangeField(min_value=1, max_value=5, default=0)
	# translation_quality = IntegerRangeField(min_value=1, max_value=5, default=0)

	# many to one
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	original_content = models.TextField()
	corrected_content = models.TextField(blank=True)
	translation = models.TextField(blank=True)


class Corpus(models.Model):
	name = models.CharField(max_length=100, blank=True)
	home_page = models.URLField(max_length=500)
	list_licenses = (("prohibition", "prohibition"),("save_use", "save_use"),
					 ("save_use_share_with_password", "save_use_share_with_password"),
					 ("CC_BY_NC_DE_3", "CC_BY_NC_DE_3"),
					 ("CC_BY_NC_SA_DE_3", "CC_BY_NC_SA_DE_3"),
					 ("CC_BY_NC_ND_DE_3", "CC_BY_NC_ND_DE_3")
					 )
	license = models.CharField(max_length=250, choices=list_licenses)
	parallel = models.BooleanField(default=False)
	simple_documents = models.ManyToManyField(Document, related_name="simple_documents")
	complex_documents = models.ManyToManyField(Document, blank=True, related_name="complex_documents")
	domain = models.CharField(max_length=100)
	language = LanguageField(blank=True, max_length=8)

	def fill_corpus(self):
		# read urls and save plain text
		# create document instances and assign to corpus
		# also add parallel link between documents, if exist
		pass


