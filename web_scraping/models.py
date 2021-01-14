from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime

import os, re, csv, requests, codecs
from pathlib import Path
import bs4
import urllib.request
from datetime import datetime

class AppURLopener(urllib.request.FancyURLopener):
	version = "Mozilla/5.0"



opener = AppURLopener()

class URL(models.Model):
	url = models.TextField(blank=True)


class Crawler(models.Model):
	html = models.TextField(blank=True)
	extracted_data = models.TextField(blank=True)
	# pdf = models.TextField(max_length=1000, blank=True)
	overview_page_url = models.TextField(max_length=1000, blank=True)
	urls = models.URLField(URL)


	def parse_overview_pages(self, page_url, output_dir, save_raw_content=False):
		if Path(output_dir + "url_overview.tsv").is_file():
			output = []
		else:
			output = [["website", "simple_url", "complex_url", "simple_level", "complex_level", "simple_location_html",
					   "complex_location_html", "simple_location_txt", "complex_location_txt", "alignment_location",
					   "simple_author", "complex_author", "simple_title", "complex_title", "license", "last_access"]]

		if "apotheken-umschau" in page_url:
			tag = "apotheken-umschau"
			output.extend(
				parse_overview_apotheke(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "hamburg.de" in page_url:
			tag = "stadt_hamburg"
			output.extend(
				parse_overview_hamburg(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "taz.de" in page_url:
			tag = "taz"
			output.extend(parse_overview_taz(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "stadt-koeln.de" in page_url:
			tag = "stadt_koeln"
			output.extend(parse_overview_koeln(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "offene-bibel.de" in page_url and "in_Arbeit" in page_url:
			tag = "bible_working_progress"
			output.extend(parse_overview_bible(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "offene-bibel.de" in page_url and "noch_zu_pr%C3%BCfen" in page_url:
			tag = "bible_awaiting_proof"
			output.extend(parse_overview_bible(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "offene-bibel.de" in page_url and "Gepr%C3%BCfte_Leichte_Sprache" in page_url:
			tag = "bible_verified"
			output.extend(parse_overview_bible(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "https://www.evangelium-in-leichter-sprache.de/" in page_url:
			tag = "bible_gospel"
			output.extend(
				parse_overview_gospel(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "einfach-teilhaben.de" in page_url:
			tag = "einfach-teilhaben"
			output.extend(parse_overview_einfach_teilhaben(page_url, tag, save_raw_content=save_raw_content,
														   output_dir=output_dir)[0])
		elif "os-hho.de" in page_url:
			tag = "os-hho"
			output.extend(
				parse_overview_os_hho(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "lebenshilfe-main-taunus" in page_url:
			tag = "lebenshilfe_main_taunus"
			output.extend(parse_overview_lebenshilfe_main_taunus(page_url, tag, save_raw_content=save_raw_content,
																 output_dir=output_dir))
		elif "alumniportal-deutschland.org" in page_url:
			tag = "alumniportal-DE"
			output.extend(
				parse_overview_alumniportal(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
		elif "manual_alignment" in page_url:
			tag = "manual_alignment"
			output.extend(add_manual_aligned_urls(save_raw_content=save_raw_content, output_dir=output_dir))
		else:
			tag = "else"
			list_simplified_urls, list_complex_urls = [], []
		print(tag)
		with open(output_dir + "url_overview.tsv", "a", newline="") as f:
			writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerows(output)
			return 1

def add_manual_aligned_urls(save_raw_content=False, output_dir="data/"):
	output = list()
	output.extend(get_easy_to_read_books("links/books", "easy_to_read_books", "citation required", save_raw_content=save_raw_content, output_dir=output_dir))
	output.extend(get_easy_to_read_books("links/fairytales", "fairytales", "not mentioned", save_raw_content=save_raw_content, output_dir=output_dir))
	output.extend(get_participation_urls("links/participation", save_raw_content=save_raw_content, output_dir=output_dir))
	output.extend(get_party_program("links/party_program", "party_program", "todo", save_raw_content=save_raw_content, output_dir=output_dir))
	return output


def get_easy_to_read_books(link, tag, license_name, save_raw_content=False, output_dir="data/"):
	print(tag)
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title = "", "", "", "", "", "", "", "", "", ""
	access_date = datetime.today().strftime('%Y-%m-%d')
	with open(link + "_complex.txt") as f:
		complex_content = f.readlines()
	with open(link + "_simple.txt") as f:
		simple_content = f.readlines()
	complex_level = "C2"
	i = 0
	for simple_line, complex_line in zip(simple_content, complex_content):
		simple_url, simple_level = simple_line.strip().split("\t")
		title, complex_author, complex_url = complex_line.strip().split("\t")
		if save_raw_content:
			simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag)
		output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
		i += 1
	return output


def get_party_program(link, tag, license_name, save_raw_content=False, output_dir="data/"):
	print(tag)
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title = "", "", "", "", "", "", "", "", "", ""
	access_date = datetime.today().strftime('%Y-%m-%d')
	with open(link + "_complex.txt") as f:
		complex_content = f.readlines()
	with open(link + "_simple.txt") as f:
		simple_content = f.readlines()
	complex_level = "C2"
	i = 0
	for simple_line, complex_line in zip(simple_content, complex_content):
		simple_url, simple_level = simple_line.strip().split("\t")
		complex_url = complex_line.strip().split("\t")[0]
		if save_raw_content:
			simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag)
		output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
		i += 1
	return output


def get_participation_urls(link, save_raw_content=False, output_dir="data/"):
	tag = "participation"
	print(tag)
	output = list()
	i = 0
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title = "", "", "", "", "", "", "", "", "", ""
	access_date = datetime.today().strftime('%Y-%m-%d')
	with open(link + "_complex.txt") as f:
		complex_content = f.readlines()
	with open(link + "_simple.txt") as f:
		simple_content = f.readlines()
	for simple_url, complex_url in zip(simple_content, complex_content):
		if save_raw_content:
			simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag)
		output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, "todo", access_date])
		i += 1
	return output


def get_complex_url_apotheke(soup):
	url_complex = ""
	link_more_info = soup.find("a", {
		"name": ["Wo-bekommen-Sie-noch-mehr-Informationen", "Wo-bekommen-Sie-noch-mehr-Informationen-"]})
	if link_more_info:
		parent = link_more_info.parent.parent
		a_complex = parent.find("a", {"class": "gp3linkclass_internal"}, href=True)
		if a_complex:
			url_complex = a_complex["href"]
	return url_complex


def get_complex_url_hamburg(soup):
	url_complex = ""
	list_a = soup.find_all("a", href=True)
	for link in list_a:
		if link.find("title") and "Alltagssprache" in link.find("title").text:
			url_complex = link["href"]
	return url_complex


def get_complex_url_taz(soup_simple_html):
	complex_urls = soup_simple_html.find_all("a", text=lambda x: x and "schwer" in x)
	if complex_urls:
		complex_url = "https://taz.de/" + complex_urls[0]["href"]
		return complex_url

	complex_p = soup_simple_html.find_all("p")
	for p in complex_p:
		if "Original" in p.text:
			complex_urls = p.find_all("a")
			if complex_urls:
				complex_url = "https://taz.de/" + complex_urls[0]["href"]
				return complex_url
	return ""


def get_complex_url_koeln(soup_simple_hmtl):
	complex_url = soup_simple_hmtl.find("a", text=lambda x: x and ("Diese Seite in Alltags-Sprache lesen" in x or "Diese Seite in  Alltags-Sprache lesen" in x))
	if complex_url:
		return complex_url["href"]
	else:
		return ""

def get_complex_url_einfach_teilhaben(simple_url):
	with opener.open(simple_url) as url:
		soup_complex = bs4.BeautifulSoup(url.read(), "lxml")
	complex_url = soup_complex.find("a", {"class": "seitenumschaltung__tab__alltagssprache"})
	if complex_url:
		link = get_link("".join(complex_url["href"].partition(".html")[:-1]), "https://www.einfach-teilhaben.de/")
		return  link
	else:
		return ""


def get_complex_url(simple_url):
	url_complex = ""
	with opener.open(simple_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	if "apotheken-umschau" in simple_url:
		url_complex = get_complex_url_apotheke(soup)
	elif "hamburg" in simple_url:
		url_complex = get_complex_url_hamburg(soup)
	# print("simple", simple_url, "complex", url_complex)
	return url_complex


def parse_overview_apotheke(overview_url, tag, save_raw_content=False, output_dir="data/"):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2/B1", "C2"
	license_name = "copyright required"
	access_date = datetime.today().strftime('%Y-%m-%d')
	i = 0
	with opener.open(overview_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	all_posts = soup.find_all("div", {"class": "teaser teaser--horizontal teaser--bottom-spacing"})
	for post in all_posts:
		a_element = post.find("a", href=True)
		if a_element["href"] and get_complex_url(a_element["href"]):
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(a_element["href"], get_complex_url(a_element["href"]), i, output_dir, tag)
			output.append([tag, a_element["href"], get_complex_url(a_element["href"]), simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output



def parse_overview_hamburg(overview_url, tag, save_raw_content=False, output_dir="data/"):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "copyright reserved. dpa prohibited"
	access_date = datetime.today().strftime('%Y-%m-%d')
	i = 0
	with opener.open(overview_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	all_posts = soup.find_all("span", {"class": "teaser-headline"})
	for post in all_posts:
		parent = post.parent.parent
		grandparent = post.parent.parent.parent.parent.parent.parent
		link_complex = get_complex_url_hamburg(grandparent)
		if parent["href"] and link_complex:
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(parent["href"], link_complex, i, output_dir, tag)
			output.append([tag, parent["href"], link_complex, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output


def parse_overview_taz(overview_url, tag, save_raw_content=False, output_dir="data/"):
	# in contrast to the urls, the simplified texts are build from one or more pages which makes the alignment more difficult
	output, post_list_simple_all = list(), list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "copyright reserved, ask lizenzen@taz.de"
	access_date = datetime.today().strftime('%Y-%m-%d')
	with opener.open(overview_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	all_urls = soup.find_all("a", href= re.compile("^/Leichte-Sprache"))
	post_list_simple_all.extend(["https://taz.de/" + url["href"] for url in all_urls])
	i = 0
	for simple_url in post_list_simple_all:
		with opener.open(simple_url) as url:
			soup_simple_html = bs4.BeautifulSoup(url.read(), "lxml")
		complex_url = get_complex_url_taz(soup_simple_html)
		if complex_url:
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag)
			output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	# todo: multiple complex texts
	return output


def parse_overview_koeln(overview_url, tag, save_raw_content=False, output_dir="data/"):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "written permit required"
	access_date = datetime.today().strftime('%Y-%m-%d')
	with opener.open(overview_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	all_lists = soup.find_all("ul", {"class": "textteaserliste"})
	i = 0
	for ul in all_lists:
		links_simple = ul.find_all("a")
		for simple_url in links_simple:
			simple_url_full = get_link(simple_url["href"], "https://www.stadt-koeln.de")
			with opener.open(simple_url_full) as url:
				soup_simple_html = bs4.BeautifulSoup(url.read(), "lxml")
			complex_url = get_complex_url_koeln(soup_simple_html)
			if complex_url:
				complex_url = get_link(complex_url, "https://www.stadt-koeln.de")
				if save_raw_content:
					simple_location, complex_location, simple_title, complex_title = save_content(simple_url_full, complex_url, i, output_dir, tag)
				output.append([tag, simple_url_full, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
				i += 1
	return output


def parse_overview_bible(overview_url, tag, lexikon=False, save_raw_content=False, output_dir="data/"):
	output, all_listings, lexikon_links = list(), list(), list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "CC BY-SA 3.0"
	access_date = datetime.today().strftime('%Y-%m-%d')
	with opener.open(overview_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	all_lists = soup.find_all("ul", {"class": ""})
	for ul in all_lists:
		all_listings.extend(ul.find_all("li", {"class": ""}))
	if not lexikon:
		lexikon_links = parse_overview_bible("https://offene-bibel.de/wiki/Kategorie:Lexikon_in_Leichter_Sprache", lexikon=True, tag="lexikon")[0]
	i = 0
	for li in all_listings:
		simple_url = li.find("a")
		if simple_url and simple_url["href"].startswith("/wiki/") and \
				simple_url["href"] != "/wiki/Leichte_Sprache" and \
				simple_url["href"] != "/wiki/Bibel_in_Leichter_Sprache" and \
				simple_url["href"] != "/wiki/Was_ist_die_Bibel_in_Leichter_Sprache%3F" and \
				"https://offene-bibel.de"+simple_url["href"] not in lexikon_links:

			if simple_url["href"].endswith("_in_Leichter_Sprache") or simple_url["href"].endswith("_in_Leichter_Sprache_gepr%C3%BCft"):
				complex_url = simple_url["href"].split("_in_Leichter_Sprache")[0]
				if "," in complex_url:
					complex_url = complex_url.split(",")[0]
				if save_raw_content:
					simple_location, complex_location, simple_title, complex_title = save_content(get_link(simple_url["href"], "https://offene-bibel.de"), get_link(complex_url, "https://offene-bibel.de"), i, output_dir, tag)
				output.append([tag, get_link(simple_url["href"], "https://offene-bibel.de"), get_link(complex_url, "https://offene-bibel.de"), simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
				i += 1
	return output


def parse_overview_gospel(overview_url, tag, save_raw_content=False, output_dir="data/"):

	output, all_listings, all_titles, lexikon_links = list(), list(), list(), list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "CC BY-NC-SA 4.0"
	access_date = datetime.today().strftime('%Y-%m-%d')
	with opener.open(overview_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	next_page = soup.find("a", {"title": "Zur nächsten Seite"})
	i = 0
	while next_page:
		print(next_page["href"])
		container = soup.find("div", {"class": "view-content"})
		listings_one_page = container.find_all("a")
		for listing in listings_one_page:
			simple_url = listing["href"]
			simple_title = listing.text
			if simple_url:
				name, number = simple_title.split(",")[0].split(" ")
				complex_url = "https://offene-bibel.de/wiki/"+name+"_"+number
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(get_link(simple_url, "https://www.evangelium-in-leichter-sprache.de"), get_link(complex_url, "https://offene-bibel.de"), i, output_dir, tag)
			output.append([tag, get_link(simple_url, "https://www.evangelium-in-leichter-sprache.de"), get_link(complex_url, "https://offene-bibel.de"), simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
		with opener.open(get_link(next_page["href"], "https://www.evangelium-in-leichter-sprache.de/")) as url:
			soup = bs4.BeautifulSoup(url.read(), "lxml")
		next_page = soup.find("a", {"title": "Zur nächsten Seite"})
	return output

def check_subpage(url, element, attribute, attribute_value):
	with opener.open(url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	all_lists = soup.find_all(element, {attribute: attribute_value})
	return all_lists


def parse_overview_einfach_teilhaben(overview_page, tag, save_raw_content=False, output_dir="data/", i=0):
	# @todo: consider that subpages can also have content and sublinks, e.g. https://www.einfach-teilhaben.de/DE/LS/Themen/LiebeSexualitaet/Familienplanung/Familienplanung_node.html
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	all_lists = check_subpage(overview_page, "li", "class", "themen__teaser__container")
	simple_level, complex_level = "A1", "C2"
	license_name = "nothing regarding texts mentioned"
	access_date = datetime.today().strftime('%Y-%m-%d')
	# print(all_lists)
	if len(all_lists) > 0:
		for listing in all_lists:
			link = get_link("".join(listing.find("a")["href"].partition(".html")[:-1]), "https://www.einfach-teilhaben.de/")
			print(i,link)
			subpages, i = parse_overview_einfach_teilhaben(link, tag, save_raw_content=save_raw_content, output_dir=output_dir, i=i)
			if type(subpages) == list:
				output.extend(subpages)
			else:
				complex_url = get_complex_url_einfach_teilhaben(subpages)
				if complex_url:
					if save_raw_content:
						simple_location, complex_location, simple_title, complex_title = save_content(subpages, complex_url, i, output_dir, tag)
					output.append([tag, subpages, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
					i += 1
		return output, i
	else:
		return overview_page, i


def get_link(link, url):
	if link.startswith(url):
		return link
	if link.startswith(url.replace("https", "http")):
		return link
	else:
		return url+link


def parse_overview_os_hho(overview_page, tag, save_raw_content=False, output_dir="data/"):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2/B1", "C2"
	license_name = "copyright reserved"
	post_list_simple, post_list_complex = list(), list()
	access_date = datetime.today().strftime('%Y-%m-%d')
	with opener.open(overview_page) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	all_urls = set()
	i = 0
	for url_tag in soup.find_all("a"):
		url = url_tag["href"]
		if not url.endswith(".pdf") and url not in all_urls \
				and	(url.startswith("https://www.os-hho.de") or url.startswith("/")) \
				and not url.endswith("#content") and not url.endswith("#hauptnavigation"):
			all_urls.add(get_link(url, "https://www.os-hho.de"))
			for simple_url in check_subpage(get_link(url, "https://www.os-hho.de"), "a", "title",
												  "Klicken Sie hier, um sich den Text in einfacher Sprache anzeigen zu lassen"):
				if get_link(simple_url["href"], "https://www.os-hho.de") not in post_list_simple:
					post_list_simple.append(get_link(simple_url["href"], "https://www.os-hho.de"))
					if save_raw_content:
						simple_location, complex_location, simple_title, complex_title = save_content(get_link(simple_url["href"], "https://www.os-hho.de"), get_link(url, "https://www.os-hho.de"), i, output_dir, tag)
					output.append([tag, get_link(simple_url["href"], "https://www.os-hho.de"), get_link(url, "https://www.os-hho.de"), simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
					i += 1
	return output


def parse_overview_lebenshilfe_main_taunus(overview_page, tag, save_raw_content=False, output_dir="data/"):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	with opener.open(overview_page) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	div_ul = soup.find("div", {"id": "inhalt_sitemap"})
	all_urls = list({get_link(url.find("a")["href"], "https://www.lebenshilfe-main-taunus.de") for url in div_ul.find_all("li")})
	simple_level, complex_level = "A1", "C2"
	license_name = "permit required"
	access_date = datetime.today().strftime('%Y-%m-%d')
	i = 0
	for complex_url in all_urls:
		try:
			with opener.open(complex_url) as url:
				soup_complex_url = bs4.BeautifulSoup(url.read(), "lxml")
		except UnicodeError:
			continue
		simple_element = soup_complex_url.find("img", title="Auf Leichte Sprache umstellen").parent
		if simple_element.name == "a" and simple_element["href"] != "/ls/" and not re.search(r"/ls/-\d{3}\.html", simple_element["href"]):
			simple_url = get_link(simple_element["href"], "https://www.lebenshilfe-main-taunus.de")
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag)
			output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output


def parse_overview_alumniportal(page_url, tag, save_raw_content=False, output_dir="data/"):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2", "B2"
	license_name = "CC BY 4.0"
	access_date = datetime.today().strftime('%Y-%m-%d')
	with opener.open(page_url) as url:
		soup = bs4.BeautifulSoup(url.read(), "lxml")
	head_listing = soup.find_all("a", href = re.compile("^deutsche-sprache/deutsch-auf-die-schnelle/.+"))
	i = 0
	if head_listing:
		for link in head_listing:
			simple_url, complex_url = get_link(link["href"], "https://www.alumniportal-deutschland.org/"), get_link(link["href"], "https://www.alumniportal-deutschland.org/")
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag)
			output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output


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
	except ValueError:
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