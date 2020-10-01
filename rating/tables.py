# tutorial/tables.py
import django_tables2 as tables
import alignment.models

class PairTable(tables.Table):
	class Meta:
		model = alignment.models.Pair
		template_name = "django_tables2/bootstrap.html"
		fields = ("pair_identifier", "rating", "rating.meaning_preservation", "rating.simplicity",
				  "rating.certainty", "rating.transaction", "domain", "simple_element")
	rating = tables.Column()
	annotator = tables.Column()

	def render_ratings(self, value):
		output = list()
		if value is not None:
			print(value, value.all())
			for rating in value.all():
				output.append(rating.grammaticality)
			return ', '.join(output)
		return '-'

	def render_annotators(self, value):
		output = list()
		print(value)
		if value is not None:
			print(value, value.all())
			for rater in value.all():
				output.append(rater.name)
			return ', '.join(output)
		return '-'

		# """
		#				 <td>ID</td>
		#				 <td>grammaticality</td>
		#				 <td>meaning preservation</td>
		#				 <td>simplicity</td>
		#				 <td>certainty</td>
		#				 <td>transaction</td>
		#				 <td>domain</td>
		#				 <td>simple sentence</td>
		#				 <td>complex sentence</td>
		#				 <td></td>"""