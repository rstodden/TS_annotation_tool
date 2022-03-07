from django import template
from django.shortcuts import get_object_or_404

import alignment.models
import data.models

register = template.Library()

@register.simple_tag
def nested_get(dct, key1, key2):
	return dct.get(int(key1), {}).get(key2)

@register.filter
def get_dict_value(dictionary, key):
    """Removes all values of arg from the given string"""
    return dictionary[key]

@register.filter
def get_value_in_qs(queryset, key):
	return queryset.values_list(key, flat=True)

@register.simple_tag()
def check_aligned(sentence, user):
	sentence_tmp = get_object_or_404(data.models.Sentence, id=sentence.id)
	if sentence_tmp.simple_element.filter(annotator=user).exists():
		return sentence_tmp.simple_element.get(annotator=user).id
		# sentence_tmp.simple_element.filter(annotator=user) or sentence_tmp.complex_element.filter(annotator=user):
	elif sentence_tmp.complex_element.filter(annotator=user).exists():
		return sentence_tmp.complex_element.get(annotator=user).id
	return None
