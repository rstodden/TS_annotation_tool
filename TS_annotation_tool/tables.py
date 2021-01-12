# tutorial/tables.py

import django_tables2 as tables
import data.models

class OverviewTableCorpus(tables.Table):
	class Meta:
		model = data.models.Corpus
		template_name = "django_tables2/bootstrap.html"
		fields = ("name", "domain", "simple_level", "complex_level", "complex_documents")


class OverviewTableDocument(tables.Table):
	edit = tables.TemplateColumn("""<a class="btn btn-default" href="{% url 'overview_per_doc' record.id %}">Edit</a>""")

	class Meta:
		model = data.models.Document
		template_name = "django_tables2/bootstrap.html"
		fields = ("title", "domain", "level", "last_changes", "alignments", "align")
