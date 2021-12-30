from django import template
register = template.Library()


@register.filter
def sort_by(queryset, order):
	return queryset.order_by(order)

@register.filter(name='split')
def split(value, key):
	"""
		Returns the value turned into a list.
	"""
	return value.split(key)[0]