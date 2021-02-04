from django.db import models
from languages.fields import LanguageField
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import stanza
from spacy_stanza import StanzaLanguage
import TS_annotation_tool.utils


class Corpus(models.Model):
	name = models.CharField(max_length=100, blank=True)
	home_page = models.URLField(max_length=500)
	license = models.CharField(max_length=250, choices=TS_annotation_tool.utils.list_licenses)
	parallel = models.BooleanField(default=False)
	domain = models.CharField(max_length=100)
	language = LanguageField(blank=True, max_length=8)
	path = models.CharField(max_length=500, blank=True, null=True)
	simple_level = models.CharField(max_length=50, choices=TS_annotation_tool.utils.language_level_list)
	complex_level = models.CharField(max_length=50, choices=TS_annotation_tool.utils.language_level_list)

	def add_documents_by_upload(self, files, form_upload):
		simple_files = [file for file in files if "simple" in file.name]
		nlp = get_spacy_model(form_upload.cleaned_data["language"])
		for file in simple_files:
			file_name, file_ending = file.name.split(".")
			file_id = file_name.split("_")[-1]
			simple_document = Document()
			simple_document = simple_document.create_or_load_document_by_upload(document=file,
														language_level=form_upload.cleaned_data["language_level_simple"],
														domain=form_upload.cleaned_data["domain"], nlp=nlp)
			complex_file_obj = [file for file in files if "complex" in file.name and "_" + file_id + "." in file.name]
			if complex_file_obj:
				complex_document = Document()
				complex_document = complex_document.create_or_load_document_by_upload(complex_file_obj[0], form_upload.cleaned_data[
					"language_level_complex"], form_upload.cleaned_data["domain"], nlp)
				document_pair_tmp = DocumentPair(corpus=self)
				document_pair_tmp.complex_document = complex_document
				document_pair_tmp.simple_document = simple_document
				document_pair_tmp.save()
				document_pair_tmp.annotator.add(*form_upload.cleaned_data["annotator"])
				document_pair_tmp.save()
				self.document_pair = document_pair_tmp
		self.complex_level = form_upload.cleaned_data["language_level_complex"]
		self.simple_level = form_upload.cleaned_data["language_level_simple"]
		self.save()
		return self


class Document(models.Model):
	url = models.URLField(max_length=500)
	title = models.TextField(max_length=500, blank=True)
	access_date = models.DateField(blank=True, null=True)
	author = models.TextField(max_length=100, blank=True)
	html_data = models.TextField(blank=True)
	plain_data = models.TextField(blank=True)
	level = models.CharField(max_length=50, blank=True, choices=TS_annotation_tool.utils.language_level_list)
	license = models.CharField(max_length=250, choices=TS_annotation_tool.utils.list_licenses, blank=True)
	path = models.FileField(upload_to='media/uploads/', blank=True, null=True)
	domain = models.CharField(max_length=50, blank=True, null=True)

	def add_sentences(self, sentences, language_level):
		for sent in sentences:
			sent_tmp = Sentence(original_content=sent, level=language_level, document=self)
			sent_tmp.save()
			sent_tmp.tokenize(sent)
		return 1

	def create_or_load_document_by_upload(self, document, language_level, domain, nlp):
		document_content = document.readlines()
		copyright_line = document_content[0].decode("utf-8").strip().split(" ")
		date = copyright_line[-1][:-1]
		url = copyright_line[3]
		title = url.split("/")[-1]

		if Document.objects.filter(title=title, url=url):
			document_tmp = Document.objects.get(title=title, url=url)
		else:
			document_tmp = Document(url=url, title=title, access_date=date,
									plain_data=document_content[1].decode("utf-8"),
									level=language_level, domain=domain)
			document_tmp.save()
			document_tmp.add_sentences(nlp(document_content[1].decode("utf-8")).sents, language_level)
			document_tmp.save()
		return document_tmp


class DocumentPair(models.Model):
	simple_document = models.ForeignKey(Document, blank=True, related_name="simple_document", on_delete=models.CASCADE)
	complex_document = models.ForeignKey(Document, blank=True, related_name="complex_document", on_delete=models.CASCADE)
	annotator = models.ManyToManyField(User, blank=True)
	last_changes = models.DateTimeField(auto_now=True)
	corpus = models.ForeignKey(Corpus, on_delete=models.CASCADE, blank=True, null=True)

	def get_all_complex_annotated_sentences_by_user(self, user, content=False):
		complex_annotated_sents_content = list()
		for sent in Sentence.objects.filter(document=self.complex_document):
			for pair in sent.complex_element.all():
				if user in pair.annotator.all():
					if content:
						complex_annotated_sents_content.append(sent.original_content)
					else:
						complex_annotated_sents_content.append(sent)
		return complex_annotated_sents_content

	def get_all_simple_annotated_sentences_by_user(self, user, content=False):
		simple_annotated_sents_content = list()
		for sent in Sentence.objects.filter(document=self.simple_document):
			for pair in sent.simple_element.all():
				if user in pair.annotator.all():
					if content:
						simple_annotated_sents_content.append(sent.original_content)
					else:
						simple_annotated_sents_content.append(sent)
		return simple_annotated_sents_content


class Sentence(models.Model):
	original_content = models.TextField()
	corrected_content = models.TextField(blank=True)
	translation = models.TextField(blank=True)
	level = models.CharField(max_length=50, blank=True, choices=TS_annotation_tool.utils.language_level_list)
	simplification = models.ForeignKey("simplification.Simplification", blank=True, on_delete=models.CASCADE, null=True)
	document = models.ForeignKey("data.Document", on_delete=models.CASCADE, blank=True, related_name="sentences")
	simple_element = models.ManyToManyField("alignment.Pair", related_name="simple_elements", blank=True)
	complex_element = models.ManyToManyField("alignment.Pair", related_name="complex_elements", blank=True)
	malformed = models.BooleanField(default=False)
	malformed_comment = models.TextField(blank=True, max_length=250)

	def tokenize(self, doc):
		for token in doc:
			token_tmp = Token(text=token.text, lemma=token.lemma_, tag=token.tag_, sentence=self)
			token_tmp.save()
		self.save()


class Token(models.Model):
	text = models.CharField(max_length=200)
	lemma = models.CharField(max_length=200)
	tag = models.CharField(max_length=10)
	sentence = models.ForeignKey(Sentence, related_name="tokens", blank=True, on_delete=models.CASCADE)

	def __str__(self):
		return self.text


def save_uploaded_file(f):
	fs = FileSystemStorage()
	filename = fs.save(f.name, f)
	uploaded_file_url = fs.url(filename)
	return uploaded_file_url


def get_spacy_model(language):
	# stanza.download(language)
	snlp = stanza.Pipeline(lang=language)
	nlp = StanzaLanguage(snlp)
	# if language == "de":
	# 	nlp = spacy.load("de_core_news_lg")
	# elif language == "en":
	# 	nlp = spacy.load("en_core_web_sm")
	# else:
	# 	nlp = spacy.load("en_core_web_sm")
	return nlp

