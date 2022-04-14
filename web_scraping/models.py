import json

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
import datetime

import os, re, csv, requests, codecs
from pathlib import Path
import bs4
import urllib.request
from datetime import datetime
import pandas as pd
import data.models


class AppURLopener(urllib.request.FancyURLopener):
	version = "Mozilla/5.0"


class URL(models.Model):
	url = models.TextField(blank=True)


opener = AppURLopener()


class Crawler(models.Model):
	html = models.TextField(blank=True)
	extracted_data = models.TextField(blank=True)
	# pdf = models.TextField(max_length=1000, blank=True)
	overview_page_url = models.TextField(max_length=1000, blank=True)
	urls = models.URLField(URL)

	def crawl_data_to_db(self, corpora_file):
		# with open(corpora_file) as f:
		corpora_dict = json.load(corpora_file)
		for corpus in corpora_dict["corpora"].keys():
			print(corpus, corpora_dict)
			result = self.crawl_corpus(corpus, corpora_dict["corpora"][corpus])

	def crawl_corpus(self, corpus_name, corpus_dict):
		overview_frame = self.parse_and_extract_webpage(corpus_name, corpus_dict["page_overview"], corpus_dict["output_dir"], corpus_dict["save_raw_content"])
		# overview_frame = pd.read_csv("data_collection/url_overview_"+corpus_name+"_par.tsv", header=0, sep="\t")
		print(corpus_dict)
		annotator_queryset = User.objects.filter(username__in=corpus_dict["annotator"])  # .values_list("id", flat=True)
		corpus_dict["annotator"] = annotator_queryset
		if len(overview_frame) > 0:
			overview_frame_repaired = overview_frame[overview_frame[["complex_location_txt_par", "simple_location_txt_par"]].notnull().all(axis=1)]
			files_list = overview_frame_repaired["complex_location_txt_par"].to_list()+overview_frame_repaired["simple_location_txt_par"].to_list()

			files_obj_list = list()
			for file in files_list:
				file_obj = UploadedFile(file=open(file), name=file, content_type="text/plain", charset="utf-8")
				files_obj_list.append(file_obj)
			if data.models.Corpus.objects.filter(name=corpus_name, home_page=corpus_dict["home_page"]):
				corpus_tmp = data.models.Corpus.objects.get(name=corpus_name, home_page=corpus_dict["home_page"])
				print("corpus found")
				corpus_tmp.add_documents_by_upload(files_obj_list, corpus_dict)
			else:
				corpus_tmp = data.models.Corpus(name=corpus_name, home_page=corpus_dict["home_page"],
												license=corpus_dict["license"], parallel=corpus_dict["parallel"],
												domain=corpus_dict["domain"],
												language=corpus_dict["language"],
												path="", simple_level=corpus_dict["language_level_simple"],
												complex_level=corpus_dict["language_level_complex"],
												professionally_simplified=corpus_dict["professionally_simplified"],
												pre_aligned=corpus_dict["pre_aligned"], pre_split=corpus_dict["pre_split"],
												license_file=corpus_dict["license_file"], author=corpus_dict["author"],
												manually_aligned=corpus_dict["manually_aligned"], to_simplify=corpus_dict["to_simplify"],
												)
				corpus_tmp.save()
				#for lang in corpus_dict["languages"]:
				#	corpus_tmp.
				corpus_tmp.add_documents_by_upload(files_obj_list, corpus_dict)
			return 1
		else:
			return 0
			
	def parse_and_extract_webpage(self, corpus, page_url, output_dir, save_raw_content=False):
		overview_path = self.parse_overview_pages(corpus, page_url, output_dir, save_raw_content)
		# overview_path = output_dir+"url_overview_"+corpus+".tsv"
		overview_df = pd.read_csv(overview_path, sep="\t", header=0)
		if len(overview_df) > 0:
			output_dataframe = filter_and_extract_data(overview_df)  # , filter_data)
			output_dataframe.to_csv(output_dir + "url_overview_"+corpus+"_par.tsv", header=True, index=False, sep="\t")
			return output_dataframe
		else:
			return None

	def parse_overview_pages(self, corpus, page_url, output_dir, save_raw_content=False):
		if Path(output_dir + "url_overview_"+corpus+".tsv").is_file():
			output = []
		else:
			output = [["website", "simple_url", "complex_url", "simple_level", "complex_level", "simple_location_html",
					   "complex_location_html", "simple_location_txt", "complex_location_txt", "alignment_location",
					   "simple_author", "complex_author", "simple_title", "complex_title", "license", "last_access"]]

		if "inclusion-europe" in page_url:
			if "etr-de-fr" in page_url:
				tag = "inclusion-europe-etr-fr"
			elif "etr-de" in page_url:
				tag = "inclusion-europe-etr-de"
			elif "etr-es" in page_url:
				tag = "inclusion-europe-etr-es"
			else:
				tag = "inclusion-europe-etr-en"
			output.extend(
				parse_overview_inclusion_europe(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "alumniportal-deutschland.org" in page_url:
			tag = "alumniportal-DE-2021"
			output.extend(parse_overview_alumniportal_2021(page_url, tag, save_raw_content=save_raw_content,
														   output_dir=output_dir))
		else:
			tag = "else"
			list_simplified_urls, list_complex_urls = [], []
		print(tag)
		with open(output_dir + "url_overview_"+corpus+".tsv", "a", newline="") as f:
			# "_"+ datetime.today().strftime('%Y-%m-%d-%H:%M') +
			writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerows(output)
		return output_dir + "url_overview_"+corpus+".tsv"


def get_link(link, url):
	if link.startswith(url) or link.startswith("https://"):
		return link
	if link.startswith(url.replace("https", "http")):
		return link
	else:
		return url+link


def parse_overview_inclusion_europe(page_url, tag, save_raw_content=False, output_dir="data/", i=0):
	print(page_url)
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "not mentioned"
	access_date = datetime.today().strftime('%Y-%m-%d')
	with opener.open(page_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	container = soup.find("div", {"class": "site-content-left"})
	all_links = [get_link(div.find("a")["href"], "https://www.inclusion-europe.eu") for div in container.find_all("div", {"class": "title"})]
	if all_links:
		for simple_url in all_links:
			complex_url = get_complex_url_inclusion_europe(simple_url)
			if complex_url:
				if save_raw_content:
					simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag)
				output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
				i += 1

	pagination = soup.find("nav", {"class": "post-pagination"})
	if pagination:
		next_page = pagination.find_all("a")
		if next_page:
			for a in next_page:
				if a.find(lambda tag:tag.name=="span" and "Next" in tag.text):
					output.extend(parse_overview_inclusion_europe(get_link(a["href"], "https://www.inclusion-europe.eu"), tag, save_raw_content=save_raw_content, output_dir=output_dir, i=i))
	return output


def parse_overview_alumniportal_2021(page_url, tag, save_raw_content=False, output_dir="data/"):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2", "B2"
	license_name = "CC BY 4.0"
	access_date = datetime.today().strftime('%Y-%m-%d')
	with opener.open(page_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	# head_listing = soup.find_all("a", href = re.compile("^deutsche-sprache/deutsch-auf-die-schnelle/.+"))
	"https://www.alumniportal-deutschland.org/digitales-lernen/deutsche-sprache/lesetexte/lesetexte-sprachniveau-a1-a2/"
	"https://www.alumniportal-deutschland.org/digitales-lernen/deutsche-sprache/lesetexte/b1-b2/online-deutsch-lernen-uebungen-integration-b/"
	"digitales-lernen/deutsche-sprache/lesetexte/lesetexte-sprachniveau-a1-a2/"
	simple_part = "lesetexte/lesetexte-sprachniveau-a1-a2/"
	complex_part = "lesetexte/b1-b2/"
	head_listing = soup.find_all("a", href=re.compile("^/digitales-lernen/deutsche-sprache/lesetexte/lesetexte-sprachniveau-a1-a2/.+"))
	head_listing_complex = soup.find_all("a", href=re.compile("^/digitales-lernen/deutsche-sprache/lesetexte/b1-b2/.+"))
	i = 0
	head_listing = [get_link(link["href"], "https://www.alumniportal-deutschland.org") for link in head_listing if "online-deutsch-lernen-uebungen-" in link["href"]]
	head_listing_complex = [get_link(link["href"], "https://www.alumniportal-deutschland.org") for link in head_listing_complex if "online-deutsch-lernen-uebungen-" in link["href"]]
	if head_listing:
		for link in head_listing:
			simple_url = link
			complex_url = ""
			complex_candidate = simple_url.replace(simple_part, complex_part)
			if complex_candidate.endswith("-a"):
				complex_candidate = complex_candidate[:-1]+"b"
			elif complex_candidate.endswith("-a1-a2"):
				complex_candidate = complex_candidate[:-5]+"b1-b2"

			if complex_candidate in head_listing_complex:
				complex_url = complex_candidate
			if complex_url and simple_url:
				if save_raw_content:
					simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url,
																								  i, output_dir, tag)
				output.append(
					[tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "",
					 "", simple_author, complex_author, simple_title, complex_title, license_name, access_date])
				i += 1
	return output


def get_complex_url_inclusion_europe(simple_url):
	with opener.open(simple_url) as url:
		soup_simple = bs4.BeautifulSoup(url.read(), "lxml")
	complex_url = soup_simple.find("a", {"class": "vc_general vc_btn3 vc_btn3-size-lg vc_btn3-shape-square vc_btn3-style-custom"})
	if complex_url:
		link = get_link(complex_url["href"], "https://www.inclusion-europe.eu")
		return link
	else:
		return ""


def umlauts_coverter_for_url(link):
	if "ä" in link:
		return link.replace("ä", "%C3%A4")
	if "ü" in link:
		return link.replace("ä", "%C3%BC")
	if "ö" in link:
		return link.replace("ä", "%C3%B6")
	else:
		return link


def save_html(level, output_dir, sub_dir, type, i, link):
	title = ""
	try:
		with opener.open(umlauts_coverter_for_url(link)) as url:
			soup = bs4.BeautifulSoup(url.read(), "lxml")
			comment = bs4.Comment('&copy; Origin: ' + link + " [last accessed: " + datetime.today().strftime('%Y-%m-%d') + "]")
			soup.head.insert(-1, comment)
			title = soup.find("title")
			if title:
				title = title.string
		with open(output_dir + sub_dir + type + "/" + level + str(i) + '.html', "w") as file:
			file.write(str(soup))
	except:  # ValueError or OSError:
		print(link, "not accessible")
		return "", ""
	return output_dir + sub_dir + type + "/" + level + str(i) + '.html', title


def save_pdf(level, output_dir, sub_dir, type, i, link):
	r = requests.get(link, stream=True)

	with open(output_dir + sub_dir + type + "/" + level + str(i) + '.pdf', "wb") as pdf:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				pdf.write(chunk)
	return output_dir + sub_dir + type + "/" + level + str(i) + '.pdf'


def save_content(simple_link, complex_link, i, output_dir, sub_dir):
	sub_dir = sub_dir+"/"
	if not os.path.exists(output_dir+sub_dir):
		os.makedirs(output_dir+sub_dir)
	if not simple_link.endswith("pdf") and not os.path.exists(output_dir+sub_dir+"html/"):
		os.makedirs(output_dir+sub_dir+"html/")
	elif simple_link.endswith("pdf") and not os.path.exists(output_dir+sub_dir+"pdf/"):
		os.makedirs(output_dir+sub_dir+"pdf/")

	simple_location, complex_location, simple_title, complex_title = "", "", "", ""
	if not simple_link.endswith("pdf"):
		simple_location, simple_title = save_html("simple_", output_dir, sub_dir, "html", i, simple_link)
	elif simple_link.endswith("pdf"):
		simple_location = save_pdf("simple_", output_dir, sub_dir, "pdf", i, simple_link)
	if not complex_link.endswith("pdf"):
		complex_location, complex_title = save_html("complex_", output_dir, sub_dir, "html", i, complex_link)
	elif complex_link.endswith("pdf"):
		complex_location = save_pdf("complex_", output_dir, sub_dir, "pdf", i, complex_link)
	return simple_location, complex_location, simple_title, complex_title


def filter_and_extract_data(dataframe, filter=None):
	if filter:
		column, value = filter
		dataframe = dataframe.loc[dataframe[column] == value]

	output_frame = iterate_files(dataframe)
	return output_frame


def html2soup(url):
	#print(url)
	with open(url) as f:
		content = f.read()
	return bs4.BeautifulSoup(content, 'html.parser')


def iterate_files(dataframe):
	output_simple, output_complex = "", ""
	for index, row in dataframe.iterrows():
		saved = False
		if pd.isna(dataframe.loc[index, "complex_location_html"]) or pd.isna(dataframe.loc[index, "simple_location_html"]):
			continue
		simple_soup = html2soup(dataframe.loc[index, "simple_location_html"])
		complex_soup = html2soup(dataframe.loc[index, "complex_location_html"])
		print(dataframe.loc[index, "simple_url"])
		if "inclusion-europe" in dataframe.loc[index, "website"]:
			text_simple = extract_inclusion_europe(simple_soup, "article", "vc_row wpb_row vc_row-fluid etr-version vc_custom_\d+ vc_row-has-fill", "A1", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			# vc_row wpb_row vc_row-fluid vc_custom_\d+ vc_row-has-fill
			text_complex = extract_inclusion_europe(complex_soup, "article", "", "C2", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "alumniportal-DE-2021" in dataframe.loc[index, "website"]:
			text_simple = extract_alumni_portal(simple_soup, "h2", "", "A2", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex = extract_alumni_portal(complex_soup, "h2", "", "B2", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		else:
			text_complex, text_simple = "", ""
			continue

		if not saved:
			dataframe = save_data(dataframe, index, text_complex, text_simple)

	return dataframe


def extract_inclusion_europe(soup, tag, attribute, search_text, level, url, date):
	text = ""
	title = soup.find("title").text
	content = soup.find(tag)
	if content:
		if level == "simple":
			paragraphs = content.find_all("div", {"class": "wpb_text_column"})
		elif level == "complex":
			paragraphs = content.find_all("p")
		else:
			paragraphs = None
		if paragraphs:
			for par in paragraphs:
				if (par.parent and par.parent.has_attr("class") and "textwidget" in par.parent["class"]) or (par.get_text().strip() == ""):
					continue
				text += par.get_text().strip() + " "+"SEPL|||SEPR"
	text = text.replace("\n", " ")
	text = " ".join(text.split())
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	return text


def extract_alumni_portal(soup, tag, attribute, search_text, level, url, date):
	text = ""
	search_text_level = "sprachniveau "+search_text.lower()
	title = soup.find("h1").text
	headline = soup.find(tag, text=lambda x: x and search_text_level in x.lower())
	if headline:
		paragraphs = headline.parent.find_all("p", {"class": ""})
		if paragraphs:
			for i_par, par in enumerate(paragraphs):
				if par.text.strip().startswith("Fragen B2") or par.text.strip().startswith("Frage B2") or \
						par.text.strip().startswith("Fragen A2") or par.text.strip().startswith("Frage A2") or \
						par.text.strip().startswith("Haben Sie die Texte gelesen und verstanden?") or \
						par.text.strip().startswith("Text und Antworten in der Community") or par.text.strip().startswith("Haben Sie den Text gelesen und verstanden?"):
					break
				else:
					text += par.text.strip()+"SEPL|||SEPR"
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	return text


def save_data(dataframe, index, text_complex, text_simple, text_path_complex=None, text_path_simple=None):
	if not dataframe.loc[index, "complex_location_html"] or not dataframe.loc[index, "simple_location_html"]:
		dataframe.drop(index)
	if not text_path_complex and not text_path_simple:
		text_path_complex = dataframe.loc[index, "complex_location_html"].replace("html", "txt_par")
		text_path_simple = dataframe.loc[index, "simple_location_html"].replace("html", "txt_par")
	if not os.path.exists("/".join(text_path_simple.split("/")[:-1])):
		os.makedirs("/".join(text_path_simple.split("/")[:-1]))
	dataframe.loc[index, "simple_location_txt_par"] = text_path_simple
	dataframe.loc[index, "complex_location_txt_par"] = text_path_complex
	with open(text_path_complex, "w", encoding="utf-8") as f:
		f.write(text_complex)
	with open(text_path_simple, "w", encoding="utf-8") as f:
		f.write(text_simple)
	return dataframe


# inclusion_europe_urls = ["https://www.inclusion-europe.eu/de/category/etr-de/",
# 						 "https://www.inclusion-europe.eu/es/category/etr-es/",
# 						 "https://www.inclusion-europe.eu/fr/category/etr-de-fr/",
# 						 "https://www.inclusion-europe.eu/category/etr/"]

