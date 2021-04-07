from django.db import models
# from languages.fields import LanguageField
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
# import stanza
# from spacy_stanza import StanzaLanguage
import spacy
import TS_annotation_tool.utils
from alignment.models import Pair
import datetime, json
from django.core.serializers.json import DjangoJSONEncoder


class Corpus(models.Model):
	name = models.CharField(max_length=100, blank=True)
	home_page = models.URLField(max_length=500, blank=True)
	license = models.CharField(max_length=250, choices=TS_annotation_tool.utils.list_licenses)
	parallel = models.BooleanField(default=False)
	domain = models.CharField(max_length=100)
	language = 	models.CharField(max_length=8, choices=TS_annotation_tool.utils.LANGUAGE_CHOICES)
	path = models.CharField(max_length=500, blank=True, null=True)
	simple_level = models.CharField(max_length=50, choices=TS_annotation_tool.utils.language_level_list)
	complex_level = models.CharField(max_length=50, choices=TS_annotation_tool.utils.language_level_list)
	pre_aligned = models.BooleanField(default=False)
	license_file = models.FileField(blank=True, null=True)
	author = models.CharField(max_length=500, blank=True)  # copyright owner
	manually_aligned = 	models.BooleanField(default=False, blank=True)

	def add_documents_by_upload(self, files, form_upload):
		simple_files = [file for file in files if "simple" in file.name]
		nlp = get_spacy_model(form_upload.cleaned_data["language"])
		for file in simple_files:
			file_name, file_ending = file.name.split(".")
			file_id = file_name.split("_")[-1]
			simple_document = Document()
			simple_document = simple_document.create_or_load_document_by_upload(document=file,
														language_level=form_upload.cleaned_data["language_level_simple"],
														domain=form_upload.cleaned_data["domain"], nlp=nlp,
														pre_aligned=form_upload.cleaned_data["pre_aligned"],
														selected_license=form_upload.cleaned_data["license"])
			complex_file_obj = [file for file in files if "complex" in file.name and "_" + file_id + "." in file.name]
			if complex_file_obj:
				complex_document = Document()
				complex_document = complex_document.create_or_load_document_by_upload(complex_file_obj[0], form_upload.cleaned_data[
					"language_level_complex"], form_upload.cleaned_data["domain"], nlp, pre_aligned=form_upload.cleaned_data["pre_aligned"],
				    selected_license=form_upload.cleaned_data["license"])
				document_pair_tmp = DocumentPair(corpus=self)
				document_pair_tmp.complex_document = complex_document
				document_pair_tmp.simple_document = simple_document
				document_pair_tmp.save()
				document_pair_tmp.annotator.add(*form_upload.cleaned_data["annotator"])
				if form_upload.cleaned_data["pre_aligned"]:
					document_pair_tmp.add_aligned_sentences(nlp=nlp, manually_aligned=form_upload.cleaned_data["manually_aligned"],
															language_level_simple=form_upload.cleaned_data["language_level_simple"],
															language_level_complex=form_upload.cleaned_data["language_level_complex"])
				document_pair_tmp.save()
				self.document_pair = document_pair_tmp
		self.complex_level = form_upload.cleaned_data["language_level_complex"]
		self.simple_level = form_upload.cleaned_data["language_level_simple"]
		self.save()
		return self

	def __str__(self):
		if self.name:
			return self.name
		else:
			return "Sentence ("+str(self.id)+")"


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

	def add_sentences(self, sentences, language_level, selected_license, number_sentences=1):
		treshold = 1
		sentence_ids = list()
		if selected_license in TS_annotation_tool.utils.license_limits.keys():
			treshold = TS_annotation_tool.utils.license_limits[selected_license]["save_use"]
		for i, sent in enumerate(sentences):
			if (i+1)/number_sentences >= treshold:
				break
			sent_tmp = Sentence(original_content=sent, level=language_level, document=self)
			sent_tmp.save()
			sentence_ids.append(sent_tmp.id)
			sent_tmp.tokenize(sent)
		return sentence_ids

	def create_or_load_document_by_upload(self, document, language_level, domain, nlp, selected_license, pre_aligned=False):
		document_content = document.readlines()
		copyright_line, title = document_content[0].decode("utf-8").strip().split("\t")
		copyright_line = copyright_line.split(" ")
		date = copyright_line[-1][:-1]
		url = copyright_line[3]
		# title = url.split("/")[-1]

		if Document.objects.filter(title=title, url=url, level=language_level):
			document_tmp = Document.objects.get(title=title, url=url, level=language_level)
		else:
			if not pre_aligned:
				document_tmp = Document(url=url, title=title, access_date=date,
									plain_data=document_content[1].decode("utf-8"),
									level=language_level, domain=domain)
			else:
				plain_data = ""
				for data in document_content[1:]:
					plain_data += data.decode("utf-8")
				document_tmp = Document(url=url, title=title, access_date=date,
										plain_data=plain_data.strip(), level=language_level, domain=domain)
			document_tmp.save()
			if not pre_aligned:
				number_sentences = len([sent for sent in nlp(document_content[1].strip().decode("utf-8")).sents])
				document_tmp.add_sentences(nlp(document_content[1].strip().decode("utf-8")).sents, language_level, selected_license, number_sentences)
			document_tmp.save()
		return document_tmp

	def __str__(self):
		if self.title:
			return self.title
		else:
			return "Document ("+str(+self.id)+")"


class DocumentPair(models.Model):
	simple_document = models.ForeignKey(Document, blank=True, related_name="simple_document", on_delete=models.CASCADE)
	complex_document = models.ForeignKey(Document, blank=True, related_name="complex_document", on_delete=models.CASCADE)
	annotator = models.ManyToManyField(User, blank=True)
	last_changes = models.DateTimeField(auto_now=True)
	no_alignment_possible = models.BooleanField(default=False)
	corpus = models.ForeignKey(Corpus, on_delete=models.CASCADE, blank=True, null=True, related_name="document_pairs")

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

	def add_aligned_sentences(self, nlp, language_level_simple, language_level_complex, manually_aligned):
		simple_doc = self.simple_document
		complex_doc = self.complex_document
		simple_sentences = simple_doc.plain_data.split("\n")
		complex_sentences = complex_doc.plain_data.split("\n")
		# print(simple_sentences, complex_sentences)
		for simple_sent, complex_sent in zip(simple_sentences, complex_sentences):
			simple_elements_ids = simple_doc.add_sentences(nlp(simple_sent).sents, language_level_simple)
			complex_elements_ids = complex_doc.add_sentences(nlp(complex_sent).sents, language_level_complex)
			simple_elements = Sentence.objects.filter(id__in=simple_elements_ids)
			complex_elements = Sentence.objects.filter(id__in=complex_elements_ids)
			if simple_sent != complex_sent:
				sentence_pair_tmp = Pair()
				user, created = User.objects.get_or_create(username="tool")
				sentence_pair_tmp.save_sentence_alignment_from_form(simple_elements, complex_elements, user, self,
																json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder),
																manually_aligned=manually_aligned)
				sentence_pair_tmp.save()
			# else:
			# 	print(simple_sent, "!!!", complex_sent)
		return self


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
	# # stanza.download(language)
	# snlp = stanza.Pipeline(lang=language)
	# nlp = StanzaLanguage(snlp)
	if language == "de":
		nlp = spacy.load("de_dep_news_trf")
	elif language == "en":
		nlp = spacy.load("en_core_web_sm")
	else:
		nlp = spacy.load("en_core_web_sm")
	return nlp


# def repair_original_text():
# 	sentences = Sentence.objects.all()
# 	nlp = get_spacy_model("de")
# 	for sent in sentences:
# 		print(sent.original_content, nlp(sent.original_content).text)