# ToDo
- compare other rating forms with the one ASSET. So far ASSET's version is implemented using a continuous scale from 0 to 100
- add different translations https://docs.djangoproject.com/en/3.1/topics/i18n/translation/
- time used for rating and alignment, fields in model already created (created_at, updates_at, finished_at, duration)
- http://127.0.0.1:8000/alignment/change_alignment/21 "'Pair' object has no attribute 'alignments'" -> solved?
- all sentences assigned to each doc?
- name changes or transactions during alignment. Use a list of options with multiple selection and provide an text field for adding a new transaction. Describe ach transaction with examples in the annotattion guideline and link to the document in the annotation tool.
- during alignment show rating form on popup?
- read csv or json file for human rating (incl. description and scale) and transformations. add automatically to models
- disable sentences which  occur without any change in both variants. 
- mark changes in two different sentences if aligned.
- show metadata as URL during the annotation process.
- insert copied texts (without webscraping) and do sentence splitting?

## Texts
### verwenden und veröffentlichen
- alumniportal-DE
- spass_am_lesen_easyytoread_books
### verwenden 
- kurier.at
- recht_leicht
### link + satznummer + erstes wort verwenden
- https://www.os-hho.de/
- https://www.apotheken-umschau.de/einfache-sprache
- https://www.passanten-verlag.de/lesen/
- https://www.bpb.de/system/files/dokument_pdf/barrierefrei_einfach_politik_grundgesetz_grundrechte_2020.pdf
- https://science.apa.at/site/home/kooperation.html?marsname=/Lines/Science/Koop/topeasy 
- https://text.orf.at/channel/orf1/page/480/1.html
- https://www.einfache-sprache.com/uploads/1/1/8/5/11853840/bremer_stadtmusikanten_auflage_1_leseprobe.pdf
- https://ebookcentral.proquest.com/lib/ulbd/detail.action?docID=6384137
- https://www.bzfe.de/einfache-sprache/
### no parallel version
- SR	https://www.sr.de/sr/home/nachrichten/nachrichten_einfach/index.html
- nachrichten_leicht	https://www.nachrichtenleicht.de/
- bpb_lexicon	https://www.bpb.de/nachschlagen/lexika/lexikon-in-einfacher-sprache/
- sachen_anhalt_minister	https://stk.sachsen-anhalt.de/service/infos-in-einfacher-sprache/
- bibentries_LS	http://vzopc4.gbv.de:8080/DB=22/CMD?ACT=SRCHA&IKT=5040&SRT=YOP&TRM=Leichte+Sprache
- bundeszentrum_ernaehrung	https://www.bzfe.de/einfache-sprache-34645.htm
- wege_aus_der_gewalt	https://www.wege-aus-der-gewalt.de/
- ohrenkuss	https://ohrenkuss.de
- ninhil_kraftwerk	https://www.ninlil.at/kraftwerk/index.html
- at_sozialministerium	https://sozialministeriumservice.at/Startseite/Leichter_Lesen/Leichter_Lesen.LL.html
- federal_ministry_inner	https://www.bmi.bund.de/DE/service/leichte-sprache/leichtesprache-node.html
- barrierefreie kommunikation	http://www.barrierefreie-kommunikation.at/einfach/blog/
- Na und ob Buchverlag	https://www.naundob.de/
- Stadt Dortmunf	https://www.dortmund.de/de/index.html
- Landtag Hessen	https://hessischer-landtag.de/content/leichte-sprache
- Herford entdecken Stadtführer in Einfacher Sprache	https://www.herford.de/PDF/StadtHF_Stadtf%C3%BChrer_einfache_Sprache.PDF?ObjSvrID=2593&ObjID=12135&ObjLa=1&Ext=PDF&WTR=1&_ts=1575368108


## Install
### Dependencies
- python3
- requirements.txt `pip3 install -r requirements.txt`


## Structure
The django project has different apps:
- TS_annotation_tool: global directory for all apps
- alignment: aligning the documents
- rating: rating the alignment pairs
- evaluation: for admin only to export data and generate inter-annotator-agreement
