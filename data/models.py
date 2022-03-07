import wasabi
from django.db import models
# from languages.fields import LanguageField
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
# import stanza
# from spacy_stanza import StanzaLanguage
import spacy
import TS_annotation_tool.utils
from alignment.models import Pair
import datetime, json
from django.core.serializers.json import DjangoJSONEncoder
import numpy
import requests
import re
from operator import itemgetter


def popover_html(content):
	# return content
	return """<i data-toggle="tooltip" data-placement="top" title='""" + content+"""' class="fas fa-question-circle">  </i>"""


# class Language(models.Model):
# 	name = models.CharField(max_length=8, choices=TS_annotation_tool.utils.LANGUAGE_CHOICES, help_text=popover_html("In which language(s) is the data?"))
#
# 	def __str__(self):
# 		return self.name


class Corpus(models.Model):
	name = models.CharField(max_length=100, blank=True, help_text=popover_html("How should the corpus be called in the annotation tool?"))  #, help_text="How should the corpus be called in the annotation tool?")
	home_page = models.URLField(max_length=500, blank=True, help_text=popover_html( "What is the source of the (web) data)? Please provide at least a author name or homepage."))
	license = models.CharField(max_length=250, choices=TS_annotation_tool.utils.list_licenses, help_text=popover_html('Is the data published under a specific license?'))
	parallel = models.BooleanField(default=False, help_text=popover_html("Do comparable or parallel documents exist? If not you can select the to_simplify option."))
	domain = models.CharField(max_length=100, help_text=popover_html('How can the domain of the data be described?'))
	# languages = models.ForeignKey(Language, blank=True, related_name="corpus_language", on_delete=models.CASCADE, null=True)
	language = models.CharField(max_length=8, choices=TS_annotation_tool.utils.LANGUAGE_CHOICES, help_text=popover_html("In which language(s) is the data?"), blank=True, null=True)
	path = models.CharField(max_length=500, blank=True, null=True)
	simple_level = models.CharField(max_length=50, choices=TS_annotation_tool.utils.language_level_list, help_text=popover_html('On which language level (following CEFR) ist the simple text? E.g., A1 for easy-to-read language, A2 or B1 for plain language.)'))
	complex_level = models.CharField(max_length=50, choices=TS_annotation_tool.utils.language_level_list, help_text=popover_html('On which language level (following CEFR) ist the complex text? E.g., C" for everyday language.)'))
	pre_aligned = models.BooleanField(default=False, help_text=popover_html("Are the documents already sentence-wise aligned?"))
	pre_split = models.BooleanField(default=False, help_text=popover_html("Are the sentences already split?"))
	license_file = models.FileField(blank=True, null=True, help_text=popover_html("If a license file is provided, please upload it."))
	author = models.CharField(max_length=500, blank=True, help_text=popover_html('Who is/are the author(s) of the data? Please provide at least a author name or homepage.'))  # copyright owner
	manually_aligned = 	models.BooleanField(default=False, blank=True, help_text=popover_html("If the texta are already aligned, were they manually or automatically aligned?"))
	to_simplify = models.BooleanField(default=False, null=True, help_text=popover_html("If no simplified version of a text exists so far you can upload the complex version with this option and simplify the texts yourself."))
	professionally_simplified = models.BooleanField(default=False, null=True, help_text=popover_html("Were the texts professionally simplified? For example, by an translation agency or a person trained in simple languages?"))
	continuous_text = models.BooleanField(default=True, null=True, help_text=popover_html("Are the documents continuous or in a random order?"))

	def add_documents_by_upload(self, files, form_upload_data):
		print(form_upload_data)
		find_most_similiar = form_upload_data["find_most_similiar"]
		if files and type(files[0]) == str:
			simple_files = [file for file in files if "simple" in file]
		else:
			simple_files = [file for file in files if "simple" in file.name]
		nlp = get_spacy_model(form_upload_data["language"])
		if len(simple_files) == 0:
			complex_file_obj = [file for file in files if "complex" in file.name]
			for complex_file in complex_file_obj:
				complex_document = Document()
				complex_document, complex_sents_nlp = complex_document.create_or_load_document_by_upload(complex_file,
																					  form_upload_data["language_level_complex"],
																					  form_upload_data["domain"], nlp,
																					  pre_aligned=form_upload_data["pre_aligned"],
																					  selected_license=form_upload_data["license"],
																					  pre_split=form_upload_data["pre_split"],
																					  find_most_similiar=False,
																					  sents_nlp=None)
				document_pair_tmp = DocumentPair(corpus=self)
				document_pair_tmp.complex_document = complex_document
				document_pair_tmp.save()
				document_pair_tmp.annotator.add(*form_upload_data["annotator"])
				document_pair_tmp.save()
				self.document_pair = document_pair_tmp
			self.complex_level = form_upload_data["language_level_complex"]
		else:
			print(simple_files)
			for file in simple_files:
				file_name, file_ending = file.name.split(".")
				file_id = file_name.split("_")[-1]
				simple_document = Document()
				simple_document = simple_document.create_or_load_document_by_upload(document=file,
																					language_level=form_upload_data["language_level_simple"],
																					domain=form_upload_data["domain"], nlp=nlp,
																					pre_aligned=form_upload_data["pre_aligned"],
																					selected_license=form_upload_data["license"],
																					pre_split=form_upload_data["pre_split"],
																					find_most_similiar=False,
																					sents_nlp=None)
				complex_file_obj = [file for file in files if "complex" in file.name and "_" + file_id + "." in file.name]
				if complex_file_obj:
					complex_document = Document()
					simple_sents = simple_document.sentences.all()
					complex_document, complex_sents_nlp = complex_document.create_or_load_document_by_upload(complex_file_obj[0],
																						  form_upload_data["language_level_complex"],
																						  form_upload_data["domain"],
																						  nlp,
																						  pre_aligned=form_upload_data["pre_aligned"],
																						  selected_license=form_upload_data["license"],
																						  pre_split=form_upload_data["pre_split"],
																						  find_most_similiar=find_most_similiar,
																						  sents_nlp=simple_sents)
					document_pair_tmp = DocumentPair(corpus=self)
					document_pair_tmp.complex_document = complex_document
					document_pair_tmp.simple_document = simple_document
					document_pair_tmp.save()
					document_pair_tmp.annotator.add(*form_upload_data["annotator"])
					if form_upload_data["pre_aligned"]:
						document_pair_tmp.add_aligned_sentences(nlp=nlp, manually_aligned=form_upload_data["manually_aligned"],
																language_level_simple=form_upload_data["language_level_simple"],
																language_level_complex=form_upload_data["language_level_complex"],
																annotators=form_upload_data["annotator"])
					document_pair_tmp.save()
					self.document_pair = document_pair_tmp
			self.complex_level = form_upload_data["language_level_complex"]
			self.simple_level = form_upload_data["language_level_simple"]
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
	manually_simplified = models.BooleanField(default=False)

	def add_sentences(self, sentences, par_nr, language_level, selected_license, number_sentences=1, tokenize=True, author=None, sent_ids=None, find_most_similiar=False, sents_nlp=None):
		treshold = 1
		sentence_ids = list()
		if selected_license in TS_annotation_tool.utils.license_limits.keys():
			treshold = TS_annotation_tool.utils.license_limits[selected_license]["save_use"]
		for i, sent in enumerate(sentences):
			if not sent:
				continue
			# print(sent, (i+1)/number_sentences)
			if (i+1)/number_sentences > treshold:
				break
			sent_tmp = Sentence(original_content=sent, level=language_level, document=self, sentence_nr=i, paragraph_nr=par_nr)
			if sent_ids:
				sent_tmp.given_id = sent_ids[i]
			sent_tmp.save()
			if author:
				sent_tmp.author.add(author)
			sent_tmp.save()
			sentence_ids.append(sent_tmp.id)
			if tokenize:
				sent_tmp.tokenize(sent)
			if find_most_similiar and sents_nlp:
				similarities = sorted([(sent.similarity(other_sent), other_sent) for other_sent in sents_nlp], key=itemgetter(0), reverse=True)
				top_5 = [sent for score, sent in similarities if score >= 0.8][:5]
				sent_tmp.most_similar_sent.add(*top_5)
				sent_tmp.save()
		return sentence_ids

	def create_or_load_document_by_upload(self, document, language_level, domain, nlp, selected_license, pre_aligned=False, pre_split=False, find_most_similiar=False, sents_nlp=None): # , add_par_nr=False):
		document_content = document.readlines()
		try:
			copyright_line, title = document_content[0].decode("utf-8").strip().split("\t")
		except AttributeError:
			copyright_line, title = document_content[0].strip().split("\t")
		copyright_line = copyright_line.split(" ")
		date = copyright_line[-1][:-1]
		url = copyright_line[3]
		# title = url.split("/")[-1]
		# todo check document only in current corpus
		if Document.objects.filter(title=title, url=url, level=language_level):
			document_tmp = Document.objects.get(title=title, url=url, level=language_level)
		else:
			if pre_aligned or pre_split:
				plain_data = ""
				for data in document_content[1:]:
					try:
						plain_data += data.decode("utf-8")
					except AttributeError:
						plain_data += data
				document_tmp = Document(url=url, title=title, access_date=date,
										plain_data=plain_data.strip(), level=language_level, domain=domain)
			else:
				try:
					plain_data = document_content[1].decode("utf-8")
				except AttributeError:
					plain_data = document_content[1]
				document_tmp = Document(url=url, title=title, access_date=date, plain_data=plain_data,
										level=language_level, domain=domain)
			document_tmp.save()
			if pre_split:
				for data in document_content[1:]:
					try:
						text = data.strip().decode("utf-8")
					except AttributeError:
						text = data.strip()
					if data.startswith(b"##") and data.endswith(b"##\n"):
						number_sentences = 1
						document_tmp.add_sentences([text], -1, language_level, selected_license, number_sentences, tokenize=False)
					elif re.match(r"^O\w{2}\.\d+\.\d+\.\d+\.\d+", text):
						sent_id, sent = text.split("\t")
						number_sentences = 1
						document_tmp.add_sentences([sent], -1, language_level, selected_license, number_sentences,
												   tokenize=False, sent_ids=[sent_id])
					else:

						number_sentences = len([sent for sent in nlp(text).sents])
						for i_par, par in enumerate(text.split("SEPL|||SEPR")):
							sentences_of_par = nlp(par).sents
							document_tmp.add_sentences(sentences_of_par, i_par, language_level, selected_license, number_sentences, find_most_similiar, sents_nlp)
					document_tmp.save()
			elif not pre_aligned:
				try:
					text = document_content[1].strip().decode("utf-8")
				except:
					text = document_content[1].strip()
				number_sentences = len([sent for sent in nlp(text).sents])
				for i_par, par in enumerate(text.split("SEPL|||SEPR")):
					sentences_of_par = nlp(par).sents
					document_tmp.add_sentences(sentences_of_par, i_par, language_level, selected_license, number_sentences, find_most_similiar, sents_nlp)
			document_tmp.save()
		return document_tmp

	def __str__(self):
		if self.title:
			return self.title
		else:
			return "Document ("+str(+self.id)+")"


class DocumentPair(models.Model):
	simple_document = models.ForeignKey(Document, blank=True, related_name="simple_document", on_delete=models.CASCADE, null=True)
	complex_document = models.ForeignKey(Document, blank=True, related_name="complex_document", on_delete=models.CASCADE, null=True)
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

	def add_aligned_sentences(self, nlp, language_level_simple, language_level_complex, manually_aligned, annotators):
		# todo: not sure if make sense to use add_sentences here
		simple_doc = self.simple_document
		complex_doc = self.complex_document
		simple_sentences = simple_doc.plain_data.split("\n")
		complex_sentences = complex_doc.plain_data.split("\n")
		# print(simple_sentences, complex_sentences)
		for simple_sent, complex_sent in zip(simple_sentences, complex_sentences):
			simple_elements_ids = simple_doc.add_sentences(nlp(simple_sent).sents, -1, language_level_simple, "")
			complex_elements_ids = complex_doc.add_sentences(nlp(complex_sent).sents, -1, language_level_complex, "")
			simple_elements = Sentence.objects.filter(id__in=simple_elements_ids)
			complex_elements = Sentence.objects.filter(id__in=complex_elements_ids)
			if simple_sent != complex_sent:
				sentence_pair_tmp = Pair()
				# user, created = User.objects.get_or_create(username="tool")
				# todo change name to add aligned setence pairs here
				sentence_pair_tmp.save_sentence_alignment_from_form(simple_elements, complex_elements, annotators, self,
																	json.dumps(datetime.datetime.now(), cls=DjangoJSONEncoder),
																	manually_aligned=manually_aligned)
				sentence_pair_tmp.save()
			# else:
			# 	print(simple_sent, "!!!", complex_sent)
		return self

	def add_similarity(self, nlp):
		if nlp.meta["vectors"]["keys"] < 0:
			assert Exception("Your SpaCy model ({}) does not support similarity measurement, please load another model.".format(nlp.meta["name"]))
			return 0
		simple_sents = self.simple_document.sentences.all()
		for complex_sent in self.complex_document.sentences.all():
			complex_sent_nlp = nlp(complex_sent.original_content)
			similarities = sorted([(complex_sent_nlp.similarity(nlp(other_sent.original_content)), other_sent) for other_sent in simple_sents], key=itemgetter(0), reverse=True)
			top_5 = [sent for score, sent in similarities if score >= 0.8][:5]
			complex_sent.most_similar_sent.add(*top_5)
			complex_sent.save()
		return 1




class Sentence(models.Model):
	original_content = models.TextField()
	original_content_repaired = models.TextField()
	corrected_content = models.TextField(blank=True)
	translation = models.TextField(blank=True)
	level = models.CharField(max_length=50, blank=True, choices=TS_annotation_tool.utils.language_level_list)
	simplification = models.ForeignKey("simplification.Simplification", blank=True, on_delete=models.CASCADE, null=True)
	document = models.ForeignKey("data.Document", on_delete=models.CASCADE, blank=True, related_name="sentences")
	simple_element = models.ManyToManyField("alignment.Pair", related_name="simple_elements", blank=True)
	complex_element = models.ManyToManyField("alignment.Pair", related_name="complex_elements", blank=True)
	malformed = models.BooleanField(default=False)
	malformed_comment = models.TextField(blank=True, max_length=250)
	author = models.ManyToManyField(User, blank=True)
	sentence_nr =  models.IntegerField(blank=True, default=-1)
	paragraph_nr =  models.IntegerField(blank=True, default=-1)
	given_id = models.CharField(blank=True, default="", max_length=20)
	most_similar_sent = models.ManyToManyField("self", default=None, blank=True)

	def tokenize(self, doc):
		for token in doc:
			token_tmp = Token(text=token.text, lemma=token.lemma_, tag=token.tag_, sentence=self)
			token_tmp.save()
		self.save()

	def __str__(self):
		return self.original_content + " ("+str(self.paragraph_nr)+"-"+str(self.sentence_nr)+")"


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


# def get_spacy_models(languages):
# 	if len(languages) >= 2:
# 		list_models = list()
# 		for lang in languages:
# 			list_models.append(get_spacy_model(lang))
# 		return list_models
# 	else:
# 		return get_spacy_model(languages[0])


def get_spacy_model(language):
	# # stanza.download(language)
	# snlp = stanza.Pipeline(lang=language)
	# nlp = StanzaLanguage(snlp)
	from spacy.cli import download
	version = spacy.about.__version__
	r = requests.get(spacy.about.__compatibility__)
	comp_table = r.json()
	comp = comp_table["spacy"]
	nlp = None
	for model_ending in ["core_news_lg", "core_web_lg", "dep_news_trf", "core_news_trf",   "core_news_sm", "xx_ent_wiki_sm", "xx_sent_ud_sm"]:
		if model_ending.startswith("xx"):
			model_name = model_ending
		else:
			model_name = language + "_" + model_ending
		if version in comp and model_name in comp[version]:
			try:
				return spacy.load(model_name)
			except OSError:
				download(model_name)
				return spacy.load(model_name)
	return nlp
