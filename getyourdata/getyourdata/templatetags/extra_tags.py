from django import template
from django.utils.translation import get_language

register = template.Library()


@register.filter(name='change_url_lang')
def change_url_lang(value, new_language):
    current_language = get_language()

    return value.replace("%s/" % current_language, "%s/" % new_language)
