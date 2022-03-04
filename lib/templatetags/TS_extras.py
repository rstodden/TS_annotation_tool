from django import template
register = template.Library()

@register.simple_tag
def nested_get(dct, key1, key2):
	return dct.get(int(key1), {}).get(key2)

@register.filter
def get_dict_value(dictionary, key):
    """Removes all values of arg from the given string"""
    return dictionary[key]